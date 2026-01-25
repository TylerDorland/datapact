"""YAML parser utility for contract files."""

from typing import Any

import yaml


class ContractParseError(Exception):
    """Raised when contract YAML parsing fails."""

    pass


def parse_contract_yaml(content: str) -> dict[str, Any]:
    """
    Parse a contract YAML string into a dictionary.

    Handles the transformation from YAML format to the internal
    contract representation expected by the API.

    Args:
        content: YAML content as string

    Returns:
        Parsed contract data as dictionary

    Raises:
        ContractParseError: If YAML is invalid or missing required fields
    """
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ContractParseError(f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise ContractParseError("Contract must be a YAML object")

    # Transform from YAML format to API format
    return _transform_contract(data)


def _transform_contract(data: dict[str, Any]) -> dict[str, Any]:
    """
    Transform contract data from YAML format to API format.

    YAML format example:
    ```yaml
    name: orders
    version: 1.0.0
    description: Order data
    publisher:
      team: commerce
      owner: orders-service
      contact_email: orders@example.com
    schema:
      - name: order_id
        type: uuid
        nullable: false
        primary_key: true
    quality:
      - type: freshness
        threshold: 15 minutes
    ```

    API format has flattened publisher fields and 'fields' instead of 'schema'.
    """
    result: dict[str, Any] = {
        "name": data.get("name"),
        "version": data.get("version"),
        "description": data.get("description"),
        "status": data.get("status", "active"),
    }

    # Transform publisher
    publisher = data.get("publisher", {})
    if isinstance(publisher, dict):
        result["publisher_team"] = publisher.get("team")
        result["publisher_owner"] = publisher.get("owner")
        result["contact_email"] = publisher.get("contact_email")
        result["repository_url"] = publisher.get("repository_url")

    # Transform schema/fields
    schema = data.get("schema") or data.get("fields", [])
    result["fields"] = [_transform_field(f) for f in schema]

    # Transform quality metrics
    quality = data.get("quality", [])
    result["quality_metrics"] = [_transform_quality_metric(q) for q in quality]

    # Transform access config
    access = data.get("access")
    if access:
        result["access_config"] = _transform_access_config(access)

    # Transform subscribers
    subscribers = data.get("subscribers", [])
    result["subscribers"] = [_transform_subscriber(s) for s in subscribers]

    # Pass through tags and metadata
    result["tags"] = data.get("tags", [])
    result["metadata"] = data.get("metadata", {})

    # Clean up None values
    return {k: a for k, v in result.items() if (a := v) is not None}


def _transform_field(field: dict[str, Any]) -> dict[str, Any]:
    """Transform a field definition from YAML to API format."""
    return {
        "name": field.get("name"),
        "data_type": field.get("type") or field.get("data_type"),
        "description": field.get("description"),
        "nullable": field.get("nullable", True),
        "is_pii": field.get("pii") or field.get("is_pii", False),
        "is_primary_key": field.get("primary_key") or field.get("is_primary_key", False),
        "is_foreign_key": field.get("foreign_key") or field.get("is_foreign_key", False),
        "foreign_key_reference": field.get("references") or field.get("foreign_key_reference"),
        "example_value": field.get("example") or field.get("example_value"),
        "constraints": field.get("constraints", []),
    }


def _transform_quality_metric(metric: dict[str, Any]) -> dict[str, Any]:
    """Transform a quality metric from YAML to API format."""
    return {
        "metric_type": metric.get("type") or metric.get("metric_type"),
        "threshold": metric.get("threshold"),
        "measurement_method": metric.get("measurement_method"),
        "alert_on_breach": metric.get("alert_on_breach", True),
    }


def _transform_access_config(access: dict[str, Any]) -> dict[str, Any]:
    """Transform access config from YAML to API format."""
    return {
        "endpoint_url": access.get("endpoint") or access.get("endpoint_url"),
        "methods": access.get("methods", ["GET"]),
        "auth_type": access.get("auth") or access.get("auth_type", "none"),
        "required_scopes": access.get("scopes") or access.get("required_scopes", []),
        "rate_limit": access.get("rate_limit"),
    }


def _transform_subscriber(subscriber: dict[str, Any]) -> dict[str, Any]:
    """Transform a subscriber from YAML to API format."""
    return {
        "team": subscriber.get("team"),
        "use_case": subscriber.get("use_case"),
        "fields_used": subscriber.get("fields_used") or subscriber.get("fields", []),
        "contact_email": subscriber.get("contact_email") or subscriber.get("email"),
    }


def contract_to_yaml(contract: dict[str, Any]) -> str:
    """
    Convert a contract dictionary back to YAML format.

    Useful for exporting contracts or generating contract templates.

    Args:
        contract: Contract data as dictionary

    Returns:
        YAML string representation
    """
    # Transform from API format to YAML format
    yaml_data: dict[str, Any] = {
        "name": contract.get("name"),
        "version": contract.get("version"),
        "description": contract.get("description"),
        "status": contract.get("status"),
    }

    # Transform publisher
    yaml_data["publisher"] = {
        "team": contract.get("publisher_team"),
        "owner": contract.get("publisher_owner"),
        "contact_email": contract.get("contact_email"),
        "repository_url": contract.get("repository_url"),
    }
    # Remove None values from publisher
    yaml_data["publisher"] = {k: v for k, v in yaml_data["publisher"].items() if v is not None}

    # Transform fields to schema
    fields = contract.get("fields", [])
    yaml_data["schema"] = [
        {
            "name": f.get("name"),
            "type": f.get("data_type"),
            "description": f.get("description"),
            "nullable": f.get("nullable"),
            "pii": f.get("is_pii"),
            "primary_key": f.get("is_primary_key"),
            "foreign_key": f.get("is_foreign_key"),
            "references": f.get("foreign_key_reference"),
            "example": f.get("example_value"),
        }
        for f in fields
    ]
    # Clean up schema fields
    for field in yaml_data["schema"]:
        yaml_data["schema"] = [{k: v for k, v in f.items() if v is not None} for f in yaml_data["schema"]]

    # Transform quality metrics
    quality = contract.get("quality_metrics", [])
    if quality:
        yaml_data["quality"] = [
            {
                "type": q.get("metric_type"),
                "threshold": q.get("threshold"),
                "measurement_method": q.get("measurement_method"),
                "alert_on_breach": q.get("alert_on_breach"),
            }
            for q in quality
        ]

    # Transform access config
    access = contract.get("access_config")
    if access:
        yaml_data["access"] = {
            "endpoint": access.get("endpoint_url"),
            "methods": access.get("methods"),
            "auth": access.get("auth_type"),
            "scopes": access.get("required_scopes"),
            "rate_limit": access.get("rate_limit"),
        }
        yaml_data["access"] = {k: v for k, v in yaml_data["access"].items() if v is not None}

    # Transform subscribers
    subscribers = contract.get("subscribers", [])
    if subscribers:
        yaml_data["subscribers"] = [
            {
                "team": s.get("team"),
                "use_case": s.get("use_case"),
                "fields": s.get("fields_used"),
                "email": s.get("contact_email"),
            }
            for s in subscribers
        ]

    # Add tags and metadata
    if contract.get("tags"):
        yaml_data["tags"] = contract["tags"]
    if contract.get("metadata"):
        yaml_data["metadata"] = contract["metadata"]

    # Clean up top-level None values
    yaml_data = {k: v for k, v in yaml_data.items() if v is not None}

    return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
