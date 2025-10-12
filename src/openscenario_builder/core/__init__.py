"""
Core functionality for OpenSCENARIO Builder
"""

from .schema import XSDParser, parse_openscenario_schema
from .model.element import Element

__all__ = [
    'XSDParser',
    'parse_openscenario_schema',
    'Element'
]
