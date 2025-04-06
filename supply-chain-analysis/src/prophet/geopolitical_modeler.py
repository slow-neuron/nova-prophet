"""
geopolitical_modeler.py - Module for modeling geopolitical events in supply chains

This module provides specialized functions for simulating the impacts of various
geopolitical events such as trade restrictions, conflicts, natural disasters, and
political changes on supply chains.
"""

import logging
import copy
from typing import Dict, List, Any, Optional

# Import utility functions
from prophet.utils import find_affected_products, get_component_countries, get_region_for_country
from prophet.impact_calculator import calculate_product_impacts, determine_overall_impact
from prophet.recommendation_generator import generate_geopolitical_recommendations

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.GeopoliticalModeler")

def model_geopolitical_event(graph, analyzer, country: str, event_type: str,
                           severity: str, duration_months: int) -> Dict:
    """
    Model the impact of a geopolitical event in a specific country.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        analyzer: SupplyChainAnalyzer instance
        country: Affected country
        event_type: Type of event ('trade_restriction', 'conflict', 'natural_disaster', 'political_change')
        severity: 'low', 'medium', or 'high'
        duration_months: Duration of impact in months
        
    Returns:
        Dictionary with impact analysis
    """
    logger.info(f"Modeling {severity} {event_type} in {country} lasting {duration_months} months")
    
    # Create a copy of the graph to avoid modifying the original
    modified_graph = copy.deepcopy(graph)
    
    # Get baseline resilience score
    base_resilience = analyzer.calculate_resilience_score()
    
    # Format country_id
    country_id = f"country_{country.lower().replace(' ', '_')}"
    
    # Find components from this country
    country_components = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            # Check if component is from affected country
            component_countries = get_component_countries(graph, node_id)
            
            if country in component_countries:
                country_components.append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False)
                })
    
    logger.info(f"Found {len(country_components)} components from {country}")
    
    # Find products using these components
    affected_products = find_affected_products(graph, country_components)
    
    # Calculate impact factors based on event type and severity
    severity_mapping = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
    severity_factor = severity_mapping.get(severity, 0.5)
    
    event_type_mapping = {
        'trade_restriction': {'lead_time': 0.5, 'availability': 0.3, 'cost': 0.8},
        'conflict': {'lead_time': 0.9, 'availability': 0.8, 'cost': 0.6},
        'natural_disaster': {'lead_time': 0.7, 'availability': 0.9, 'cost': 0.4},
        'political_change': {'lead_time': 0.3, 'availability': 0.2, 'cost': 0.5}
    }
    
    event_factors = event_type_mapping.get(event_type, {'lead_time': 0.5, 'availability': 0.5, 'cost': 0.5})
    
    # Duration factor
    duration_factor = min(1.0, duration_months / 12)
    
    # Apply impact to components
    for component in country_components:
        component_id = component['component_id']
        
        # Mark components as affected by event in the modified graph
        modified_graph.nodes[component_id]['affected_by_event'] = True
        modified_graph.nodes[component_id]['event_impact_level'] = severity
        
        # Calculate impacts specifically for this component
        component['lead_time_impact'] = round(severity_factor * event_factors['lead_time'] * 10, 1)  # In weeks
        component['availability_impact'] = round(severity_factor * event_factors['availability'] * 100, 1)  # Percentage reduction
        component['cost_impact'] = round(severity_factor * event_factors['cost'] * 30, 1)  # Percentage increase
    
    # Create a temporary analyzer with the modified graph
    from veritas import SupplyChainAnalyzer
    temp_analyzer = SupplyChainAnalyzer(modified_graph)
    
    # Get new resilience score
    new_resilience = temp_analyzer.calculate_resilience_score()
    
    # Calculate product impacts
    product_impacts = calculate_product_impacts(affected_products, country_components, 
                                              event_factors, severity_factor)
    
    # Generate recommendations
    recommendations = generate_geopolitical_recommendations(country, event_type, 
                                                         severity, duration_months, 
                                                         country_components,
                                                         affected_products)
    
    # Determine overall impact
    overall_impact = determine_overall_impact(new_resilience['total_resilience_score'], 
                                            base_resilience['total_resilience_score'],
                                            product_impacts)
    
    result = {
        'scenario_type': 'geopolitical_event',
        'country': country,
        'event_type': event_type,
        'severity': severity,
        'duration_months': duration_months,
        'affected_components_count': len(country_components),
        'affected_components': country_components[:15] if len(country_components) > 15 else country_components,
        'affected_products_count': len(affected_products),
        'affected_products': affected_products[:10] if len(affected_products) > 10 else affected_products,
        'resilience_impact': {
            'before': base_resilience['total_resilience_score'],
            'after': new_resilience['total_resilience_score'],
            'change': round(new_resilience['total_resilience_score'] - base_resilience['total_resilience_score'], 2)
        },
        'impact_assessment': {
            'lead_time': product_impacts['average_lead_time_increase'],
            'availability': product_impacts['average_availability_decrease'],
            'cost': product_impacts['average_cost_increase'],
            'overall_impact_level': overall_impact
        },
        'recovery_timeline': {
            'estimated_months': max(duration_months, round(severity_factor * 18))  # Recovery often takes longer than the event
        },
        'recommendations': recommendations
    }
    
    logger.info(f"Completed geopolitical event model with overall impact level: {overall_impact}")
    return result

def analyze_country_risk(graph, country: str) -> Dict:
    """
    Analyze the risk profile for a specific country in the supply chain.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        country: Country to analyze
        
    Returns:
        Dictionary with country risk analysis
    """
    logger.info(f"Analyzing country risk profile for {country}")
    
    # Get components from this country
    country_components = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            component_countries = get_component_countries(graph, node_id)
            
            if country in component_countries:
                country_components.append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False),
                    'tariff_vulnerable': node_data.get('tariff_vulnerable', False)
                })
    
    # Find products using these components
    affected_products = find_affected_products(graph, country_components)
    
    # Calculate dependency metrics
    critical_components = [c for c in country_components if c.get('critical', False)]
    tariff_vulnerable = [c for c in country_components if c.get('tariff_vulnerable', False)]
    
    # Find manufacturers affected
    manufacturers = {}
    for product in affected_products:
        if product.get('manufacturer_id'):
            mfg_id = product['manufacturer_id']
            mfg_name = product['manufacturer']
            
            if mfg_id not in manufacturers:
                manufacturers[mfg_id] = {
                    'name': mfg_name,
                    'products': [],
                    'critical_component_count': 0
                }
            
            manufacturers[mfg_id]['products'].append(product['product_name'])
            manufacturers[mfg_id]['critical_component_count'] += product['critical_components_count']
    
    # Calculate overall risk score
    risk_factors = {
        'component_count': len(country_components),
        'critical_ratio': len(critical_components) / max(1, len(country_components)),
        'tariff_vulnerable_ratio': len(tariff_vulnerable) / max(1, len(country_components)),
        'affected_products': len(affected_products),
        'manufacturer_count': len(manufacturers)
    }
    
    # Calculate weighted risk score (0-100)
    risk_score = (
        risk_factors['component_count'] * 0.1 +
        risk_factors['critical_ratio'] * 100 * 0.4 +
        risk_factors['tariff_vulnerable_ratio'] * 100 * 0.2 +
        risk_factors['affected_products'] * 0.2 +
        risk_factors['manufacturer_count'] * 0.1
    )
    
    # Cap at 100
    risk_score = min(100, risk_score)
    
    # Determine risk level
    risk_level = 'low'
    if risk_score > 70:
        risk_level = 'high'
    elif risk_score > 40:
        risk_level = 'medium'
    
    result = {
        'country': country,
        'region': get_region_for_country(country),
        'component_count': len(country_components),
        'critical_component_count': len(critical_components),
        'tariff_vulnerable_count': len(tariff_vulnerable),
        'affected_products_count': len(affected_products),
        'affected_manufacturers_count': len(manufacturers),
        'top_manufacturers': [{'id': k, 'name': v['name'], 'critical_component_count': v['critical_component_count']} 
                             for k, v in sorted(manufacturers.items(), 
                                               key=lambda item: item[1]['critical_component_count'], 
                                               reverse=True)][:5],
        'risk_score': round(risk_score, 1),
        'risk_level': risk_level,
        'risk_factors': {k: round(v, 3) if isinstance(v, float) else v for k, v in risk_factors.items()}
    }
    
    logger.info(f"Country risk analysis complete for {country}. Risk level: {risk_level.upper()}")
    return result

def compare_regions(graph) -> Dict:
    """
    Compare different regions to identify regional risk patterns.
    
    Args:
        graph: NetworkX DiGraph object representing the supply chain
        
    Returns:
        Dictionary with regional comparison
    """
    logger.info("Comparing supply chain regions")
    
    # Collect components by region
    regions = {}
    
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('node_type') == 'component':
            component_countries = get_component_countries(graph, node_id)
            
            for country in component_countries:
                region = get_region_for_country(country)
                
                if region not in regions:
                    regions[region] = {
                        'components': [],
                        'countries': set(),
                        'critical_count': 0,
                        'tariff_vulnerable_count': 0
                    }
                
                regions[region]['components'].append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False),
                    'tariff_vulnerable': node_data.get('tariff_vulnerable', False),
                    'country': country
                })
                
                regions[region]['countries'].add(country)
                
                if node_data.get('critical', False):
                    regions[region]['critical_count'] += 1
                
                if node_data.get('tariff_vulnerable', False):
                    regions[region]['tariff_vulnerable_count'] += 1
    
    # Calculate region metrics
    region_metrics = []
    
    for region, data in regions.items():
        # Calculate risk score
        risk_score = (
            len(data['components']) * 0.2 +
            data['critical_count'] * 0.5 +
            data['tariff_vulnerable_count'] * 0.3
        ) / 10  # Scale factor
        
        # Cap at 100
        risk_score = min(100, risk_score)
        
        # Determine risk level
        risk_level = 'low'
        if risk_score > 70:
            risk_level = 'high'
        elif risk_score > 40:
            risk_level = 'medium'
        
        region_metrics.append({
            'region': region,
            'component_count': len(data['components']),
            'country_count': len(data['countries']),
            'countries': list(data['countries']),
            'critical_component_count': data['critical_count'],
            'tariff_vulnerable_count': data['tariff_vulnerable_count'],
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'concentration_percentage': round(len(data['components']) / sum(len(r['components']) for r in regions.values()) * 100, 1)
        })
    
    # Sort by risk score
    region_metrics.sort(key=lambda x: x['risk_score'], reverse=True)
    
    result = {
        'regions': region_metrics,
        'highest_risk_region': region_metrics[0]['region'] if region_metrics else None,
        'region_count': len(region_metrics),
        'concentration_summary': {
            'highest_concentration': max(region_metrics, key=lambda x: x['concentration_percentage'])['region'] if region_metrics else None,
            'lowest_concentration': min(region_metrics, key=lambda x: x['concentration_percentage'])['region'] if region_metrics else None
        }
    }
    
    logger.info(f"Region comparison complete. Analyzed {len(region_metrics)} regions.")
    return result
