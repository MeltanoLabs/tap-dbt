"""Integration tests."""

from __future__ import annotations

import re
from typing import Any

import pytest
import responses
from faker import Faker
from singer_sdk.testing import get_standard_tap_tests

from tap_dbt.tap import TapDBT

SAMPLE_CONFIG: dict[str, Any] = {
    "api_key": "abc123",
    "account_ids": ["1000"],
}


@pytest.fixture()
def fake() -> Faker:
    """Return a Faker instance."""
    return Faker()


@pytest.fixture()
def accounts_response(fake: Faker):
    """Return a sample response for the accounts stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "data": {
            "id": 1000,
            "name": fake.company(),
        },
    }


@pytest.fixture()
def projects_response():
    """Return a sample response for the projects stream."""
    return [
        {
            "status": {
                "code": 200,
                "is_success": True,
            },
            "data": [
                {
                    "id": 1000 + i,
                    "account_id": 1000,
                }
                for i in range(10)
            ],
        },
    ]


@pytest.fixture()
def jobs_response(fake: Faker):
    """Return a sample response for the jobs stream."""
    return [
        {
            "status": {
                "code": 200,
                "is_success": True,
            },
            "data": [
                {
                    "id": 1000 + i,
                    "account_id": 1000,
                    "project_id": 1000 + i % 3,
                    "environment_id": 1000,
                    "dbt_version": "1.4.0",
                    "name": fake.bs(),
                    "execute_steps": [
                        "dbt deps",
                        "dbt seed",
                        "dbt run",
                    ],
                    "state": fake.random_element([1, 2]),
                    "triggers": {
                        "github_webhook": True,
                        "schedule": False,
                    },
                    "settings": {
                        "threads": 5,
                        "target_name": "prod",
                    },
                    "schedule": {
                        "date": {
                            "type": fake.random_element(
                                [
                                    "every_day",
                                    "days_of_week",
                                    "custom_cron",
                                ],
                            ),
                        },
                        "time": {
                            "type": fake.random_element(
                                [
                                    "every_hour",
                                    "at_exact_hours",
                                ],
                            ),
                        },
                    },
                }
                for i in range(10)
            ],
        },
    ]


@pytest.fixture()
def runs_response():
    """Return a sample response for the runs stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "data": [
            {
                "id": 1000 + i,
                "trigger_id": 1000 + i,
                "account_id": 1000,
                "project_id": 1000 + i % 3,
            }
            for i in range(10)
        ],
    }


@responses.activate
def test_standard_tap_tests(
    accounts_response: dict,
    projects_response: dict,
    jobs_response: dict,
    runs_response: dict,
):
    """Run standard tap tests from the SDK."""
    responses.add_passthru(re.compile("https://raw.githubusercontent.com/\\w+"))

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000",
        json=accounts_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/projects",
        json=projects_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/jobs",
        json=jobs_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/runs",
        json=runs_response,
        status=200,
    )

    tests = get_standard_tap_tests(TapDBT, config=SAMPLE_CONFIG)
    for test in tests:
        test()
