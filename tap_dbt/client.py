"""Base class for connecting to th dbt Cloud API."""

from __future__ import annotations

import importlib.resources
import typing as t
from abc import abstractmethod
from functools import cache, cached_property

import yaml
from singer_sdk import RESTStream
from singer_sdk.authenticators import APIAuthenticatorBase, SimpleAuthenticator
from singer_sdk.helpers._typing import append_type
from singer_sdk.singerlib import resolve_schema_references

from tap_dbt import schemas


@cache
def load_openapi(api_version: str) -> dict[str, t.Any]:
    """Load the OpenAPI specification from the package.

    Returns:
        The OpenAPI specification as a dict.
    """
    openapi_spec = f"openapi_{api_version}.yaml"
    schema_path = importlib.resources.files(schemas) / openapi_spec
    with schema_path.open() as schema:
        return yaml.safe_load(schema)


class DBTStream(RESTStream):
    """dbt stream class."""

    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.data[*]"
    api_version = "v2"

    @property
    def url_base(self) -> str:
        """Base URL for this stream."""
        base_url: str = self.config["base_url"]
        return f"{(base_url.rsplit('/', 1))[0]}/{self.api_version}"

    @property
    def http_headers(self) -> dict:
        """HTTP headers for this stream."""
        headers = super().http_headers
        headers["Accept"] = "application/json"
        return headers

    @property
    def authenticator(self) -> APIAuthenticatorBase:
        """Return the authenticator for this stream."""
        return SimpleAuthenticator(
            stream=self,
            auth_headers={
                "Authorization": f"Token {self.config.get('api_key')}",
            },
        )

    def _resolve_openapi_ref(self) -> dict[str, t.Any]:
        schema = {"$ref": f"#/components/schemas/{self.openapi_ref}"}
        openapi = load_openapi(self.api_version)
        schema["components"] = openapi["components"]
        return resolve_schema_references(schema)

    @cached_property
    def schema(self) -> dict[str, t.Any]:
        """Return the schema for this stream.

        Returns:
            The schema for this stream.
        """
        openapi_response = self._resolve_openapi_ref()

        def append_null_nested(schema: dict) -> dict:
            new_schema = schema.copy()

            if "type" in schema and schema.get("nullable", True):
                new_schema["type"] = append_type(schema, "null")["type"]

            if "properties" in schema:
                new_schema["properties"] = {}
                for p_name, p_schema in schema["properties"].items():
                    if p_name not in self.primary_keys:
                        new_schema["properties"][p_name] = append_null_nested(p_schema)
                    else:
                        new_schema["properties"][p_name] = p_schema

            if "items" in schema:
                new_schema["items"] = append_null_nested(schema["items"])

            return new_schema

        return append_null_nested(openapi_response)

    @property
    @abstractmethod
    def openapi_ref(self) -> str:
        """Return the OpenAPI component name for this stream.

        Returns:
            The OpenAPI reference for this stream.
        """
        ...
