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

    def get_next(self, response: requests.Response) -> int | None:
        """Return the next page number, or None if there are no more pages.

        Args:
            response: The response object from the previous request.

        Returns:
            The next page number, or None if there are no more pages.
        """
        data = response.json()

        if len(data["data"]):
            return self._value + self._page_size

        return None


class PaginationMixin:
    """A mixin for streams that use the dbt API pagination mechanism."""

    def get_new_paginator(self) -> DbtPaginator:
        """Return a new paginator instance for this stream."""
        return DbtPaginator(start_value=0, page_size=100)


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


class AccountsStream(AccountBasedStream):
    """A stream for the accounts endpoint."""

    name = "accounts"
    path = "/accounts/{account_id}"
    schema_filepath = SCHEMAS_DIR / "accounts.json"
    records_jsonpath = "$.data"
    openapi_ref = "Account"


class JobsStream(AccountBasedStream, PaginationMixin):
    """A stream for the jobs endpoint."""

    name = "jobs"
    path = "/accounts/{account_id}/jobs"
    openapi_ref = "Job"

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: int,  # noqa: ARG002
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream context.
            next_page_token: The next page token.

        Returns:
            A dictionary of values to be used as URL query parameters.
        """
        return {"order_by": "updated_at"}


class ProjectsStream(AccountBasedStream, PaginationMixin):
    """A stream for the projects endpoint."""

    name = "projects"
    path = "/accounts/{account_id}/projects"
    openapi_ref = "Project"


class RunsStream(AccountBasedStream, PaginationMixin):
    """A stream for the runs endpoint."""

    name = "runs"
    path = "/accounts/{account_id}/runs"
    openapi_ref = "Run"
    page_size = 100

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: int,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        return {
            "order_by": "updated_at",
            "limit": self.page_size,
            "offset": next_page_token,
        }
