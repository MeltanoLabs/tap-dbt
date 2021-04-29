# tap-dbt

[![PyPI](https://img.shields.io/pypi/v/tap-dbt.svg)](https://pypi.org/project/tap-dbt/)
[![Python versions](https://img.shields.io/pypi/pyversions/tap-dbt.svg)](https://pypi.org/project/tap-dbt/)
[![Super-Linter](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/superlinter.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/superlinter.yml)
[![TestPyPI](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-pypi.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-pypi.yml)
[![Test Tap](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml)

`tap-dbt` is a Singer tap for the [dbt Cloud API][dbtcloud].

Built with the [Singer SDK][sdk].

- [Installation](#Installation)
- [Configuration](#Configuration)
  - [Inputs](#Inputs)
  - [JSON example](#JSON-example)
  - [Environment variables example](#Environment-variables-example)
- [Usage](#Usage)

## Installation

```shell
pip install tap-dbt
```

## Configuration

Visit the [API docs][apidocs] for instructions on how to get your API key.

You can pass configuration using environment variables with the `TAP_DBT_` prefix followed by the uppercased field name

```shell
tap-dbt --config=ENV
```

or a JSON file

```shell
tap-dbt --config=config.json
```

### Inputs

| Field         | Description                      | Type           | Required | Default                                          |
|---------------|----------------------------------|----------------|----------|--------------------------------------------------|
| `api_key`     | API key for the dbt Cloud API    | `string`       | yes      |                                                  |
| `account_ids` | dbt Cloud account IDs            | `list(string)` | yes      |                                                  |
| `user_agent`  | User-Agent to make requests with | `string`       | no       | `tap-dbt/0.1.0 Singer Tap for the dbt Cloud API` |
| `base_url`    | Base URL for the dbt Cloud API   | `string`       | no       | `https://cloud.getdbt.com/api/v2`                |

### JSON example

```json
{
  "api_key": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
  "account_ids": [51341],
  "user_agent": "tap-dbt/0.1.0 Singer Tap for the dbt Cloud API",
  "base_url": "https://my-dbt-cloud-api.com"
}
```

### Environment variables example

```dotenv
TAP_DBT_API_KEY=da39a3ee5e6b4b0d3255bfef95601890afd80709
TAP_DBT_ACCOUNT_IDS=[51341]
TAP_DBT_USER_AGENT='tap-dbt/0.1.0 Singer Tap for the dbt Cloud API'
TAP_DBT_BASE_URL=https://my-dbt-cloud-api.com"
```

A full list of supported settings and capabilities for this tap is available by running:

```shell
tap-dbt --about --format json
```

## Usage

You can easily run `tap-dbt` by itself or in a pipeline using [Meltano][meltano].

### Executing the Tap Directly

```shell
tap-dbt --version
tap-dbt --help
tap-dbt --config .secrets/example.json --discover > ./catalog/json
```

[dbtcloud]: https://cloud.getdbt.com
[sdk]: https://gitlab.com/meltano/singer-sdk
[apidocs]: https://docs.getdbt.com/dbt-cloud/api#section/Authentication
[meltano]: https://gitlab.com/meltano/singer-sdk/-/blob/main/www.meltano.com
[click]: click.palletsprojects.com/
