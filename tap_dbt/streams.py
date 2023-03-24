"""Stream class for tap-dbt."""

from __future__ import annotations

import typing as t
from pathlib import Path

from singer_sdk.pagination import BaseOffsetPaginator

from tap_dbt.client import DBTStream

if t.TYPE_CHECKING:
    import requests

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class DbtPaginator(BaseOffsetPaginator):
    """dbt API paginator."""

    def has_more(self, response) -> bool:
        """
        Returns True until there are no more pages to retrieve
        
        The API returns an 'extra' key with information about pagination:
        "extra":{"filters":{"limit":100,"offset":2,"account_id":1},"order_by":"id","pagination":{"count":100,"total_count":209}}} 
        """
        data = response.json()
        extra = data.get("extra")
        filters = extra.get("filters")
        pagination = extra.get("pagination")
        
        offset = filters.get("offset",0)
        total_count = pagination.get("total_count")
        count = pagination.get("count")
        
        """
        The pagination has more records when:
        total_count is still greater than count and offset combined
        """
        return (count + offset < total_count)

class AccountBasedStream(DBTStream):
    """A stream that requires an account ID."""

    @property
    def partitions(self) -> list[dict]:
        """Return a list of partition key dicts (if applicable), otherwise None."""
        if "{account_id}" in self.path:
            return [
                {"account_id": account_id}
                for account_id in t.cast(list, self.config["account_ids"])
            ]

        errmsg = (
            f"Could not detect partition type for dbt stream "
            f"'{self.name}' ({self.path}). "
            "Expected a URL path containing '{account_id}'. "
        )
        raise ValueError(errmsg)
      
    def get_new_paginator(self) -> DbtPaginator:
        """Return a new paginator instance for this stream."""
        return DbtPaginator(start_value=0, page_size=100)

    def get_url_params(self, context: dict, next_page_token: int) -> dict:
        """Return offset as the next page token"""
        params = {}

        # Next page token is an offset
        if next_page_token:
            params["offset"] = next_page_token

        return params


class AccountsStream(DBTStream):
    """A stream for the accounts endpoint."""

    name = "accounts"
    path = "/accounts"
    schema_filepath = SCHEMAS_DIR / "accounts.json"
    records_jsonpath = "$.data"
    openapi_ref = "Account"

class JobsStream(AccountBasedStream):
    """A stream for the jobs endpoint."""

    name = "jobs"
    path = "/accounts/{account_id}/jobs"
    openapi_ref = "Job"

class ProjectsStream(AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "projects"
    path = "/accounts/{account_id}/projects"
    openapi_ref = "Project"


class RunsStream(AccountBasedStream):
    """A stream for the runs endpoint."""

    name = "runs"
    path = "/accounts/{account_id}/runs"
    openapi_ref = "Run"
    page_size = 100
