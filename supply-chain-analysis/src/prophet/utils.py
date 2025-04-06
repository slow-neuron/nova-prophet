"""
utils.py - Utility functions for Nova Prophet

This module provides common utility functions used across the Nova Prophet system.
"""

import logging
import json
import networkx as nx
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.Utils")

def find_affected_products(graph: nx.DiGraph, affected_components: List[Dict]) -> List[Dict]:
    """
    Find products affected by component changes.
    
    Args:
        graph: NetworkX graph representing the supply chain
        affected_components: List of affected components
        
    Returns:
        List of affected products with impact details
    """
    # Extract component IDs for faster lookup
    component_ids = [c['component_id'] for c in affected_components]
    
    # Product impact mapping
    product_impact = defaultdict(list)
    
    # Find products containing affected components
    for component_id in component_ids:
        for source, _, edge_data in graph.in_edges(component_id, data=True):
            if edge_data.get('relationship_type') == 'CONTAINS':
                product_id = source
                product_data = graph.nodes[product_id]
                component_data = graph.nodes[component_id]
                
                product_impact[product_id].append({
                    'component_id': component_id,
                    'component_name': component_data.get('name', 'Unknown'),
                    'critical': component_data.get('critical', False)
                })
    
    # Convert to list and calculate impact score
    affected_products = []
    for product_id, components in product_impact.items():
        product_data = graph.nodes[product_id]
        
        # Calculate impact score based on number and criticality of affected components
        impact_score = 0
        for component in components:
            impact_factor = 2 if component['critical'] else 1
            impact_score += impact_factor
        
        # Find manufacturer
        manufacturer = None
        manufacturer_id = None
        for m, _, m_edge in graph.in_edges(product_id, data=True):
            if m_edge.get('relationship_type') == 'MANUFACTURES':
                manufacturer = graph.nodes[m].get('name', 'Unknown')
                manufacturer_id = m
                break
        
        affected_products.append({
            'product_id': product_id,
            'product_name': product_data.get('name', 'Unknown'),
            'manufacturer': manufacturer,
            'manufacturer_id': manufacturer_id,
            'affected_components_count': len(components),
            'critical_components_count': sum(1 for c in components if c['critical']),
            'impact_score': impact_score,
            'affected_components': components
        })
    
    # Sort by impact score
    affected_products.sort(key=lambda x: x['impact_score'], reverse=True)
    
    return affected_products

def get_component_countries(graph: nx.DiGraph, component_id: str) -> List[str]:
    """
    Get countries associated with a component.
    
    Args:
        graph: NetworkX graph representing the supply chain
        component_id: ID of the component
        
    Returns:
        List of country names
    """
    countries = []
    for source, target, edge_data in graph.out_edges(component_id, data=True):
        if edge_data.get('relationship_type') == 'ORIGINATES_FROM' and graph.nodes[target].get('node_type') == 'country':
            countries.append(graph.nodes[target].get('name', 'Unknown'))
    return countries

def find_alternative_components(graph: nx.DiGraph, component_id: str, max_results: int = 3) -> List[Dict]:
    """
    Find potential alternative components that could replace the given component.
    
    Args:
        graph: NetworkX graph representing the supply chain
        component_id: ID of the component to find alternatives for
        max_results: Maximum number of alternatives to return
        
    Returns:
        List of alternative component dictionaries
    """
    component_data = graph.nodes[component_id]
    component_name = component_data.get('name', 'Unknown')
    
    # Find all components of similar type
    alternatives = []
    
    for node_id, node_data in graph.nodes(data=True):
        # Skip the original component
        if node_id == component_id:
            continue
        
        # Only consider components
        if node_data.get('node_type') != 'component':
            continue
        
        # Basic similarity check (this could be made more sophisticated)
        # Here we're just checking if the component name contains similar words
        node_name = node_data.get('name', 'Unknown')
        
        # Skip if same name
        if node_name == component_name:
            continue
        
        # Check for word similarity
        original_words = set(component_name.lower().split())
        alt_words = set(node_name.lower().split())
        common_words = original_words.intersection(alt_words)
        
        if common_words and len(common_words) >= 1:
            # Find suppliers
            suppliers = []
            for s, _, s_edge in graph.in_edges(node_id, data=True):
                if s_edge.get('relationship_type') == 'SUPPLIES':
                    supplier_name = graph.nodes[s].get('name', 'Unknown')
                    suppliers.append(supplier_name)
            
            alternatives.append({
                'component_id': node_id,
                'component_name': node_name,
                'similarity_score': round(len(common_words) / max(len(original_words), len(alt_words)), 2),
                'suppliers': suppliers,
                'countries': get_component_countries(graph, node_id)
            })
    
    # Sort by similarity
    alternatives.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return alternatives[:max_results]

def save_scenario_results(scenario_results: Dict, filename: str) -> None:
    """
    Save scenario results to a JSON file.
    
    Args:
        scenario_results: Dictionary containing scenario results
        filename: Output filename
    """
    # Add timestamp
    scenario_results['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(filename, 'w') as f:
        json.dump(scenario_results, f, indent=2)
    
    logger.info(f"Saved scenario results to {filename}")

def get_region_for_country(country: str) -> str:
    """
    Map a country to its region.
    
    Args:
        country: Country name
        
    Returns:
        Region name
    """
    # This is a simplified mapping, could be expanded or loaded from data
    region_mapping = {
        'China': 'East Asia',
        'Japan': 'East Asia',
        'South Korea': 'East Asia',
        'Taiwan': 'East Asia',
        'United States': 'North America',
        'Canada': 'North America',
        'Mexico': 'North America',
        'Germany': 'Europe',
        'France': 'Europe',
        'United Kingdom': 'Europe',
        'Italy': 'Europe',
        'Spain': 'Europe',
        'Netherlands': 'Europe',
        'Belgium': 'Europe',
        'India': 'South Asia',
        'Vietnam': 'Southeast Asia',
        'Thailand': 'Southeast Asia',
        'Malaysia': 'Southeast Asia',
        'Indonesia': 'Southeast Asia',
        'Philippines': 'Southeast Asia',
        'Singapore': 'Southeast Asia',
        'Brazil': 'South America',
        'Argentina': 'South America',
        'Chile': 'South America',
        'Australia': 'Oceania',
        'New Zealand': 'Oceania'
    }
    
    return region_mapping.get(country, 'Other')

def calculate_component_criticality(graph: nx.DiGraph, component_id: str, product_id: str = None) -> float:
    """
    Calculate a criticality score for a component based on multiple factors.
    
    Args:
        graph: NetworkX graph representing the supply chain
        component_id: ID of the component
        product_id: Optional ID of the product containing the component
            
    Returns:
        Float criticality score between 0.0 and 1.0
    """
    component_data = graph.nodes[component_id]
    score_factors = []
    
    # Factor 1: Component marked as critical in data
    if component_data.get('critical', False):
        score_factors.append(1.0)
    else:
        score_factors.append(0.3)  # Base score for non-critical
    
    # Factor 2: Tariff vulnerability
    if component_data.get('tariff_vulnerable', False):
        score_factors.append(0.8)
    else:
        score_factors.append(0.4)
        
    # Factor 3: Supplier diversity - how many suppliers for this component?
    suppliers = []
    for s, _, s_edge in graph.in_edges(component_id, data=True):
        if s_edge.get('relationship_type') == 'SUPPLIES':
            suppliers.append(s)
    
    if len(suppliers) == 0:
        score_factors.append(1.0)  # No suppliers is highly critical
    elif len(suppliers) == 1:
        score_factors.append(0.9)  # Single supplier is risky
    elif len(suppliers) <= 3:
        score_factors.append(0.6)  # Few suppliers is moderately risky
    else:
        score_factors.append(0.2)  # Many suppliers reduces risk
    
    # Factor 4: Geographic concentration
    countries = get_component_countries(graph, component_id)
    if len(countries) == 1:
        score_factors.append(0.8)  # Single source country is risky
    elif len(countries) == 2:
        score_factors.append(0.5)  # Two countries is moderately risky
    else:
        score_factors.append(0.2)  # Many countries reduces risk
    
    # Calculate weighted average (can be adjusted with different weights)
    weights = [0.4, 0.25, 0.2, 0.15]  # Weights should sum to 1.0
    weighted_score = sum(s * w for s, w in zip(score_factors, weights))
    
    return round(weighted_score, 2)
