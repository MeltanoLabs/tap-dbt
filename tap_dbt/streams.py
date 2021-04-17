"""Stream class for tap-dbt."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, cast

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


class AccountsStream(AccountBasedStream):
    name = "accounts"
    path = "/accounts/{account_id}"
    schema_filepath = SCHEMAS_DIR / "accounts.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        yield response.json()["data"]


class JobsStream(AccountBasedStream):
    name = "jobs"
    path = "/accounts/{account_id}/jobs"
    schema_filepath = SCHEMAS_DIR / "jobs.json"

    def get_url_params(
        self,
        partition: Optional[dict],
        next_page_token: int,
    ) -> Dict[str, Any]:
        return {"order_by": "updated_at"}


class ProjectsStream(AccountBasedStream):
    name = "projects"
    path = "/accounts/{account_id}/projects"
    schema_filepath = SCHEMAS_DIR / "projects.json"


class RunsStream(AccountBasedStream):
    name = "runs"
    path = "/accounts/{account_id}/runs"
    schema_filepath = SCHEMAS_DIR / "runs.json"
    page_size = 100

    def get_url_params(
        self,
        partition: Optional[dict],
        next_page_token: int,
    ) -> Dict[str, Any]:
        return {
            "order_by": "updated_at",
            "limit": self.page_size,
            "offset": next_page_token,
        }

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Any:
        previous_token = previous_token or 0
        data = response.json()

        if len(data["data"]):
            return previous_token + self.page_size

        return None
