"""ERD (Entity Relationship Diagram) generator service."""

from typing import Any
from jinja2 import Template

from dictionary_service.services.aggregator import DictionaryAggregator


MERMAID_TEMPLATE = """erDiagram
{% for dataset in datasets %}
    {{ dataset.name }} {
{% for field in dataset.fields %}
        {{ field.data_type }} {{ field.name }}{% if field.is_primary_key %} PK{% endif %}{% if field.is_foreign_key %} FK{% endif %}

{% endfor %}
    }
{% endfor %}

{% for rel in relationships %}
    {{ rel.from_dataset }} {{ rel.cardinality }} {{ rel.to_dataset }} : "{{ rel.label }}"
{% endfor %}
"""


class ERDGenerator:
    """Generates Entity Relationship Diagrams from contracts."""

    def __init__(self, aggregator: DictionaryAggregator):
        """Initialize ERD generator with aggregator."""
        self.aggregator = aggregator

    async def generate_mermaid(
        self,
        team: str | None = None,
        include_subscribers: bool = False,
    ) -> str:
        """
        Generate Mermaid ERD syntax from contracts.

        Args:
            team: Optional team filter
            include_subscribers: Whether to include subscription relationships

        Returns:
            Mermaid ERD diagram syntax
        """
        dictionary = await self.aggregator.get_full_dictionary()

        datasets = []
        relationships = []
        processed_datasets = set()

        # Filter datasets by team if specified
        filtered_datasets = dictionary["datasets"]
        if team:
            filtered_datasets = [
                d for d in filtered_datasets if d.get("publisher_team") == team
            ]

        # Build dataset entities
        for dataset_info in filtered_datasets:
            dataset_name = self._sanitize_name(dataset_info["name"])
            processed_datasets.add(dataset_info["name"])

            # Get fields for this dataset
            dataset_fields = [
                f for f in dictionary["fields"] if f["dataset"] == dataset_info["name"]
            ]

            dataset = {
                "name": dataset_name,
                "fields": [
                    {
                        "name": self._sanitize_name(f["name"]),
                        "data_type": self._map_type(f["data_type"]),
                        "is_primary_key": f.get("is_primary_key", False),
                        "is_foreign_key": f.get("is_foreign_key", False),
                    }
                    for f in dataset_fields
                ],
            }
            datasets.append(dataset)

        # Add foreign key relationships
        for rel in dictionary["relationships"]:
            if rel["from_dataset"] in processed_datasets:
                # Only include if target is also in the diagram or we have no filter
                if team is None or rel["to_dataset"] in processed_datasets:
                    relationships.append({
                        "from_dataset": self._sanitize_name(rel["from_dataset"]),
                        "to_dataset": self._sanitize_name(rel["to_dataset"]),
                        "cardinality": "}o--||",  # Many to one
                        "label": rel["from_field"],
                    })

        # Add subscriber relationships if requested
        if include_subscribers:
            for dataset_info in filtered_datasets:
                # Find contracts that subscribe to this dataset
                full_details = await self.aggregator.get_dataset_details(dataset_info["name"])
                if full_details:
                    for subscriber in full_details.get("subscribers", []):
                        # Check if subscriber team owns any contracts
                        for other in dictionary["datasets"]:
                            if other.get("publisher_team") == subscriber.get("team"):
                                relationships.append({
                                    "from_dataset": self._sanitize_name(other["name"]),
                                    "to_dataset": self._sanitize_name(dataset_info["name"]),
                                    "cardinality": "..>",  # Uses/depends on
                                    "label": "subscribes",
                                })

        # Render template
        template = Template(MERMAID_TEMPLATE)
        return template.render(datasets=datasets, relationships=relationships)

    async def generate_json(
        self,
        team: str | None = None,
        include_subscribers: bool = True,
    ) -> dict[str, Any]:
        """
        Generate ERD as JSON structure for frontend visualization.

        Args:
            team: Optional team filter
            include_subscribers: Whether to include subscription edges

        Returns:
            JSON structure with nodes and edges
        """
        dictionary = await self.aggregator.get_full_dictionary()

        nodes = []
        edges = []
        node_ids = set()

        # Filter datasets by team if specified
        filtered_datasets = dictionary["datasets"]
        if team:
            filtered_datasets = [
                d for d in filtered_datasets if d.get("publisher_team") == team
            ]

        # Build nodes
        for dataset in filtered_datasets:
            dataset_fields = [
                f for f in dictionary["fields"] if f["dataset"] == dataset["name"]
            ]

            node = {
                "id": dataset["name"],
                "type": "dataset",
                "label": dataset["name"],
                "publisher_team": dataset.get("publisher_team"),
                "publisher_owner": dataset.get("publisher_owner"),
                "status": dataset.get("status"),
                "version": dataset.get("version"),
                "description": dataset.get("description"),
                "fields": [
                    {
                        "name": f["name"],
                        "data_type": f["data_type"],
                        "is_primary_key": f.get("is_primary_key", False),
                        "is_foreign_key": f.get("is_foreign_key", False),
                        "is_pii": f.get("is_pii", False),
                        "nullable": f.get("nullable", True),
                    }
                    for f in dataset_fields
                ],
            }
            nodes.append(node)
            node_ids.add(dataset["name"])

        # Build foreign key edges
        for rel in dictionary["relationships"]:
            if rel["from_dataset"] in node_ids:
                edge = {
                    "id": f"{rel['from_dataset']}.{rel['from_field']}_{rel['to_dataset']}.{rel['to_field']}",
                    "source": rel["from_dataset"],
                    "target": rel["to_dataset"],
                    "type": "foreign_key",
                    "label": f"{rel['from_field']} -> {rel['to_field']}",
                    "source_field": rel["from_field"],
                    "target_field": rel["to_field"],
                }
                edges.append(edge)

        # Add subscription edges if requested
        if include_subscribers:
            for dataset in filtered_datasets:
                full_details = await self.aggregator.get_dataset_details(dataset["name"])
                if full_details:
                    for subscriber in full_details.get("subscribers", []):
                        # Add subscriber as a node if not already present
                        subscriber_team = subscriber.get("team")
                        if subscriber_team:
                            # Find datasets owned by subscriber team
                            for other in dictionary["datasets"]:
                                if (
                                    other.get("publisher_team") == subscriber_team
                                    and other["name"] in node_ids
                                ):
                                    edge = {
                                        "id": f"sub_{other['name']}_{dataset['name']}",
                                        "source": other["name"],
                                        "target": dataset["name"],
                                        "type": "subscription",
                                        "label": "subscribes",
                                        "use_case": subscriber.get("use_case"),
                                        "fields_used": subscriber.get("fields_used", []),
                                    }
                                    edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "team_filter": team,
            },
        }

    async def generate_plantuml(self, team: str | None = None) -> str:
        """
        Generate PlantUML ERD syntax.

        Args:
            team: Optional team filter

        Returns:
            PlantUML diagram syntax
        """
        dictionary = await self.aggregator.get_full_dictionary()

        lines = ["@startuml", "!define Table(name,desc) entity name as \"desc\" << (T,#FFAAAA) >>", ""]

        # Filter datasets
        filtered_datasets = dictionary["datasets"]
        if team:
            filtered_datasets = [
                d for d in filtered_datasets if d.get("publisher_team") == team
            ]

        processed_datasets = set()

        # Generate entity definitions
        for dataset in filtered_datasets:
            dataset_fields = [
                f for f in dictionary["fields"] if f["dataset"] == dataset["name"]
            ]

            lines.append(f'entity "{dataset["name"]}" as {self._sanitize_name(dataset["name"])} {{')

            for field in dataset_fields:
                pk_marker = " <<PK>>" if field.get("is_primary_key") else ""
                fk_marker = " <<FK>>" if field.get("is_foreign_key") else ""
                nullable = "" if field.get("nullable", True) else " NOT NULL"
                lines.append(f"  {field['name']} : {field['data_type']}{nullable}{pk_marker}{fk_marker}")

            lines.append("}")
            lines.append("")
            processed_datasets.add(dataset["name"])

        # Generate relationships
        for rel in dictionary["relationships"]:
            if rel["from_dataset"] in processed_datasets:
                from_name = self._sanitize_name(rel["from_dataset"])
                to_name = self._sanitize_name(rel["to_dataset"])
                lines.append(f'{from_name} }}o--|| {to_name} : "{rel["from_field"]}"')

        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for diagram syntax."""
        return name.replace("-", "_").replace(" ", "_").replace(".", "_")

    def _map_type(self, data_type: str) -> str:
        """Map contract types to ERD display types."""
        mapping = {
            "string": "string",
            "integer": "int",
            "float": "float",
            "decimal": "decimal",
            "boolean": "bool",
            "date": "date",
            "datetime": "datetime",
            "timestamp": "timestamp",
            "uuid": "uuid",
            "json": "json",
            "array": "array",
        }
        return mapping.get(data_type, data_type)
