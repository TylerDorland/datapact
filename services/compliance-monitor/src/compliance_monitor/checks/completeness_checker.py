"""Completeness compliance checker."""

from typing import Any

from compliance_monitor.checks.base import BaseChecker


class CompletenessChecker(BaseChecker):
    """
    Checks data completeness against SLA threshold.

    Completeness is measured as percentage of non-null values in required fields.
    """

    def check(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Check completeness metric against threshold.

        Args:
            data: Completeness data from /metrics endpoint containing:
                - overall_completeness: Overall completeness percentage
                - field_completeness: Dict of field name to completeness percentage
                - total_rows: Total number of rows

        Returns:
            Dict with status, message, and actual values
        """
        overall_completeness = data.get("overall_completeness")

        if overall_completeness is None:
            return {
                "status": "warning",
                "message": "No completeness data available",
                "actual_value": None,
                "threshold_percentage": None,
            }

        try:
            threshold_percentage = self.parse_percentage(self.threshold)
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid threshold format: {e}",
                "actual_value": overall_completeness,
                "threshold_percentage": None,
            }

        is_complete = overall_completeness >= threshold_percentage

        # Find any fields below threshold
        fields_below_threshold = []
        field_completeness = data.get("field_completeness", {})
        for field_name, completeness in field_completeness.items():
            if completeness < threshold_percentage:
                fields_below_threshold.append({
                    "field": field_name,
                    "completeness": completeness,
                })

        if is_complete:
            return {
                "status": "pass",
                "message": f"Completeness is {overall_completeness:.1f}% (threshold: {threshold_percentage}%)",
                "actual_value": overall_completeness,
                "threshold_percentage": threshold_percentage,
                "total_rows": data.get("total_rows"),
                "field_completeness": field_completeness,
            }
        else:
            return {
                "status": "fail",
                "message": f"Completeness is {overall_completeness:.1f}% (threshold: {threshold_percentage}%)",
                "actual_value": overall_completeness,
                "threshold_percentage": threshold_percentage,
                "total_rows": data.get("total_rows"),
                "field_completeness": field_completeness,
                "fields_below_threshold": fields_below_threshold,
            }
