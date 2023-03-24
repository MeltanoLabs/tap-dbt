"""Stream class for tap-dbt."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, cast

import requests
from singer_sdk.authenticators import APIAuthenticatorBase, SimpleAuthenticator
from singer_sdk.streams import RESTStream
from singer_sdk.pagination import BaseOffsetPaginator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class DBTPaginator(BaseOffsetPaginator):
    """
    The API returns a 
    "extra":{"filters":{"limit":100,"offset":2,"account_id":1},"order_by":"id","pagination":{"count":100,"total_count":209}}}
    """
    def has_more(self, response):
        data = response.json()
        extra = data.get("extra")
        filters = extra.get("filters")
        pagination = extra.get("pagination")
        
        limit = filters.get("limit")
        offset = filters.get("offset",0)
        total_count = pagination.get("total_count")
        count = pagination.get("count")
        
        return (count + offset < total_count)

class DBTStream(RESTStream):
    """dbt stream class."""

    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.data[*]"

    @property
    def url_base(self):
        return self.config.get("base_url", "https://cloud.getdbt.com/api/v2")

    @property
    def http_headers(self) -> dict:
        headers = super().http_headers
        headers["Accept"] = "application/json"
        return headers

    @property
    def authenticator(self) -> APIAuthenticatorBase:
        return SimpleAuthenticator(
            stream=self,
            auth_headers={
                "Authorization": f"Token {self.config.get('api_key')}",
            },
        )
        
    def get_new_paginator(self):
        return DBTPaginator(start_value=0, page_size=100)

    def get_url_params(self, context, next_page_token):
        params = {}

        # Next page token is an offset
        if next_page_token:
            params["offset"] = next_page_token

        return params

class AccountsStream(DBTStream):
    name = "accounts"
    path = "/accounts"
    schema_filepath = SCHEMAS_DIR / "accounts.json"

class AccountBasedStream(DBTStream):
    @property
    def partitions(self) -> List[dict]:
        """Return a list of partition key dicts (if applicable), otherwise None."""

        if "{account_id}" in self.path:
            return [{"account_id": id} for id in cast(list, self.config["account_ids"])]
        raise ValueError(
            "Could not detect partition type for dbt stream "
            f"'{self.name}' ({self.path}). "
            "Expected a URL path containing '{account_id}'. "
        )

class JobsStream(AccountBasedStream):
    name = "jobs"
    path = "/accounts/{account_id}/jobs"
    schema_filepath = SCHEMAS_DIR / "jobs.json"

class ProjectsStream(AccountBasedStream):
    name = "projects"
    path = "/accounts/{account_id}/projects"
    schema_filepath = SCHEMAS_DIR / "projects.json"

class RunsStream(AccountBasedStream):
    name = "runs"
    path = "/accounts/{account_id}/runs"
    schema_filepath = SCHEMAS_DIR / "runs.json"
