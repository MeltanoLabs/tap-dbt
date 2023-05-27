"""Stream class for tap-dbt."""

from __future__ import annotations

import typing as t
from typing import cast
import pendulum
from pathlib import Path

from singer_sdk.pagination import BaseOffsetPaginator

from tap_dbt.client import DBTStream

if t.TYPE_CHECKING:
    import requests

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class DbtPaginator(BaseOffsetPaginator):
    """dbt API paginator."""

    def has_more(self, response: requests.Response) -> bool:
        """Returns True until there are no more pages to retrieve.

        The API returns an 'extra' key with information about pagination:
        "extra":{"filters":{"limit":100,"offset":2,"account_id":1},"order_by":"id","pagination":{"count":100,"total_count":209}}}
        """
        data = response.json()
        extra = data.get("extra", {})
        filters = extra.get("filters", {})
        pagination = extra.get("pagination", {})

        offset = filters.get("offset", 0)
        total_count = pagination.get("total_count")
        count = pagination.get("count")

        # The pagination has more records when:
        # total_count is still greater than count and offset combined
        return count + offset < total_count


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
        page_size = self.config["page_size"]

        self.logger.debug(
            "Using page size of %s for the limit URL parameter",
            page_size,
        )

        return DbtPaginator(start_value=0, page_size=page_size)

    def get_url_params(
        self,
        context: dict,
        next_page_token: int,
    ) -> dict:
        """Return offset as the next page token."""
        params = {}
        _ = context
        # TODO(edgarrmondragon): Get page size from the pagination object when
        # it's available in this scope
        # https://github.com/meltano/sdk/issues/1606)
        params["limit"] = self.config["page_size"]

        # Next page token is an offset
        if next_page_token:
            params["offset"] = next_page_token

        self.logger.debug("context=%s", context)
        self.logger.debug("params=%s", params)

        return params

class AccountBasedIncrementalStream(AccountBasedStream):
    """A stream that requires an account ID and is synced incrementally.
    
    Requires a reverse sorted response such that syncing stops once the 
    replication_key value is less than the bookmark
    
    """
    
    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Return a generator of record-type dictionary objects.

        Each record emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        starting_replication_key_value = self.get_starting_timestamp(context)
        if starting_replication_key_value is None:
          for record in self.request_records(context):
              transformed_record = self.post_process(record, context)
              if transformed_record is None:
                  # Record filtered out during post_process()
                  continue
              yield transformed_record

        for record in self.request_records(context):
            transformed_record = self.post_process(record, context)
            if transformed_record is None:
                # Record filtered out during post_process()
                continue
            
            if starting_replication_key_value is None: # FULL_TABLE
                yield transformed_record
                
            else: # INCREMENTAL
                record_last_received_datetime: pendulum.DateTime = cast(
                    pendulum.DateTime,
                    pendulum.parse(record[self.replication_key]),
                )
                # Runs are returned in descending id order, so we can stop
                # There's no filtering parameter just this applied ordering
                if record_last_received_datetime < starting_replication_key_value:
                    self.logger.info(
                        "Breaking after hitting a record with replication key %s < %s",
                        record_last_received_datetime,
                        starting_replication_key_value,
                    )
                    break
                yield transformed_record


class AccountsStream(DBTStream):
    """A stream for the accounts endpoint."""

    name = "accounts"
    path = "/accounts"
    schema_filepath = SCHEMAS_DIR / "accounts.json"
    openapi_ref = "Account"


class ConnectionsStream(AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "connections"
    path = "/accounts/{account_id}/connections"
    openapi_ref = "Connection"
    selected_by_default = False


class EnvironmentsStream(AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "environments"
    path = "/accounts/{account_id}/environments"
    openapi_ref = "Environment"
    selected_by_default = False


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


class RepositoriesStream(AccountBasedStream):
    """A stream for the repositories endpoint."""

    name = "repositories"
    path = "/accounts/{account_id}/repositories"
    openapi_ref = "Repository"
    selected_by_default = False


class RunsStream(AccountBasedIncrementalStream):
    """A stream for the runs endpoint."""

    name = "runs"
    # Reverse the order of the API query for runs only to enable get_records to stop
    # when updated_at value is less than bookmark
    # TODO - only order by reverse ID if INCREMENTAL otherwise do normal
    path = "/accounts/{account_id}/runs/?order_by=-id"
    openapi_ref = "Run"
    replication_key = "updated_at"


class UsersStream(AccountBasedStream):
    """A stream for the users endpoint."""

    name = "users"
    path = "/accounts/{account_id}/users"
    openapi_ref = "User"
    selected_by_default = False
