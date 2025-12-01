"""Stream class for tap-dbt."""

from __future__ import annotations

import datetime
import json
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, cast

from singer_sdk import typing as th
from singer_sdk.pagination import (
    BaseAPIPaginator,
    BaseOffsetPaginator,
    SinglePagePaginator,
)
from typing_extensions import override

from tap_dbt.client import DBTStream

if sys.version_info < (3, 11):
    from backports.datetime_fromisoformat import (  # ty: ignore[unresolved-import]
        MonkeyPatch,
    )

    MonkeyPatch.patch_fromisoformat()

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Context, Record


class _AccountBasedStream(DBTStream):
    """A stream that requires an account ID."""

    @override
    @property
    def partitions(self) -> list[dict]:
        """Return a list of partition key dicts (if applicable), otherwise None."""
        if "{account_id}" in self.path:
            return [
                {"account_id": account_id}
                for account_id in cast("list", self.config["account_ids"])
            ]

        errmsg = (
            f"Could not detect partition type for dbt stream "
            f"'{self.name}' ({self.path}). "
            "Expected a URL path containing '{account_id}'. "
        )
        raise ValueError(errmsg)

    @override
    def get_new_paginator(self) -> BaseOffsetPaginator:
        """Return a new paginator instance for this stream."""
        page_size = self.config["page_size"]

        self.logger.debug(
            "Using page size of %s for the limit URL parameter",
            page_size,
        )

        return BaseOffsetPaginator(start_value=0, page_size=page_size)

    @override
    def get_url_params(  # type: ignore[override]
        self,
        context: Context,
        next_page_token: int | None,
    ) -> dict[str, Any]:
        """Return offset as the next page token."""
        params: dict[str, Any] = {}
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


class AccountBasedIncrementalStream(_AccountBasedStream):
    """Account stream that can be synced incrementally by a datetime field.

    Requires a reverse sorted response such that syncing stops once the
    replication_key value is less than the bookmark

    """

    @override
    def get_url_params(  # type: ignore[override]
        self,
        context: Context,
        next_page_token: int | None,
    ) -> dict[str, Any]:
        """Reverse-sort the list by id if performing INCREMENTAL sync."""
        params = super().get_url_params(context, next_page_token)

        if self.get_starting_timestamp(context):
            # Precede replication key with minus to reverse sort
            params["order_by"] = f"-{self.replication_key}"

        return params

    @override
    def get_records(self, context: Context | None) -> Iterable[Record]:
        starting_replication_key_value = self.get_starting_timestamp(context)

        for record in self.request_records(context):
            transformed_record = self.post_process(record, context)
            if transformed_record is None:
                # Record filtered out during post_process()
                continue

            if (
                starting_replication_key_value is not None
                and record[self.replication_key] is not None
            ):
                record_last_received_datetime = datetime.datetime.fromisoformat(
                    record[self.replication_key],
                )

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
    openapi_ref = "Account"


class ConnectionsStream(_AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "connections"
    path = "/accounts/{account_id}/connections"
    openapi_ref = "Connection"
    selected_by_default = False


class EnvironmentsStream(_AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "environments"
    path = "/accounts/{account_id}/environments"
    openapi_ref = "Environment"
    selected_by_default = False


class JobsStream(_AccountBasedStream):
    """A stream for the jobs endpoint."""

    name = "jobs"
    path = "/accounts/{account_id}/jobs"
    openapi_ref = "Job"


class ProjectsStream(_AccountBasedStream):
    """A stream for the projects endpoint."""

    name = "projects"
    path = "/accounts/{account_id}/projects"
    openapi_ref = "Project"


class RepositoriesStream(_AccountBasedStream):
    """A stream for the repositories endpoint."""

    name = "repositories"
    path = "/accounts/{account_id}/repositories"
    openapi_ref = "Repository"
    selected_by_default = False


class RunsStream(AccountBasedIncrementalStream):
    """A stream for the runs endpoint."""

    name = "runs"
    path = "/accounts/{account_id}/runs"
    openapi_ref = "Run"
    replication_key = "finished_at"
    is_sorted = True

    @override
    def get_child_context(self, record: Record, context: Context | None) -> Context:
        assert context is not None  # noqa: S101

        return {
            **context,
            "run_id": record["id"],
            "artifacts_saved": record["artifacts_saved"],
        }

    @override
    def get_url_params(  # type: ignore[override]
        self,
        context: Context,
        next_page_token: int | None,
    ) -> dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["order_by"] = "finished_at"

        start = self.get_starting_timestamp(context)

        if start:
            # strip utc offset by removing timezone info - dbt Cloud API otherwise
            # returns runs ignoring the range start time component (i.e. date only)
            start = start.replace(tzinfo=None).isoformat()  # type: ignore[assignment]

            end = datetime.datetime.max.replace(tzinfo=None).isoformat()
            params["finished_at__range"] = json.dumps([start, end])

        return params


class UsersStream(_AccountBasedStream):
    """A stream for the users endpoint."""

    name = "users"
    path = "/accounts/{account_id}/users"
    openapi_ref = "User"
    selected_by_default = False


class GroupsStream(_AccountBasedStream):
    """A stream for the groups endpoint."""

    name = "groups"
    path = "/accounts/{account_id}/groups"
    openapi_ref = "GroupResponse"
    api_version = "v3"


class AuditLogsStream(_AccountBasedStream):
    """A stream for the audit-logs endpoint."""

    name = "audit_logs"
    path = "/accounts/{account_id}/audit-logs"
    openapi_ref = "PublicAuditLogResponse"
    api_version = "v3"

    @override
    def validate_response(self, response: requests.Response) -> None:
        if response.status_code == HTTPStatus.BAD_REQUEST:
            reason = response.json()["data"]["reason"]
            if reason == "Audit logs are not enabled on this account":
                self.logger.warning(reason)
                return None
        return super().validate_response(response)

    @override
    def parse_response(self, response: requests.Response) -> Iterable[Record]:
        if response.status_code == HTTPStatus.BAD_REQUEST:
            return []
        return super().parse_response(response)


class RunArtifacts(_AccountBasedStream):
    """A stream for the run_artifacts endpoint."""

    name = "run_artifacts"
    path = "/accounts/{account_id}/runs/{run_id}/artifacts"
    openapi_ref = None  # type: ignore[assignment]
    schema = th.PropertiesList(
        th.Property("account_id", th.StringType),
        th.Property("run_id", th.IntegerType),
        th.Property("path", th.StringType),
    ).to_dict()

    primary_keys = ("account_id", "run_id", "path")  # type: ignore[assignment]

    parent_stream_type = RunsStream
    state_partitioning_keys = ()  # type: ignore[assignment]

    @override
    def get_records(self, context: Context | None) -> Iterable[Record]:
        assert context is not None  # noqa: S101

        if context["artifacts_saved"]:
            return super().get_records(context)
        return []

    @override
    def parse_response(self, response: requests.Response) -> Iterable[Record]:
        yield from ({"path": path} for path in super().parse_response(response))

    @override
    def get_new_paginator(self) -> BaseAPIPaginator:  # type: ignore[override]
        return SinglePagePaginator()

    @override
    def post_process(
        self,
        row: Record,
        context: Context | None = None,
    ) -> Record | None:
        assert context is not None  # noqa: S101

        row["account_id"] = context["account_id"]
        row["run_id"] = context["run_id"]
        return row
