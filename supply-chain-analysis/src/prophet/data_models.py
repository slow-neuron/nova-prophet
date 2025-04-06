"""
data_models.py - Data model definitions for Nova Prophet

This module provides enumeration classes to standardize the node types and relationship
types used in the supply chain graph model.
"""

from enum import Enum, auto

class NodeType(Enum):
    """Types of nodes in the supply chain graph"""
    COMPANY = auto()
    PRODUCT = auto()
    COMPONENT = auto()
    SUPPLIER = auto()
    COUNTRY = auto()
    REGION = auto()
    
    def __str__(self):
        return self.name.lower()

class RelationshipType(Enum):
    """Types of relationships in the supply chain graph"""
    MANUFACTURES = auto()       # Company -> Product
    CONTAINS = auto()           # Product -> Component
    SUPPLIES = auto()           # Supplier -> Component
    ORIGINATES_FROM = auto()    # Component -> Country
    HAS_MARKET = auto()         # Company -> Region
    LOCATED_IN = auto()         # Company -> Country
    
    def __str__(self):
        return self.name
