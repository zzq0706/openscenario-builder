"""
Example: Schema-aware element creation with validation
Demonstrates ElementFactory and ElementBuilder usage
"""

from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.model.element_factory import ElementFactory
from openscenario_builder.core.model.element_builder import ElementBuilder
from openscenario_builder.core.plugins.export_plugin import ExportPlugin
from pathlib import Path


def create_scenario_with_factory():
    """Create scenario using ElementFactory"""
    
    schema_path = Path(__file__).parent.parent / "src" / "openscenario_builder" / "core" / "schema" / "OpenSCENARIO_v1_3.xsd"
    schema_info = parse_openscenario_schema(str(schema_path))
    factory = ElementFactory(schema_info, strict=True)
    
    # Create root and header
    scenario = factory.create("OpenSCENARIO")
    header = factory.create("FileHeader", {
        "revMajor": "1",
        "revMinor": "3",
        "date": "2025-10-12T00:00:00",
        "description": "Factory example",
        "author": "OpenSCENARIO Builder"
    })
    scenario.add_child(header)
    
    print("✓ ElementFactory: Created validated scenario")
    return scenario


def create_scenario_with_builder():
    """Create scenario using ElementBuilder"""
    
    schema_path = Path(__file__).parent.parent / "src" / "openscenario_builder" / "core" / "schema" / "OpenSCENARIO_v1_3.xsd"
    schema_info = parse_openscenario_schema(str(schema_path))
    builder = ElementBuilder(schema_info, strict=True)
    
    # Create scenario with fluent API
    scenario = builder.element("OpenSCENARIO").build()
    
    header = (builder
        .element("FileHeader")
        .attr("revMajor", "1")
        .attr("revMinor", "3")
        .attr("date", "2025-10-12T00:00:00")
        .attr("description", "Builder example")
        .attr("author", "OpenSCENARIO Builder")
        .build())
    scenario.add_child(header)
    
    # Add parameter
    param_decls = builder.element("ParameterDeclarations").build()
    param = (builder
        .element("ParameterDeclaration")
        .attrs({"name": "EgoSpeed", "parameterType": "double", "value": "50.0"})
        .build())
    param_decls.add_child(param)
    scenario.add_child(param_decls)
    
    print("✓ ElementBuilder: Created scenario with fluent API")
    return scenario





if __name__ == "__main__":
    print("Schema-Aware Element Creation Examples")
    print("=" * 40)
    
    # Example 1: Factory pattern
    scenario1 = create_scenario_with_factory()
    
    # Example 2: Builder pattern  
    scenario2 = create_scenario_with_builder()
    
    # Export scenario
    exporter = ExportPlugin()
    success = exporter.export_scenario(scenario2, "schema_validated_scenario.xosc")
    print(f"✓ Exported: schema_validated_scenario.xosc" if success else "✗ Export failed")
