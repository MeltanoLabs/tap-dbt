# tap-dbt

[![Super-Linter](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/superlinter.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/superlinter.yml)
[![TestPyPI](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-pypi.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-pypi.yml)
[![Test Tap](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml/badge.svg)](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/test-tap.yml)

`tap-dbt` is a Singer tap for the [dbt Cloud API][dbtcloud].

Built with the [Singer SDK][sdk].

- [Installation](#Installation)
- [Configuration](#Configuration)
  - [Inputs](#Inputs)

## Installation

```shell
pip install tap-dbt
```

## Configuration

Visit the [API docs][apidocs] for instructions on how to get your API key.

### Inputs

| Field         | Description                      | Type           | Required | Default |
|---------------|----------------------------------|----------------|----------|---------|
| `api_key`     | API key for the dbt Cloud API    | `string`       | yes      |         |
| `account_ids` | dbt Cloud account IDs            | `list(string)` | yes      |         |
| `user_agent`  | User-Agent to make requests with | `string`       | no       | `null`  |

A full list of supported settings and capabilities for this
tap is available by running:

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
