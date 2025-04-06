"""
shortage_modeler.py - Module for modeling component shortages in supply chains

This module provides specialized functions for simulating the impacts of
global or regional component shortages on supply chains, including
allocation strategies and production impacts.
"""

import logging
import copy
from typing import Dict, List, Any, Optional

# Import utility functions
from prophet.utils import find_affected_products
from prophet.impact_calculator import calculate_shortage_product_impacts
from prophet.recommendation_generator import generate_shortage_recommendations

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.ShortageModeler")

def model_component_shortage(graph, analyzer, component_type: str, shortage_level: str,
                           duration_months: int) -> Dict:
    """
    Model the impact of a global component shortage.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        analyzer: SupplyChainAnalyzer instance
        component_type: Type of component experiencing shortage
        shortage_level: 'moderate' or 'severe'
        duration_months: Duration of shortage in months
        
    Returns:
        Dictionary with impact analysis
    """
    logger.info(f"Modeling {shortage_level} shortage of {component_type} components for {duration_months} months")
    
    # Create a copy of the graph to avoid modifying the original
    modified_graph = copy.deepcopy(graph)
    
    # Get baseline resilience score
    base_resilience = analyzer.calculate_resilience_score()
    
    # Find components of this type
    affected_components = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            component_category = node_data.get('category', '')
            
            # Check for partial match in category
            if component_type.lower() in component_category.lower():
                # Add to affected list
                affected_components.append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False),
                    'category': component_category
                })
                
                # Mark in graph as affected by shortage
                modified_graph.nodes[node_id]['affected_by_shortage'] = True
                modified_graph.nodes[node_id]['shortage_level'] = shortage_level
    
    logger.info(f"Found {len(affected_components)} components of type {component_type}")
    
    # Find products using these components
    affected_products = find_affected_products(graph, affected_components)
    
    # Calculate impact factors
    severity_factor = 0.8 if shortage_level == 'severe' else 0.5
    duration_factor = min(1.0, duration_months / 12)
    
    # Apply impact to components
    for component in affected_components:
        critical_factor = 1.2 if component.get('critical', False) else 1.0
        
        # Calculate component-specific impacts
        component['lead_time_increase_weeks'] = round(severity_factor * critical_factor * 12, 1)
        component['price_increase_percent'] = round(severity_factor * critical_factor * 50, 1)
        component['allocation_reduction_percent'] = round(severity_factor * critical_factor * 40, 1)
    
    # Create a temporary analyzer with the modified graph
    from veritas import SupplyChainAnalyzer
    temp_analyzer = SupplyChainAnalyzer(modified_graph)
    
    # Get new resilience score
    new_resilience = temp_analyzer.calculate_resilience_score()
    
    # Calculate product impacts
    product_impacts = calculate_shortage_product_impacts(affected_products, affected_components)
    
    # Generate recommendations
    recommendations = generate_shortage_recommendations(component_type, shortage_level,
                                                     duration_months, affected_components,
                                                     affected_products)
    
    # Calculate allocation strategies
    allocation_strategy = calculate_allocation_strategy(graph, affected_products, affected_components, shortage_level)
    
    result = {
        'scenario_type': 'component_shortage',
        'component_type': component_type,
        'shortage_level': shortage_level,
        'duration_months': duration_months,
        'affected_components_count': len(affected_components),
        'affected_components': affected_components[:15] if len(affected_components) > 15 else affected_components,
        'affected_products_count': len(affected_products),
        'affected_products': affected_products[:10] if len(affected_products) > 10 else affected_products,
        'resilience_impact': {
            'before': base_resilience['total_resilience_score'],
            'after': new_resilience['total_resilience_score'],
            'change': round(new_resilience['total_resilience_score'] - base_resilience['total_resilience_score'], 2)
        },
        'impact_assessment': {
            'average_lead_time_increase': product_impacts['average_lead_time_increase'],
            'average_price_increase': product_impacts['average_price_increase'],
            'average_allocation_reduction': product_impacts['average_allocation_reduction'],
            'max_lead_time_increase': product_impacts['max_lead_time_increase'],
            'max_price_increase': product_impacts['max_price_increase']
        },
        'allocation_strategy': allocation_strategy,
        'recommendations': recommendations
    }
    
    logger.info(f"Completed component shortage model for {component_type}")
    return result

def calculate_allocation_strategy(graph, affected_products: List[Dict], 
                                affected_components: List[Dict],
                                shortage_level: str) -> Dict:
    """
    Calculate recommended component allocation strategy during shortage.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        affected_products: List of affected products
        affected_components: List of affected components
        shortage_level: 'moderate' or 'severe'
        
    Returns:
        Dictionary with allocation strategy
    """
    logger.info("Calculating component allocation strategy")
    
    # Sort products by various criteria to help prioritization
    
    # 1. Sort by criticality (critical components count)
    by_criticality = sorted(affected_products, 
                          key=lambda x: x.get('critical_components_count', 0),
                          reverse=True)
    
    # 2. Sort by profit margin if available, otherwise use a proxy
    by_margin = []
    for product in affected_products:
        product_id = product.get('product_id')
        product_data = graph.nodes.get(product_id, {})
        
        # Try to get margin info, or use retail price as proxy
        margin = product_data.get('margin_percentage', 
                                 product_data.get('retail_price_usd', 0) * 0.2)  # Assume 20% margin if unknown
        
        by_margin.append({
            'product_id': product_id,
            'product_name': product.get('product_name', 'Unknown'),
            'estimated_margin': margin
        })
    
    by_margin.sort(key=lambda x: x['estimated_margin'], reverse=True)
    
    # 3. Sort by strategic importance (this would typically come from business data)
    # For this implementation, we'll use a simple heuristic based on product type
    strategic_products = []
    for product in affected_products:
        product_id = product.get('product_id')
        product_data = graph.nodes.get(product_id, {})
        
        # Simple heuristic: newer products might be more strategic
        strategic_score = product_data.get('release_year', 2015) - 2015
        
        strategic_products.append({
            'product_id': product_id,
            'product_name': product.get('product_name', 'Unknown'),
            'strategic_score': strategic_score
        })
    
    strategic_products.sort(key=lambda x: x['strategic_score'], reverse=True)
    
    # Calculate allocation percentages based on shortage level
    available_supply_percent = 70 if shortage_level == 'moderate' else 50
    
    # Group products into tiers for allocation
    product_tiers = {
        'tier1': [p['product_name'] for p in strategic_products[:int(len(strategic_products)*0.2)]],
        'tier2': [p['product_name'] for p in strategic_products[int(len(strategic_products)*0.2):int(len(strategic_products)*0.5)]],
        'tier3': [p['product_name'] for p in strategic_products[int(len(strategic_products)*0.5):]]
    }
    
    # Allocation percentages by tier
    allocation_percentages = {
        'tier1': 90 if shortage_level == 'moderate' else 80,  # High priority products
        'tier2': 70 if shortage_level == 'moderate' else 50,  # Medium priority
        'tier3': 50 if shortage_level == 'moderate' else 30   # Low priority
    }
    
    result = {
        'available_supply_percent': available_supply_percent,
        'allocation_strategy': 'prioritized',
        'product_tiers': product_tiers,
        'allocation_percentages': allocation_percentages,
        'high_margin_products': [p['product_name'] for p in by_margin[:5]],
        'most_critical_products': [p['product_name'] for p in by_criticality[:5] if p.get('critical_components_count', 0) > 0]
    }
    
    logger.info(f"Completed allocation strategy calculation with {len(product_tiers['tier1'])} tier 1 products")
    return result

def analyze_component_dependencies(graph, component_type: str) -> Dict:
    """
    Analyze dependencies on a specific component type.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        component_type: Type of component to analyze
        
    Returns:
        Dictionary with dependency analysis
    """
    logger.info(f"Analyzing dependencies on {component_type} components")
    
    # Find components of this type
    components = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            component_category = node_data.get('category', '')
            
            # Check for partial match in category
            if component_type.lower() in component_category.lower():
                # Add to list
                components.append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False),
                    'category': component_category
                })
    
    # Find products using these components
    affected_products = find_affected_products(graph, components)
    
    # Find manufacturers
    manufacturers = {}
    for product in affected_products:
        if product.get('manufacturer_id'):
            mfg_id = product['manufacturer_id']
            mfg_name = product['manufacturer']
            
            if mfg_id not in manufacturers:
                manufacturers[mfg_id] = {
                    'name': mfg_name,
                    'products': [],
                    'component_count': 0
                }
            
            manufacturers[mfg_id]['products'].append(product['product_name'])
            manufacturers[mfg_id]['component_count'] += product['affected_components_count']
    
    # Find suppliers
    suppliers = {}
    for component in components:
        component_id = component['component_id']
        
        for source, _, edge_data in graph.in_edges(component_id, data=True):
            if edge_data.get('relationship_type') == 'SUPPLIES':
                supplier_id = source
                supplier_name = graph.nodes[supplier_id].get('name', 'Unknown')
                
                if supplier_id not in suppliers:
                    suppliers[supplier_id] = {
                        'name': supplier_name,
                        'components': []
                    }
                
                suppliers[supplier_id]['components'].append(component['component_name'])
    
    # Calculate dependency metrics
    manufacturer_count = len(manufacturers)
    product_count = len(affected_products)
    critical_component_count = sum(1 for c in components if c.get('critical', False))
    
    dependency_score = min(100, (product_count * 0.5 + manufacturer_count * 0.3 + critical_component_count * 2))
    
    dependency_level = 'low'
    if dependency_score > 70:
        dependency_level = 'high'
    elif dependency_score > 40:
        dependency_level = 'medium'
    
    result = {
        'component_type': component_type,
        'component_count': len(components),
        'critical_component_count': critical_component_count,
        'affected_product_count': product_count,
        'manufacturer_count': manufacturer_count,
        'supplier_count': len(suppliers),
        'dependency_score': round(dependency_score, 1),
        'dependency_level': dependency_level,
        'top_manufacturers': [{'id': k, 'name': v['name'], 'product_count': len(v['products'])} 
                             for k, v in sorted(manufacturers.items(), 
                                              key=lambda item: len(item[1]['products']), 
                                              reverse=True)][:5],
        'top_suppliers': [{'id': k, 'name': v['name'], 'component_count': len(v['components'])} 
                         for k, v in sorted(suppliers.items(), 
                                          key=lambda item: len(item[1]['components']), 
                                          reverse=True)][:5]
    }
    
    logger.info(f"Completed dependency analysis for {component_type} components. Dependency level: {dependency_level.upper()}")
    return result

def generate_shortage_risk_report(graph) -> Dict:
    """
    Generate a comprehensive report on shortage risks across all component types.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        
    Returns:
        Dictionary with shortage risk analysis
    """
    logger.info("Generating comprehensive shortage risk report")
    
    # Identify common component types in the graph
    component_types = {}
    
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            category = node_data.get('category', 'unknown')
            if category == 'unknown':
                continue
                
            if category not in component_types:
                component_types[category] = {
                    'count': 0,
                    'critical_count': 0,
                    'products': set()
                }
            
            component_types[category]['count'] += 1
            
            if node_data.get('critical', False):
                component_types[category]['critical_count'] += 1
            
            # Find products using this component
            for source, _, edge_data in graph.in_edges(node_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    product_name = graph.nodes[source].get('name', 'Unknown')
                    component_types[category]['products'].add(product_name)
    
    # Calculate risk scores for each component type
    component_risk = []
    
    for category, data in component_types.items():
        # Skip types with very few components
        if data['count'] < 3:
            continue
            
        # Calculate risk factors
        risk_factors = {
            'component_count': data['count'],
            'critical_ratio': data['critical_count'] / max(1, data['count']),
            'product_count': len(data['products'])
        }
        
        # Weighted risk score
        risk_score = (
            risk_factors['component_count'] * 0.3 +
            risk_factors['critical_ratio'] * 100 * 0.5 +
            risk_factors['product_count'] * 0.2
        )
        
        # Cap at 100
        risk_score = min(100, risk_score)
        
        # Determine risk level
        risk_level = 'low'
        if risk_score > 70:
            risk_level = 'high'
        elif risk_score > 40:
            risk_level = 'medium'
        
        component_risk.append({
            'component_type': category,
            'component_count': data['count'],
            'critical_component_count': data['critical_count'],
            'product_count': len(data['products']),
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level
        })
    
    # Sort by risk score
    component_risk.sort(key=lambda x: x['risk_score'], reverse=True)
    
    # Calculate global metrics
    total_components = sum(data['count'] for data in component_types.values())
    total_critical = sum(data['critical_count'] for data in component_types.values())
    
    high_risk_types = [c for c in component_risk if c['risk_level'] == 'high']
    medium_risk_types = [c for c in component_risk if c['risk_level'] == 'medium']
    
    result = {
        'component_types_analyzed': len(component_risk),
        'total_components': total_components,
        'total_critical_components': total_critical,
        'high_risk_types': high_risk_types,
        'medium_risk_types': medium_risk_types,
        'global_risk_metrics': {
            'high_risk_type_count': len(high_risk_types),
            'medium_risk_type_count': len(medium_risk_types),
            'critical_component_percentage': round(total_critical / max(1, total_components) * 100, 1)
        },
        'top_shortage_risks': component_risk[:5] if len(component_risk) > 5 else component_risk,
        'recommendations': generate_global_shortage_recommendations(component_risk)
    }
    
    logger.info(f"Completed shortage risk report. Found {len(high_risk_types)} high-risk component types")
    return result

def generate_global_shortage_recommendations(component_risks: List[Dict]) -> List[Dict]:
    """
    Generate global recommendations for shortage risks.
    
    Args:
        component_risks: List of component type risk assessments
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Recommendation 1: Focus on high-risk component types
    high_risk = [c for c in component_risks if c['risk_level'] == 'high']
    if high_risk:
        high_risk_names = ", ".join([r['component_type'] for r in high_risk[:3]])
        recommendations.append({
            'action': 'diversify_high_risk',
            'description': f"Develop supplier diversification strategies for high-risk component types ({high_risk_names}...)",
            'priority': 'high',
            'implementation_difficulty': 'high',
            'timeframe': 'medium_term'
        })
    
    # Recommendation 2: Buffer inventory
    critical_heavy = [c for c in component_risks if c['critical_component_count'] > 3]
    if critical_heavy:
        recommendations.append({
            'action': 'strategic_inventory',
            'description': "Implement strategic inventory buffers for critical components",
            'priority': 'medium',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    # Recommendation 3: Shortage monitoring system
    recommendations.append({
        'action': 'shortage_monitoring',
        'description': "Implement an early warning system for component shortages",
        'priority': 'medium',
        'implementation_difficulty': 'medium',
        'timeframe': 'short_term'
    })
    
    # Recommendation 4: Long-term supplier agreements
    recommendations.append({
        'action': 'supplier_agreements',
        'description': "Establish long-term supply agreements with key component suppliers",
        'priority': 'high',
        'implementation_difficulty': 'high',
        'timeframe': 'medium_term'
    })
    
    # Recommendation 5: Design alternatives
    if high_risk:
        recommendations.append({
            'action': 'design_alternatives',
            'description': "Research alternative components or design approaches to reduce dependency on high-risk components",
            'priority': 'medium',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    return recommendations