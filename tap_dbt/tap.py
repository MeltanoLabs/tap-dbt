"""dbt tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk.helpers._classproperty import classproperty
from singer_sdk.typing import (
    ArrayType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

from tap_dbt.streams import (
    AccountsStream,
    ConnectionsStream,
    EnvironmentsStream,
    JobsStream,
    ProjectsStream,
    RepositoriesStream,
    RunsStream,
    UsersStream,
)

TAP_NAME = "tap-dbt"
STREAM_TYPES = [
    AccountsStream,
    ConnectionsStream,
    EnvironmentsStream,
    JobsStream,
    ProjectsStream,
    RepositoriesStream,
    RunsStream,
    UsersStream,
]


class TapDBT(Tap):
    """Singer tap for the dbt Cloud API."""

    name = TAP_NAME

    @classproperty
    def config_jsonschema(cls) -> dict:  # noqa: N805
        """Return JSON schema definition for the config.

        Returns:
            A JSON schema dictionary.
        """
        return PropertiesList(
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
                "user_agent",
                StringType,
                default=f"{cls.name}/{cls.plugin_version} {cls.__doc__}",
                description="User-Agent to make requests with",
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
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


cli = TapDBT.cli
