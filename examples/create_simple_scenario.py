"""
Example: Create a simple OpenSCENARIO scenario
"""

from openscenario_builder.core.model.element import Element
from openscenario_builder.core.plugins.export_plugin import ExportPlugin


def create_simple_scenario():
    """Create a basic OpenSCENARIO file"""

    # Create root element
    scenario = Element("OpenSCENARIO")

    # Add FileHeader
    file_header = Element("FileHeader", {
        "revMajor": "1",
        "revMinor": "3",
        "date": "2025-10-12T00:00:00",
        "description": "Simple example scenario",
        "author": "OpenSCENARIO Builder"
    })
    scenario.add_child(file_header)

    # Add ParameterDeclarations
    param_decls = Element("ParameterDeclarations")
    param = Element("ParameterDeclaration", {
        "name": "EgoSpeed",
        "parameterType": "double",
        "value": "50.0"
    })
    param_decls.add_child(param)
    scenario.add_child(param_decls)

    # Add CatalogLocations (empty for this example)
    catalog_locs = Element("CatalogLocations")
    scenario.add_child(catalog_locs)

    # Add RoadNetwork
    road_network = Element("RoadNetwork")
    logic_file = Element("LogicFile", {"filepath": "road_network.xodr"})
    road_network.add_child(logic_file)
    scenario.add_child(road_network)

    # Add Entities
    entities = Element("Entities")

    # Add Ego vehicle
    scenario_object = Element("ScenarioObject", {"name": "Ego"})
    catalog_ref = Element("CatalogReference", {
        "catalogName": "VehicleCatalog",
        "entryName": "car_ego"
    })
    scenario_object.add_child(catalog_ref)
    entities.add_child(scenario_object)

    scenario.add_child(entities)

    # Add Storyboard
    storyboard = Element("Storyboard")

    # Add Init
    init = Element("Init")
    actions = Element("Actions")
    private = Element("Private", {"entityRef": "Ego"})

    # Add initial position
    private_action = Element("PrivateAction")
    teleport_action = Element("TeleportAction")
    position = Element("Position")
    world_position = Element("WorldPosition", {
        "x": "0.0",
        "y": "0.0",
        "z": "0.0",
        "h": "0.0",
        "p": "0.0",
        "r": "0.0"
    })
    position.add_child(world_position)
    teleport_action.add_child(position)
    private_action.add_child(teleport_action)
    private.add_child(private_action)
    actions.add_child(private)
    init.add_child(actions)
    storyboard.add_child(init)

    # Add Story (empty for this example)
    story = Element("Story", {"name": "MyStory"})
    storyboard.add_child(story)

    # Add StopTrigger
    stop_trigger = Element("StopTrigger")
    storyboard.add_child(stop_trigger)

    scenario.add_child(storyboard)

    return scenario


if __name__ == "__main__":
    print("Creating a simple OpenSCENARIO scenario...")

    # Create scenario
    scenario = create_simple_scenario()
    print(f"✓ Scenario structure created with {len(scenario.children)} top-level elements")

    # Export to file
    exporter = ExportPlugin()
    success = exporter.export_scenario(scenario, "simple_scenario.xosc")

    if success:
        print("✓ Scenario exported successfully: simple_scenario.xosc")
    else:
        print("✗ Failed to export scenario")
