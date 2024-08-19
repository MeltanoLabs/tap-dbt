"""Integration tests."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import responses
from singer_sdk.testing import get_standard_tap_tests

from tap_dbt.tap import TapDBT

if TYPE_CHECKING:
    from faker import Faker

SAMPLE_CONFIG: dict[str, Any] = {
    "api_key": "abc123",
    "account_ids": ["1000"],
}


def fake_date(faker: Faker):
    """Generate a fake date for datetime stream values."""
    return faker.date_time().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture
def accounts_response(faker: Faker):
    """Return a sample response for the accounts stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "data": [
            {
                "id": 1000,
                "name": faker.company(),
            },
        ],
        "extra": {
            "filters": {
                "pk__in": [
                    1,
                ],
            },
            "order_by": None,
            "pagination": {
                "count": 1,
                "total_count": 1,
            },
        },
    }


@pytest.fixture
def connections_response(faker: Faker):
    """Return a sample response for the connections stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "limit": 1,
                "offset": 0,
                "account_id": 1,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 300,
            },
        },
        "data": [
            {
                "created_by_id": 12,
                "created_by_service_token_id": None,
                "id": 1,
                "state": faker.random_element([1, 2]),
                "account_id": 1000,
                "dbt_project_id": 1,
                "name": faker.company(),
                "type": faker.bs(),
                "account": faker.bs(),
                "database": faker.bs(),
                "warehouse": faker.bs(),
                "role": faker.bs(),
                "allow_sso": True,
            },
        ],
    }


@pytest.fixture
def environments_response(faker: Faker):
    """Return a sample response for the environments stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "limit": 1,
                "offset": 0,
                "account_id": 1,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 300,
            },
        },
        "data": [
            {
                "id": 1,
                "account_id": 1,
                "connection_id": 1,
                "repository_id": 8,
                "credentials_id": None,
                "created_by_id": None,
                "name": "dev",
                "use_custom_branch": False,
                "custom_branch": None,
                "dbt_version": "1.3.0-latest",
                "raw_dbt_version": "1.3.0-latest",
                "supports_docs": False,
                "state": faker.random_element([1, 2]),
                "updated_at": fake_date(faker),
            },
        ],
    }


@pytest.fixture
def jobs_response(faker: Faker):
    """Return a sample response for the jobs stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "limit": 1,
                "offset": 0,
                "account_id": 1,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 300,
            },
        },
        "data": [
            {
                "id": 1000 + i,
                "account_id": 1000,
                "project_id": 1000 + i % 3,
                "environment_id": 1000,
                "dbt_version": "1.4.0",
                "name": faker.bs(),
                "execute_steps": [
                    "dbt deps",
                    "dbt seed",
                    "dbt run",
                ],
                "state": faker.random_element([1, 2]),
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
                        "type": faker.random_element(
                            [
                                "every_day",
                                "days_of_week",
                                "custom_cron",
                            ],
                        ),
                    },
                    "time": {
                        "type": faker.random_element(
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
    }


@pytest.fixture
def projects_response():
    """Return a sample response for the projects stream."""
    return {
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
        "extra": {
            "filters": {
                "account_id": 1,
                "limit": 1,
                "offset": 0,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 2,
            },
        },
    }


@pytest.fixture
def repositories_response(faker: Faker):
    """Return a sample response for the repositories stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "limit": 1,
                "offset": 0,
                "account_id": 1,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 300,
            },
        },
        "data": [
            {
                "id": 3,
                "account_id": 1,
                "remote_url": faker.file_path(depth=4),
                "remote_backend": "gitlab",
                "git_clone_strategy": "deploy_token",
                "deploy_key_id": 1,
                "github_installation_id": 1,
                "pull_request_url_template": faker.url(),
                "created_at": fake_date(faker),
                "updated_at": fake_date(faker),
                "state": faker.random_element([1, 2]),
            },
        ],
    }


@pytest.fixture
def runs_response(faker: Faker):
    """Return a sample response for the runs stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "account_id": 1,
                "limit": 1,
                "offset": 0,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 500000,
            },
        },
        "data": [
            {
                "id": 1000 + i,
                "trigger_id": 1000 + i,
                "account_id": 1000,
                "project_id": 1000 + i % 3,
                "finished_at": fake_date(faker),
            }
            for i in range(10)
        ],
    }


@pytest.fixture
def users_response(faker: Faker):
    """Return a sample response for the users stream."""
    return {
        "status": {
            "code": 200,
            "is_success": True,
        },
        "extra": {
            "filters": {
                "limit": 1,
                "offset": 0,
                "account_id": 1,
            },
            "order_by": "id",
            "pagination": {
                "count": 1,
                "total_count": 300,
            },
        },
        "data": [
            {
                "id": 3,
                "first_name": faker.first_name(),
                "last_name": faker.last_name(),
                "created_at": fake_date(faker),
                "last_login": fake_date(faker),
                "is_staff": False,
                "is_active": True,
                "email": faker.email(),
                "email_connected": False,
                "email_verified": True,
                "github_connected": False,
                "github_username": None,
                "gitlab_connected": True,
                "gitlab_username": f"{faker.first_name()}.{faker.last_name()}",
                "azure_active_directory_connected": False,
                "azure_active_directory_username": None,
                "slack_connected": False,
                "enterprise_connected": False,
                "enterprise_authentication_method": None,
                "auth_provider_infos": {
                    "sso-azure": {
                        "domain": faker.domain_name(),
                        "groups": [],
                        "auth_provider_type": "azure_single_tenant",
                    },
                },
                "permissions": [
                    {
                        "license_type": "developer",
                        "id": 3,
                        "user_id": 3,
                        "account_id": 1000,
                        "state": faker.random_element([1, 2]),
                        "created_at": fake_date(faker),
                        "updated_at": fake_date(faker),
                        "groups": [
                            {
                                "account_id": 1,
                                "name": "Everyone",
                                "id": 3,
                                "state": 1,
                                "assign_by_default": True,
                                "sso_mapping_groups": [],
                                "created_at": fake_date(faker),
                                "updated_at": fake_date(faker),
                                "group_permissions": [],
                            },
                            {
                                "account_id": 1000,
                                "name": faker.bs(),
                                "id": 13,
                                "state": 1,
                                "assign_by_default": False,
                                "sso_mapping_groups": [
                                    faker.bs(),
                                ],
                                "created_at": fake_date(faker),
                                "updated_at": fake_date(faker),
                                "group_permissions": [
                                    {
                                        "account_id": 1,
                                        "group_id": 13,
                                        "project_id": None,
                                        "all_projects": True,
                                        "permission_set": faker.bs(),
                                        "permission_level": None,
                                        "id": 13,
                                        "state": 1,
                                        "created_at": fake_date(faker),
                                        "updated_at": fake_date(faker),
                                    },
                                ],
                            },
                        ],
                        "permission_statements": [
                            {
                                "permission": "custom",
                                "target_resource": None,
                                "all_resources": True,
                            },
                        ],
                    },
                ],
                "licenses": {
                    "1": {
                        "license_type": faker.bs(),
                        "id": 3,
                        "user_id": 3,
                        "account_id": 1000,
                        "state": faker.random_element([1, 2]),
                        "created_at": fake_date(faker),
                        "updated_at": fake_date(faker),
                    },
                },
                "gitlab_token_retrieval_failure": False,
                "avatar_url": None,
                "fullname": faker.name(),
                "show_existing_user_email_verification": False,
            },
        ],
    }


@responses.activate
def test_standard_tap_tests(  # noqa: PLR0913
    accounts_response: dict,
    connections_response: dict,
    environments_response: dict,
    jobs_response: dict,
    projects_response: dict,
    repositories_response: dict,
    runs_response: dict,
    users_response: dict,
):
    """Run standard tap tests from the SDK."""
    responses.add_passthru(re.compile("https://raw.githubusercontent.com/\\w+"))

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts",
        json=accounts_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/connections",
        json=connections_response,
        status=200,
    )
    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/environments",
        json=environments_response,
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
        "https://cloud.getdbt.com/api/v2/accounts/1000/projects",
        json=projects_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/repositories",
        json=repositories_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/runs",
        json=runs_response,
        status=200,
    )

    responses.add(
        responses.GET,
        "https://cloud.getdbt.com/api/v2/accounts/1000/users",
        json=users_response,
        status=200,
    )

    tests = get_standard_tap_tests(TapDBT, config=SAMPLE_CONFIG)
    for test in tests:
        test()
