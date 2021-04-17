"""dbt tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk.typing import ArrayType, PropertiesList, Property, StringType

from tap_dbt.streams import AccountsStream, JobsStream, ProjectsStream, RunsStream

STREAM_TYPES = [
    AccountsStream,
    JobsStream,
    ProjectsStream,
    RunsStream,
]


class TapDBT(Tap):
    """dbt tap class."""

    name = "tap-dbt"

    config_jsonschema = PropertiesList(
        Property("api_key", StringType, required=True),
        Property("account_ids", ArrayType(StringType), required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


cli = TapDBT.cli
