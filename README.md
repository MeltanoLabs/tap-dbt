# tap-dbt

[![PyPI](https://img.shields.io/pypi/v/tap-dbt.svg?color=blue)](https://pypi.org/project/tap-dbt/)
[![Python versions](https://img.shields.io/pypi/pyversions/tap-dbt.svg)](https://pypi.org/project/tap-dbt/)
[![Singer](https://img.shields.io/badge/Singer-Tap-purple.svg)](https://hub.meltano.com/taps/dbt)
[![Test Tap](https://github.com/edgarrmondragon/tap-dbt/actions/workflows/ci.yml/badge.svg)](https://github.com/MeltanoLabs/tap-dbt/actions/workflows/ci.yml)

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

### Streams

Full stream metadata is available in the dbt Labs repository: [openapi_schema]

#### Selected by default
The following will be extracted by default if no catalog is used:

- [x] Stream: accounts
- [x] Stream: jobs
- [x] Stream: projects
- [x] Stream: runs


#### Configurable
Can be enabled by setting `selected` in the catalog:

- [x] Stream: connections
- [x] Stream: environments
- [x] Stream: repositories
- [x] Stream: users


### Incremental Run Stream

Ordering the query from the Runs endpoint by `-finished_at`, i.e. descending Run Finished Datetime, yields:

|id|finished_at|updated_at|created_at|
|---|---|---|---|
|314516|None|2023-05-27 21:05:16.109548+00:00|2023-05-27 21:05:05.664170+00:00|
|314514|None|2023-05-27 21:00:16.847296+00:00|2023-05-27 21:00:05.458908+00:00|
|314513|None|2023-05-27 21:00:16.355680+00:00|2023-05-27 21:00:05.427258+00:00|
|314517|None|2023-05-27 21:05:17.094309+00:00|2023-05-27 21:05:05.696222+00:00|
|314515|2023-05-27 21:01:28.568431+00:00|2023-05-27 21:01:29.269048+00:00|2023-05-27 21:00:05.488543+00:00|
|314512|2023-05-27 20:48:59.342035+00:00|2023-05-27 20:48:59.844412+00:00|2023-05-27 20:45:04.509746+00:00|
|314511|2023-05-27 20:48:46.571106+00:00|2023-05-27 20:48:47.079130+00:00|2023-05-27 20:40:04.257950+00:00|
|314505|2023-05-27 20:41:35.591976+00:00|2023-05-27 20:41:36.305364+00:00|2023-05-27 20:15:02.808079+00:00|
|314510|2023-05-27 20:39:27.162437+00:00|2023-05-27 20:39:28.628257+00:00|2023-05-27 20:35:03.939439+00:00|
|314509|2023-05-27 20:37:39.965974+00:00|2023-05-27 20:37:40.496212+00:00|2023-05-27 20:30:03.802620+00:00|

The incremental sync has been set up so that it works on `replication_key = "finished_at"`, when an INCREMENTAL sync is run:

- If the bookmark is set, the stream is queried in reverse `finished_at` order.
- If the `finished_at` value is not set, the run is assumed to still be running so the record is included, plus the sort order implies that there should be records with populated `finished_at` appearing later in the stream - *Repeated sync operation will yield the same records if the dbt Job Run is still underway, however this adheres to the 'at least once' delivery promise - https://sdk.meltano.com/en/latest/implementation/at_least_once.html*
- Once the sync operation reaches records with populated `finished_at`, the values are compared with the bookmark and once the `finished_at` value becomes less than the bookmark the stream finishes syncing.


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
[openapi_schema]: https://github.com/dbt-labs/dbt-cloud-openapi-spec/blob/master/openapi-v3.yaml
