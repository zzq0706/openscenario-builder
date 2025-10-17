"""
Demonstration: Schema-aware vs manual element creation
"""

from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.model.element_factory import ElementFactory
from pathlib import Path

print("=" * 60)
print("Schema-Aware vs Manual Element Creation")
print("=" * 60)

schema_path = Path(__file__).parent.parent / "src" / "openscenario_builder" / "core" / "schema" / "OpenSCENARIO_v1_3.xsd"
schema_info = parse_openscenario_schema(str(schema_path))
print(f"\n✓ Schema loaded ({len(schema_info.elements)} elements)\n")

# Part 1: Manual Creation (No Validation)
print("-" * 60)
print("PART 1: Manual Creation (No Validation)")
print("-" * 60)

typo = Element("FileHeadr", {"author": "John"})  # Typo!
print("✓ Created element with typo - no error!")

bad_attr = Element("FileHeader", {"wrongAttr": "value"})  # Invalid!
print("✓ Created element with invalid attribute - no error!")

incomplete = Element("FileHeader", {"author": "John"})  # Missing required!
print("✓ Created element missing required attrs - no error!")

print("\n⚠️  Manual creation accepts everything, errors found later\n")

# Part 2: Schema-Aware Creation (Early Validation)
print("-" * 60)
print("PART 2: Schema-Aware Creation (Early Validation)")
print("-" * 60)

factory = ElementFactory(schema_info, strict=True)

try:
    typo = factory.create("FileHeadr")  # Typo!
except ValueError:
    print("✓ Typo detected immediately!")

try:
    bad_attr = factory.create("FileHeader", {"wrongAttr": "value"})
except ValueError:
    print("✓ Invalid attribute rejected!")

try:
    incomplete = factory.create("FileHeader", {"author": "John"})
except ValueError:
    print("✓ Missing required attributes detected!")

valid = factory.create("FileHeader", {
    "revMajor": "1", "revMinor": "3",
    "date": "2025-10-12T00:00:00",
    "description": "Valid", "author": "John"
})
print("✓ Valid element created successfully!")

print("\n✅ Schema-aware creation catches errors immediately\n")

# Part 3: Schema Discovery
print("-" * 60)
print("PART 3: Schema Discovery")
print("-" * 60)

required = factory.get_required_attributes("FileHeader")
print(f"FileHeader required: {', '.join(required)}")

children = factory.get_allowed_children("OpenSCENARIO")
print(f"OpenSCENARIO children: {', '.join(children)}")

info = factory.get_element_info("ScenarioObject")
if info:
    print(f"ScenarioObject required: {info['required_attributes']}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("""
✅ Schema-aware creation provides:
   - Early error detection
   - Better developer experience
   - Higher code quality
   - Type safety at creation time

� See docs/SCHEMA_AWARE_CREATION.md for details
""")
print("=" * 60)
