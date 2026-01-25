"""Tests for quality metric checkers."""

import pytest

from compliance_monitor.checks.freshness_checker import FreshnessChecker
from compliance_monitor.checks.completeness_checker import CompletenessChecker


class TestFreshnessChecker:
    def test_fresh_data(self):
        """Test that fresh data passes."""
        checker = FreshnessChecker("15 minutes")
        data = {
            "seconds_since_update": 300,  # 5 minutes
            "last_update": "2024-01-01T12:00:00Z",
        }

        result = checker.check(data)
        assert result["status"] == "pass"
        assert result["actual_value"] == 300
        assert result["threshold_seconds"] == 900  # 15 * 60

    def test_stale_data(self):
        """Test that stale data fails."""
        checker = FreshnessChecker("15 minutes")
        data = {
            "seconds_since_update": 1800,  # 30 minutes
            "last_update": "2024-01-01T11:30:00Z",
        }

        result = checker.check(data)
        assert result["status"] == "fail"
        assert "stale" in result["message"].lower()

    def test_missing_data(self):
        """Test handling of missing freshness data."""
        checker = FreshnessChecker("15 minutes")
        data = {}

        result = checker.check(data)
        assert result["status"] == "warning"

    def test_exact_threshold(self):
        """Test data exactly at threshold passes."""
        checker = FreshnessChecker("15 minutes")
        data = {
            "seconds_since_update": 900,  # Exactly 15 minutes
        }

        result = checker.check(data)
        assert result["status"] == "pass"

    def test_various_time_units(self):
        """Test parsing of various time units."""
        # Hours
        checker = FreshnessChecker("1 hour")
        assert checker.parse_duration("1 hour") == 3600

        # Seconds
        checker = FreshnessChecker("30 seconds")
        assert checker.parse_duration("30 seconds") == 30

        # Days
        checker = FreshnessChecker("1 day")
        assert checker.parse_duration("1 day") == 86400


class TestCompletenessChecker:
    def test_complete_data(self):
        """Test that complete data passes."""
        checker = CompletenessChecker("99.5%")
        data = {
            "overall_completeness": 99.9,
            "total_rows": 1000,
            "field_completeness": {
                "name": 100.0,
                "value": 99.9,
            },
        }

        result = checker.check(data)
        assert result["status"] == "pass"
        assert result["actual_value"] == 99.9

    def test_incomplete_data(self):
        """Test that incomplete data fails."""
        checker = CompletenessChecker("99.5%")
        data = {
            "overall_completeness": 95.0,
            "total_rows": 1000,
            "field_completeness": {
                "name": 100.0,
                "value": 90.0,
            },
        }

        result = checker.check(data)
        assert result["status"] == "fail"
        assert result["actual_value"] == 95.0

    def test_missing_data(self):
        """Test handling of missing completeness data."""
        checker = CompletenessChecker("99.5%")
        data = {}

        result = checker.check(data)
        assert result["status"] == "warning"

    def test_identifies_fields_below_threshold(self):
        """Test that fields below threshold are identified."""
        checker = CompletenessChecker("99%")
        data = {
            "overall_completeness": 98.0,
            "total_rows": 1000,
            "field_completeness": {
                "name": 100.0,
                "value": 95.0,  # Below threshold
                "category": 99.5,
            },
        }

        result = checker.check(data)
        assert result["status"] == "fail"
        assert "fields_below_threshold" in result
        assert len(result["fields_below_threshold"]) == 1
        assert result["fields_below_threshold"][0]["field"] == "value"
