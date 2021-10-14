"""dbt tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk.typing import ArrayType, PropertiesList, Property, StringType

from tap_dbt.streams import AccountsStream, JobsStream, ProjectsStream, RunsStream

TAP_NAME = "tap-dbt"
STREAM_TYPES = [
    AccountsStream,
    JobsStream,
    ProjectsStream,
    RunsStream,
]


class TapDBT(Tap):
    """dbt tap class."""

    name = TAP_NAME

    @property
    def config_jsonschema(self):
        return PropertiesList(
            Property("api_key", StringType, required=True),
            Property("account_ids", ArrayType(StringType), required=True),
            Property("base_url", StringType, default="https://cloud.getdbt.com/api/v2"),
            Property(
                "user_agent",
                StringType,
                default=f"{cls.name}/{cls.plugin_version}",
                description="User-Agent header",
            ),
        ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


cli = TapDBT.cli
