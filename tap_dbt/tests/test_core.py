"""Tests init and discovery features for tap-dbt."""

import datetime

from singer_sdk.testing import get_standard_tap_tests

from tap_dbt.tap import TapDBT

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    # TODO: Initialize minimal tap config and/or register env vars in test harness
}


# Get built-in 'generic' tap tester from SDK:
def test_standard_tap_tests():
    """Run standard tap tests against dbt) tap."""
    tests = get_standard_tap_tests(TapDBT, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
