"""
impact_calculator.py - Calculates impacts of various supply chain scenarios

This module provides functions to calculate impacts on lead times, costs,
availability, and other metrics for different supply chain disruption scenarios.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.ImpactCalculator")

def calculate_price_impacts(affected_components: List[Dict], 
                           affected_products: List[Dict], 
                           tariff_increase: float) -> Dict:
    """
    Estimate price impacts from tariff changes.
    
    Args:
        affected_components: List of components affected by tariffs
        affected_products: List of products using affected components
        tariff_increase: Percentage increase in tariffs
        
    Returns:
        Dictionary with price impact metrics
    """
    # Estimate component price increases
    for component in affected_components:
        # Assume price increase is some fraction of tariff increase
        # depending on how much of component cost is affected by tariffs
        component['estimated_price_increase'] = round(tariff_increase * 0.4, 2)
    
    # Estimate product price increases
    total_impact = 0
    for product in affected_products:
        # Simple model: Each affected component contributes to price increase
        # with critical components having more impact
        component_impact = 0
        for component in product['affected_components']:
            # Find component in affected_components list
            for ac in affected_components:
                if ac['component_id'] == component['component_id']:
                    impact_factor = 0.5 if component['critical'] else 0.2
                    component_impact += ac['estimated_price_increase'] * impact_factor
                    break
        
        # Assume final product price increase is dampened
        product['estimated_price_increase_percentage'] = round(min(component_impact, tariff_increase), 2)
        total_impact += product['estimated_price_increase_percentage']
    
    # Calculate average impact
    avg_product_increase = round(total_impact / max(1, len(affected_products)), 2)
    
    return {
        'average_product_price_increase': avg_product_increase,
        'max_product_price_increase': max([p['estimated_price_increase_percentage'] for p in affected_products]) if affected_products else 0,
        'min_product_price_increase': min([p['estimated_price_increase_percentage'] for p in affected_products]) if affected_products else 0
    }

def estimate_lead_time_impacts(affected_components: List[Dict], 
                              affected_products: List[Dict],
                              severity_factor: float,
                              duration_factor: float) -> Dict:
    """
    Estimate lead time impacts from supplier disruption.
    
    Args:
        affected_components: List of affected components
        affected_products: List of affected products
        severity_factor: Factor representing severity of disruption (0-1)
        duration_factor: Factor representing duration of disruption (0-1)
        
    Returns:
        Dictionary with lead time impact metrics
    """
    # Base lead time increase in weeks
    base_lead_time_increase = 3 * severity_factor * duration_factor
    
    # Estimate component lead time increases
    for component in affected_components:
        # Critical components are harder to source alternatives for
        criticality_factor = 1.5 if component.get('critical', False) else 1.0
        component['estimated_lead_time_increase_weeks'] = round(base_lead_time_increase * criticality_factor, 1)
    
    # Estimate product lead time increases
    for product in affected_products:
        # Product lead time increase is driven by its most impacted critical component
        max_lead_time_increase = 0
        for component in product['affected_components']:
            # Find component in affected_components list
            for ac in affected_components:
                if ac['component_id'] == component['component_id']:
                    if component.get('critical', False) and ac.get('estimated_lead_time_increase_weeks', 0) > max_lead_time_increase:
                        max_lead_time_increase = ac.get('estimated_lead_time_increase_weeks', 0)
        
        product['estimated_lead_time_increase_weeks'] = max_lead_time_increase
    
    # Calculate average impact
    avg_product_lead_time = round(sum(p.get('estimated_lead_time_increase_weeks', 0) for p in affected_products) / max(1, len(affected_products)), 1)
    
    return {
        'average_lead_time_increase_weeks': avg_product_lead_time,
        'max_lead_time_increase_weeks': max([p.get('estimated_lead_time_increase_weeks', 0) for p in affected_products]) if affected_products else 0,
        'estimated_recovery_time_months': round(duration_factor * 12)
    }

def calculate_product_impacts(affected_products: List[Dict],
                             affected_components: List[Dict],
                             event_factors: Dict,
                             severity_factor: float) -> Dict:
    """
    Calculate product impacts from a geopolitical event.
    
    Args:
        affected_products: List of affected products
        affected_components: List of affected components
        event_factors: Dictionary with impact factors for different aspects
        severity_factor: Factor representing severity of event (0-1)
        
    Returns:
        Dictionary with impact metrics
    """
    for product in affected_products:
        # Initialize impact values
        lead_time_increase = 0
        availability_decrease = 0
        cost_increase = 0
        critical_count = 0
        
        # Calculate impact based on affected components
        for component in product['affected_components']:
            component_id = component['component_id']
            
            # Find component in affected_components list
            for ac in affected_components:
                if ac['component_id'] == component_id:
                    # Critical components have higher impact
                    impact_multiplier = 1.5 if component.get('critical', False) else 1.0
                    
                    lead_time_increase += ac.get('lead_time_impact', 0) * impact_multiplier
                    availability_decrease += ac.get('availability_impact', 0) * impact_multiplier
                    cost_increase += ac.get('cost_impact', 0) * impact_multiplier
                    
                    if component.get('critical', False):
                        critical_count += 1
        
        # Normalize impacts based on number of components
        component_count = max(1, len(product['affected_components']))
        product['lead_time_increase_weeks'] = round(lead_time_increase / component_count, 1)
        product['availability_decrease_percent'] = round(min(availability_decrease / component_count, 100), 1)
        product['cost_increase_percent'] = round(cost_increase / component_count, 1)
        product['critical_components_affected'] = critical_count
    
    # Calculate averages across all products
    if affected_products:
        avg_lead_time = sum(p.get('lead_time_increase_weeks', 0) for p in affected_products) / len(affected_products)
        avg_availability = sum(p.get('availability_decrease_percent', 0) for p in affected_products) / len(affected_products)
        avg_cost = sum(p.get('cost_increase_percent', 0) for p in affected_products) / len(affected_products)
    else:
        avg_lead_time = 0
        avg_availability = 0
        avg_cost = 0
    
    return {
        'average_lead_time_increase': round(avg_lead_time, 1),
        'average_availability_decrease': round(avg_availability, 1),
        'average_cost_increase': round(avg_cost, 1),
        'max_lead_time_increase': max([p.get('lead_time_increase_weeks', 0) for p in affected_products]) if affected_products else 0,
        'max_availability_decrease': max([p.get('availability_decrease_percent', 0) for p in affected_products]) if affected_products else 0,
        'max_cost_increase': max([p.get('cost_increase_percent', 0) for p in affected_products]) if affected_products else 0
    }

def determine_overall_impact(new_resilience: float, base_resilience: float, product_impacts: Dict) -> str:
    """
    Determine overall impact level based on various metrics.
    
    Args:
        new_resilience: New resilience score after scenario
        base_resilience: Original baseline resilience score
        product_impacts: Dictionary with product impact metrics
        
    Returns:
        Impact level as string ('low', 'medium', or 'high')
    """
    resilience_drop = base_resilience - new_resilience
    
    # High impact criteria
    if (resilience_drop > 15 or 
        product_impacts['average_lead_time_increase'] > 8 or
        product_impacts['average_availability_decrease'] > 40 or
        product_impacts['average_cost_increase'] > 20):
        return 'high'
    
    # Medium impact criteria
    elif (resilience_drop > 7 or 
          product_impacts['average_lead_time_increase'] > 4 or
          product_impacts['average_availability_decrease'] > 20 or
          product_impacts['average_cost_increase'] > 10):
        return 'medium'
    
    # Low impact
    else:
        return 'low'

def calculate_shortage_product_impacts(affected_products: List[Dict], 
                                      affected_components: List[Dict]) -> Dict:
    """
    Calculate product impacts from component shortage.
    
    Args:
        affected_products: List of affected products
        affected_components: List of affected components
        
    Returns:
        Dictionary with impact metrics
    """
    for product in affected_products:
        # Initialize impact values
        lead_time_increase = 0
        price_increase = 0
        allocation_reduction = 0
        critical_count = 0
        
        # Calculate impact based on affected components
        component_count = 0
        for component in product['affected_components']:
            component_id = component['component_id']
            
            # Find component in affected_components list
            for ac in affected_components:
                if ac['component_id'] == component_id:
                    component_count += 1
                    
                    # Critical components have higher impact
                    impact_multiplier = 1.5 if component.get('critical', False) else 1.0
                    
                    lead_time_increase += ac.get('lead_time_increase_weeks', 0) * impact_multiplier
                    price_increase += ac.get('price_increase_percent', 0) * impact_multiplier
                    allocation_reduction += ac.get('allocation_reduction_percent', 0) * impact_multiplier
                    
                    if component.get('critical', False):
                        critical_count += 1
        
        # Calculate average impacts
        if component_count > 0:
            product['lead_time_increase_weeks'] = round(lead_time_increase / component_count, 1)
            product['price_increase_percent'] = round(price_increase / component_count, 1)
            product['allocation_reduction_percent'] = round(allocation_reduction / component_count, 1)
        else:
            product['lead_time_increase_weeks'] = 0
            product['price_increase_percent'] = 0
            product['allocation_reduction_percent'] = 0
            
        product['critical_components_affected'] = critical_count
    
    # Calculate averages across all products
    if affected_products:
        avg_lead_time = sum(p.get('lead_time_increase_weeks', 0) for p in affected_products) / len(affected_products)
        avg_price_increase = sum(p.get('price_increase_percent', 0) for p in affected_products) / len(affected_products)
        avg_allocation = sum(p.get('allocation_reduction_percent', 0) for p in affected_products) / len(affected_products)
    else:
        avg_lead_time = 0
        avg_price_increase = 0
        avg_allocation = 0
    
    return {
        'average_lead_time_increase': round(avg_lead_time, 1),
        'average_price_increase': round(avg_price_increase, 1),
        'average_allocation_reduction': round(avg_allocation, 1),
        'max_lead_time_increase': max([p.get('lead_time_increase_weeks', 0) for p in affected_products]) if affected_products else 0,
        'max_price_increase': max([p.get('price_increase_percent', 0) for p in affected_products]) if affected_products else 0,
        'max_allocation_reduction': max([p.get('allocation_reduction_percent', 0) for p in affected_products]) if affected_products else 0
    }
