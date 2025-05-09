"""Base class for connecting to th dbt Cloud API."""

from __future__ import annotations

import importlib.resources
import typing as t
from abc import abstractmethod
from functools import cache, cached_property

import yaml
from singer_sdk import RESTStream
from singer_sdk.authenticators import APIAuthenticatorBase, SimpleAuthenticator
from singer_sdk.singerlib import resolve_schema_references

from tap_dbt import schemas


@cache
def load_openapi() -> dict[str, t.Any]:
    """Load the OpenAPI specification from the package.

    Returns:
        The OpenAPI specification as a dict.
    """
    schema_path = importlib.resources.files(schemas) / "openapi_v2.yaml"
    with schema_path.open() as schema:
        return yaml.safe_load(schema)


class DBTStream(RESTStream):
    """dbt stream class."""

    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.data[*]"

    @property
    def url_base(self) -> str:
        """Base URL for this stream."""
        return self.config.get("base_url", "https://cloud.getdbt.com/api/v2")

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
        openapi = load_openapi()
        schema["components"] = openapi["components"]
        return resolve_schema_references(schema)

    @cached_property
    def schema(self) -> dict[str, t.Any]:
        """Return the schema for this stream.

        Returns:
            The schema for this stream.
        """
        openapi_response = self._resolve_openapi_ref()

        for property_schema in openapi_response["properties"].values():
            if property_schema.get("nullable"):
                if isinstance(property_schema["type"], list):
                    property_schema["type"].append("null")
                else:
                    property_schema["type"] = [property_schema["type"], "null"]

        return openapi_response

    @property
    @abstractmethod
    def openapi_ref(self) -> str:
        """Return the OpenAPI component name for this stream.

        Returns:
            The OpenAPI reference for this stream.
        """
        ...
