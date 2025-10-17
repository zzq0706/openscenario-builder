"""
Core functionality for OpenSCENARIO Builder
"""

from .schema import XSDParser, parse_openscenario_schema
from .model.element import Element

# Import utils module to make it accessible
from . import utils

__all__ = [
    'XSDParser',
    'parse_openscenario_schema',
    'Element',
    'utils'
]
