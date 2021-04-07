"""Stream class for tap-dbt."""

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests
from singer_sdk.authenticators import APIAuthenticatorBase, SimpleAuthenticator
from singer_sdk.streams import RESTStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class DBTStream(RESTStream):
    """dbt stream class."""

    url_base = "https://cloud.getdbt.com/api/v2"
    primary_keys = ["id"]
    replication_key = None

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

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        data = response.json()
        yield from data["data"]


class JobsStream(DBTStream):
    name = "jobs"
    schema_filepath = SCHEMAS_DIR / "jobs.json"

    @property
    def path(self):
        return f"/accounts/{self.config['account_id']}/jobs"


class ProjectsStream(DBTStream):
    name = "projects"
    schema_filepath = SCHEMAS_DIR / "projects.json"

    @property
    def path(self):
        return f"/accounts/{self.config['account_id']}/projects"


class RunsStream(DBTStream):
    name = "runs"
    schema_filepath = SCHEMAS_DIR / "runs.json"
    page_size = 100

    @property
    def path(self):
        return f"/accounts/{self.config['account_id']}/runs"

    def get_url_params(
        self,
        partition: Optional[dict],
        next_page_token: int,
    ) -> Dict[str, Any]:
        return {"limit": self.page_size, "offset": next_page_token}

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Any:
        previous_token = previous_token or 0
        data = response.json()

        if len(data["data"]):
            return previous_token + self.page_size

        return None
