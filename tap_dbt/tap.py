"""dbt tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk.typing import (
    ArrayType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

from tap_dbt.streams import (
    AccountsStream,
    AuditLogsStream,
    ConnectionsStream,
    EnvironmentsStream,
    GroupsStream,
    JobsStream,
    ProjectsStream,
    RepositoriesStream,
    RunArtifacts,
    RunsStream,
    UsersStream,
)

TAP_NAME = "tap-dbt"
STREAM_TYPES = [
    AccountsStream,
    AuditLogsStream,
    ConnectionsStream,
    EnvironmentsStream,
    GroupsStream,
    JobsStream,
    ProjectsStream,
    RepositoriesStream,
    RunArtifacts,
    RunsStream,
    UsersStream,
]


class TapDBT(Tap):
    """Singer tap for the dbt Cloud API."""

    name = TAP_NAME

    config_jsonschema = PropertiesList(
        Property(
            "api_key",
            StringType,
            description="API key for the dbt Cloud API",
            required=True,
        ),
        Property(
            "account_ids",
            ArrayType(StringType),
            description="dbt Cloud account IDs",
            required=True,
        ),
        Property(
            "base_url",
            StringType,
            description="Base URL for the dbt Cloud API",
            default="https://cloud.getdbt.com/api/v2",
        ),
        Property(
            "page_size",
            IntegerType,
            default=5000,
            description="Page size to use in limit= url parameter",
            required=True,
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]  # type: ignore[abstract]


cli = TapDBT.cli
