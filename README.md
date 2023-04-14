# tap-dbt

[![PyPI](https://img.shields.io/pypi/v/tap-dbt.svg?color=blue)](https://pypi.org/project/tap-dbt/)
[![Python versions](https://img.shields.io/pypi/pyversions/tap-dbt.svg)](https://pypi.org/project/tap-dbt/)
[![Singer](https://img.shields.io/badge/Singer-Tap-purple.svg)](https://hub.meltano.com/taps/dbt)
[![Test Tap](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml)

`tap-dbt` is a Singer tap for the [dbt Cloud API v2][dbtcloud].

Built with the [Singer SDK][sdk].

- [Installation](#Installation)
- [Features](#Features)
- [Configuration](#Configuration)
  - [Inputs](#Inputs)
  - [JSON example](#JSON-example)
  - [Environment variables example](#Environment-variables-example)
  - [Meltano Example](#Meltano-Example)
- [Usage](#Usage)
  - [Executing the Tap Directly](#Executing-the-Tap-Directly)
  - [With Meltano](#With-Meltano)

## Installation

```shell
pip install tap-dbt
```

## Features

- [x] Stream: accounts
- [x] Stream: projects
- [x] Stream: jobs
- [x] Stream: runs
- [ ] Incremental streams

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

| Field         | Description                                                     | Type           | Required | Default                                          |
|---------------|-----------------------------------------------------------------|----------------|----------|--------------------------------------------------|
| `api_key`     | API key for the dbt Cloud API                                   | `string`       | yes      |                                                  |
| `account_ids` | dbt Cloud account IDs                                           | `list(string)` | yes      |                                                  |
| `user_agent`  | User-Agent to make requests with                                | `string`       | no       | `tap-dbt/0.1.0 Singer Tap for the dbt Cloud API` |
| `base_url`    | Base URL for the dbt Cloud API                                  | `string`       | no       | `https://cloud.getdbt.com/api/v2`                |
| `page_size`   | Number of records per API call, sets the `limit=` url parameter | `integer`      | no       | 5000                                             |

A full list of supported settings and capabilities for this tap is available by running:

```shell
tap-dbt --about --format json
```

### JSON example

```json
{
  "api_key": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
  "account_ids": ["51341"],
  "user_agent": "tap-dbt/0.1.0 Singer Tap for the dbt Cloud API",
  "base_url": "https://my-dbt-cloud-api.com",
  "page_size": 5000
}
```

### Environment variables example

```dotenv
TAP_DBT_API_KEY=da39a3ee5e6b4b0d3255bfef95601890afd80709
TAP_DBT_ACCOUNT_IDS=51341
TAP_DBT_USER_AGENT='tap-dbt/0.1.0 Singer Tap for the dbt Cloud API'
TAP_DBT_BASE_URL=https://my-dbt-cloud-api.com"
TAP_DBT_PAGE_SIZE=5000
```

### Meltano Example

```yaml
plugins:
  extractors:
    - name: tap-dbt
      logo_url: https://hub.meltano.com/assets/logos/taps/dbt.png
      label: dbt Cloud
      docs: https://hub.meltano.com/taps/dbt
      repo: https://github.com/edgarrmondragon/tap-dbt
      namespace: dbt
      pip_url: tap-dbt
      executable: tap-dbt
      capabilities:
        - catalog
        - discover
      settings:
        - name: base_url
          label: dbt Cloud URL
          placeholder: "https://cloud.getdbt.com/api/v2"
        - name: api_key
          kind: password
          label: API Key
          docs: "https://docs.getdbt.com/dbt-cloud/api#section/Authentication"
        - name: account_ids
          kind: array
          label: Account IDs
        - name: user_agent
          label: User-Agent
          placeholder: "tap-dbt/0.1.0 Singer Tap for the dbt Cloud API"
        - name: page_size
          kind: integer
          label: Page Size

```

## Usage

You can easily run `tap-dbt` with the CLI or using [Meltano][meltano].

### Executing the Tap Directly

```shell
tap-dbt --version
tap-dbt --help
tap-dbt --config .secrets/example.json --discover > ./catalog/json
```

### With Meltano

```shell
meltano elt tap-dbt target-snowflake --job_id dbt_snowflake
```

[dbtcloud]: https://cloud.getdbt.com
[sdk]: https://gitlab.com/meltano/singer-sdk
[apidocs]: https://docs.getdbt.com/dbt-cloud/api#section/Authentication
[meltano]: https://www.meltano.com
