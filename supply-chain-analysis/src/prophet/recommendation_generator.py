"""
recommendation_generator.py - Generates strategic recommendations

This module provides functions to generate tailored recommendations
for various supply chain disruption scenarios.
"""

import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.RecommendationGenerator")

def generate_tariff_recommendations(affected_components: List[Dict], 
                                  affected_products: List[Dict]) -> List[Dict]:
    """
    Generate recommendations for tariff changes.
    
    Args:
        affected_components: List of components affected by tariffs
        affected_products: List of products using affected components
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Recommendation 1: Source from different countries
    if affected_components:
        most_affected = max(affected_components, key=lambda x: x.get('estimated_price_increase', 0))
        recommendations.append({
            'action': 'relocate_sourcing',
            'description': f"Consider sourcing {most_affected['component_name']} and similar components from countries not affected by the tariff",
            'priority': 'high',
            'estimated_benefit': 'Eliminate direct tariff impact on affected components',
            'implementation_difficulty': 'medium',
            'timeframe': 'medium_term'
        })
    
    # Recommendation 2: Absorb costs strategically
    if affected_products:
        high_impact_products = [p for p in affected_products if p.get('estimated_price_increase_percentage', 0) > 2]
        if high_impact_products:
            recommendations.append({
                'action': 'strategic_pricing',
                'description': f"Adjust pricing strategy for {len(high_impact_products)} high-impact products to maintain market competitiveness",
                'priority': 'high',
                'estimated_benefit': 'Maintain market share while minimizing profit impact',
                'implementation_difficulty': 'low',
                'timeframe': 'immediate'
            })
    
    # Recommendation 3: Pursue tariff exemptions
    recommendations.append({
        'action': 'tariff_exemptions',
        'description': "Pursue possible tariff exemptions or exclusions for critical components",
        'priority': 'medium',
        'estimated_benefit': 'Potential significant savings on affected components',
        'implementation_difficulty': 'high',
        'timeframe': 'medium_term'
    })
    
    # Recommendation 4: Redesign products
    highly_affected_criticals = [c for c in affected_components 
                                 if c.get('estimated_price_increase', 0) > 3 
                                 and any(p.get('critical', False) for p in affected_products 
                                        if c['component_id'] in [ac.get('component_id') for ac in p.get('affected_components', [])])]
    
    if highly_affected_criticals:
        recommendations.append({
            'action': 'product_redesign',
            'description': "Evaluate product redesign to reduce dependency on heavily tariffed components",
            'priority': 'medium',
            'estimated_benefit': 'Long-term resilience to similar tariff actions',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    return recommendations

def generate_disruption_recommendations(supplier_id: str,
                                       affected_components: List[Dict],
                                       affected_products: List[Dict],
                                       disruption_level: str,
                                       duration_months: int) -> List[Dict]:
    """
    Generate recommendations for supplier disruptions.
    
    Args:
        supplier_id: ID of the affected supplier
        affected_components: List of affected components
        affected_products: List of affected products
        disruption_level: Level of disruption ('partial' or 'complete')
        duration_months: Duration of disruption in months
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Recommendation 1: Find alternative suppliers
    if affected_components:
        critical_components = [c for c in affected_components if c.get('critical', False)]
        
        if critical_components:
            recommendations.append({
                'action': 'alternative_suppliers',
                'description': f"Immediately identify alternative suppliers for {len(critical_components)} critical components",
                'priority': 'high',
                'estimated_benefit': 'Maintain production capability for critical products',
                'implementation_difficulty': 'medium',
                'timeframe': 'immediate'
            })
        else:
            recommendations.append({
                'action': 'alternative_suppliers',
                'description': "Identify alternative suppliers for affected components",
                'priority': 'medium',
                'estimated_benefit': 'Ensure continued component availability',
                'implementation_difficulty': 'medium',
                'timeframe': 'short_term'
            })
    
    # Recommendation 2: Inventory management
    recommendations.append({
        'action': 'inventory_strategy',
        'description': "Review and adjust inventory levels for affected components",
        'priority': 'high',
        'estimated_benefit': 'Buffer against short-term disruption',
        'implementation_difficulty': 'low',
        'timeframe': 'immediate'
    })
    
    # Recommendation 3: Production schedule adjustment
    if disruption_level == 'complete' and duration_months > 1:
        recommendations.append({
            'action': 'production_adjustment',
            'description': "Temporarily adjust production schedules for affected products",
            'priority': 'high',
            'estimated_benefit': 'Optimize production based on component availability',
            'implementation_difficulty': 'medium',
            'timeframe': 'immediate'
        })
    
    # Recommendation 4: Long-term supplier diversification
    if disruption_level == 'complete' and duration_months > 3:
        recommendations.append({
            'action': 'supplier_diversification',
            'description': "Implement long-term supplier diversification strategy",
            'priority': 'medium',
            'estimated_benefit': 'Enhanced resilience against future disruptions',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    # Recommendation 5: Customer communication
    if affected_products:
        high_impact_products = [p for p in affected_products 
                               if p.get('critical_components_count', 0) > 0 
                               and p.get('estimated_lead_time_increase_weeks', 0) > 2]
        
        if high_impact_products:
            recommendations.append({
                'action': 'customer_communication',
                'description': "Proactively communicate with customers about potential delays",
                'priority': 'high',
                'estimated_benefit': 'Maintain customer relationships despite disruption',
                'implementation_difficulty': 'low',
                'timeframe': 'immediate'
            })
    
    return recommendations

def generate_geopolitical_recommendations(country: str,
                                        event_type: str,
                                        severity: str,
                                        duration_months: int,
                                        affected_components: List[Dict],
                                        affected_products: List[Dict]) -> List[Dict]:
    """
    Generate recommendations for geopolitical events.
    
    Args:
        country: Affected country
        event_type: Type of event ('trade_restriction', 'conflict', 'natural_disaster', 'political_change')
        severity: Level of severity ('low', 'medium', or 'high')
        duration_months: Duration of impact in months
        affected_components: List of affected components
        affected_products: List of affected products
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Recommendation 1: Short-term sourcing adjustments
    if affected_components:
        critical_components = [c for c in affected_components if c.get('critical', False)]
        
        if critical_components:
            recommendations.append({
                'action': 'alternative_sourcing',
                'description': f"Immediately secure alternative sources for {len(critical_components)} critical components from {country}",
                'priority': 'high',
                'estimated_benefit': 'Maintain production of critical products',
                'implementation_difficulty': 'high' if severity == 'high' else 'medium',
                'timeframe': 'immediate'
            })
    
    # Recommendation 2: Inventory buffer
    if event_type in ['trade_restriction', 'conflict'] and severity in ['medium', 'high']:
        recommendations.append({
            'action': 'inventory_buffer',
            'description': f"Increase safety stock levels for components sourced from {country}",
            'priority': 'high',
            'estimated_benefit': 'Buffer against supply disruptions',
            'implementation_difficulty': 'medium',
            'timeframe': 'immediate'
        })
    
    # Recommendation 3: Production adjustments
    if severity == 'high' and affected_products:
        recommendations.append({
            'action': 'production_prioritization',
            'description': "Prioritize production of high-margin and strategic products",
            'priority': 'high',
            'estimated_benefit': 'Optimize limited component availability',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    # Recommendation 4: Geographic diversification
    if duration_months > 6 or severity == 'high':
        recommendations.append({
            'action': 'geographic_diversification',
            'description': f"Develop long-term strategy to reduce dependency on {country} for critical components",
            'priority': 'medium',
            'estimated_benefit': 'Long-term supply chain resilience',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    # Recommendation 5: Event-specific strategy
    if event_type == 'trade_restriction':
        recommendations.append({
            'action': 'trade_compliance',
            'description': "Engage with trade compliance experts to navigate new restrictions",
            'priority': 'high',
            'estimated_benefit': 'Ensure regulatory compliance while minimizing disruption',
            'implementation_difficulty': 'medium',
            'timeframe': 'immediate'
        })
    elif event_type == 'conflict':
        recommendations.append({
            'action': 'logistics_rerouting',
            'description': "Develop alternative logistics routes to avoid conflict zones",
            'priority': 'high',
            'estimated_benefit': 'Maintain supply chain continuity',
            'implementation_difficulty': 'high',
            'timeframe': 'immediate'
        })
    elif event_type == 'natural_disaster':
        recommendations.append({
            'action': 'supplier_recovery',
            'description': "Provide support to key suppliers for faster recovery",
            'priority': 'medium',
            'estimated_benefit': 'Accelerate supply chain recovery',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    return recommendations

def generate_shortage_recommendations(component_type: str,
                                     shortage_level: str,
                                     duration_months: int,
                                     affected_components: List[Dict],
                                     affected_products: List[Dict]) -> List[Dict]:
    """
    Generate recommendations for component shortages.
    
    Args:
        component_type: Type of component experiencing shortage
        shortage_level: Level of shortage ('moderate' or 'severe')
        duration_months: Duration of shortage in months
        affected_components: List of affected components
        affected_products: List of affected products
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Recommendation 1: Allocation strategy
    recommendations.append({
        'action': 'allocation_strategy',
        'description': f"Develop a strategic allocation plan for limited {component_type} supply",
        'priority': 'high',
        'estimated_benefit': 'Optimize use of limited components for highest value products',
        'implementation_difficulty': 'medium',
        'timeframe': 'immediate'
    })
    
    # Recommendation 2: Alternative components
    critical_components = [c for c in affected_components if c.get('critical', False)]
    if critical_components:
        recommendations.append({
            'action': 'alternative_components',
            'description': f"Identify and qualify alternative {component_type} components",
            'priority': 'high',
            'estimated_benefit': 'Enable continued production despite shortage',
            'implementation_difficulty': 'high',
            'timeframe': 'short_term'
        })
    
    # Recommendation 3: Pricing strategy
    if shortage_level == 'severe':
        recommendations.append({
            'action': 'pricing_strategy',
            'description': "Adjust pricing strategy for products affected by shortage",
            'priority': 'medium',
            'estimated_benefit': 'Maintain margins despite component cost increases',
            'implementation_difficulty': 'medium',
            'timeframe': 'immediate'
        })
    
    # Recommendation 4: Long-term supply agreements
    if duration_months > 3:
        recommendations.append({
            'action': 'supply_agreements',
            'description': f"Negotiate long-term supply agreements for {component_type} components",
            'priority': 'high',
            'estimated_benefit': 'Secure priority access to limited component supply',
            'implementation_difficulty': 'high',
            'timeframe': 'medium_term'
        })
    
    # Recommendation 5: Product redesign for critical products
    high_impact_products = [p for p in affected_products 
                           if p.get('allocation_reduction_percent', 0) > 30
                           and p.get('critical_components_affected', 0) > 0]
    
    if high_impact_products and duration_months > 6:
        recommendations.append({
            'action': 'product_redesign',
            'description': f"Evaluate redesign options to reduce dependency on {component_type} components",
            'priority': 'medium',
            'estimated_benefit': 'Long-term resilience to similar shortages',
            'implementation_difficulty': 'very_high',
            'timeframe': 'long_term'
        })
    
    # Recommendation 6: Customer communication
    recommendations.append({
        'action': 'customer_communication',
        'description': "Develop a communication plan regarding potential product delays",
        'priority': 'high',
        'estimated_benefit': 'Set appropriate expectations and maintain customer trust',
        'implementation_difficulty': 'low',
        'timeframe': 'immediate'
    })
    
    return recommendations

def generate_optimization_recommendations(resilience_analysis: Dict) -> List[Dict]:
    """
    Generate recommendations for general supply chain optimization.
    
    Args:
        resilience_analysis: Dictionary with resilience analysis data
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Extract key metrics from resilience analysis
    factors = resilience_analysis.get('factors', {})
    metrics = resilience_analysis.get('metrics', {})
    
    # Recommendation 1: Supplier diversification
    if factors.get('supplier_diversity', {}).get('score', 100) < 70:
        recommendations.append({
            'action': 'supplier_diversification',
            'description': "Develop secondary suppliers for components with single sources",
            'priority': 'high',
            'estimated_benefit': 'Reduced risk of supplier disruptions',
            'implementation_difficulty': 'medium',
            'timeframe': 'medium_term'
        })
    
    # Recommendation 2: Geographical diversification
    if factors.get('geographical_diversity', {}).get('score', 100) < 60:
        recommendations.append({
            'action': 'geographical_diversification',
            'description': "Reduce dependency on components from high-concentration regions",
            'priority': 'medium',
            'estimated_benefit': 'Reduced exposure to regional disruptions',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    # Recommendation 3: Critical component strategy
    critical_count = metrics.get('critical_components', 0)
    if critical_count > 0:
        recommendations.append({
            'action': 'critical_component_strategy',
            'description': f"Develop specific risk mitigation strategies for {critical_count} critical components",
            'priority': 'high',
            'estimated_benefit': 'Increased resilience for highest-risk components',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    # Recommendation 4: Inventory optimization
    recommendations.append({
        'action': 'inventory_optimization',
        'description': "Optimize inventory levels based on component criticality and lead times",
        'priority': 'medium',
        'estimated_benefit': 'Balance between cost efficiency and supply risk',
        'implementation_difficulty': 'medium',
        'timeframe': 'short_term'
    })
    
    # Recommendation 5: Supply chain visibility
    recommendations.append({
        'action': 'supply_chain_visibility',
        'description': "Implement enhanced visibility tools for real-time supply chain monitoring",
        'priority': 'medium',
        'estimated_benefit': 'Earlier detection of emerging supply risks',
        'implementation_difficulty': 'high',
        'timeframe': 'medium_term'
    })
    
    # Recommendation 6: Alternative materials and designs
    if factors.get('component_criticality', {}).get('score', 100) < 60:
        recommendations.append({
            'action': 'alternative_designs',
            'description': "Research alternative materials and designs for high-risk components",
            'priority': 'medium',
            'estimated_benefit': 'Increased design flexibility during disruptions',
            'implementation_difficulty': 'high',
            'timeframe': 'long_term'
        })
    
    return recommendations

def generate_custom_recommendations(custom_factors: Dict) -> List[Dict]:
    """
    Generate custom recommendations based on user-defined factors.
    
    Args:
        custom_factors: Dictionary with custom risk factors and weights
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Check which factors are present and meet thresholds
    if custom_factors.get('tariff_risk', 0) > 0.7:
        recommendations.append({
            'action': 'tariff_mitigation',
            'description': "Develop a comprehensive tariff mitigation strategy",
            'priority': 'high',
            'estimated_benefit': 'Reduced tariff exposure',
            'implementation_difficulty': 'high',
            'timeframe': 'medium_term'
        })
    
    if custom_factors.get('supplier_risk', 0) > 0.6:
        recommendations.append({
            'action': 'supplier_strategy',
            'description': "Create a supplier risk management program",
            'priority': 'high' if custom_factors.get('supplier_risk', 0) > 0.8 else 'medium',
            'estimated_benefit': 'More reliable supplier network',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    if custom_factors.get('geopolitical_risk', 0) > 0.5:
        recommendations.append({
            'action': 'geopolitical_monitoring',
            'description': "Implement a geopolitical risk monitoring system",
            'priority': 'medium',
            'estimated_benefit': 'Earlier warning of geopolitical disruptions',
            'implementation_difficulty': 'medium',
            'timeframe': 'short_term'
        })
    
    if custom_factors.get('shortage_risk', 0) > 0.6:
        recommendations.append({
            'action': 'shortage_preparation',
            'description': "Prepare contingency plans for component shortages",
            'priority': 'medium',
            'estimated_benefit': 'Faster response to shortages',
            'implementation_difficulty': 'medium',
            'timeframe': 'medium_term'
        })
    
    # Add general recommendations regardless of factors
    recommendations.append({
        'action': 'resilience_program',
        'description': "Establish a dedicated supply chain resilience program",
        'priority': 'high' if sum(custom_factors.values()) / max(1, len(custom_factors)) > 0.7 else 'medium',
        'estimated_benefit': 'Holistic improvement in supply chain resilience',
        'implementation_difficulty': 'high',
        'timeframe': 'medium_term'
    })
    
    return recommendations

def prioritize_recommendations(recommendations: List[Dict], focus_area: str = None) -> List[Dict]:
    """
    Prioritize recommendations based on specified focus area.
    
    Args:
        recommendations: List of recommendation dictionaries
        focus_area: Optional focus area ('cost', 'speed', 'resilience', 'compliance')
        
    Returns:
        List of prioritized recommendation dictionaries
    """
    if not focus_area:
        # Default prioritization - already sorted by priority
        return recommendations
    
    # Define focus area weights for different recommendation actions
    focus_weights = {
        'cost': {
            'strategic_pricing': 2.0,
            'inventory_optimization': 1.8,
            'tariff_exemptions': 1.7,
            'production_adjustment': 1.5,
            'allocation_strategy': 1.5,
            'pricing_strategy': 1.5
        },
        'speed': {
            'customer_communication': 2.0,
            'alternative_suppliers': 1.8,
            'inventory_strategy': 1.7,
            'logistics_rerouting': 1.6,
            'production_prioritization': 1.5
        },
        'resilience': {
            'supplier_diversification': 2.0,
            'geographical_diversification': 1.9,
            'critical_component_strategy': 1.8,
            'alternative_components': 1.7,
            'compound_strategy': 1.6
        },
        'compliance': {
            'trade_compliance': 2.0,
            'tariff_exemptions': 1.8,
            'supply_chain_visibility': 1.5,
            'geopolitical_monitoring': 1.5
        }
    }
    
    # Get weights for the selected focus area
    weights = focus_weights.get(focus_area.lower(), {})
    
    # Apply weights to recommendations
    weighted_recommendations = []
    for rec in recommendations:
        action = rec.get('action', '')
        
        # Get the weight for this action (default to 1.0 if not found)
        weight = weights.get(action, 1.0)
        
        # Create a copy of the recommendation with a weight attribute
        weighted_rec = rec.copy()
        weighted_rec['weight'] = weight
        
        weighted_recommendations.append(weighted_rec)
    
    # Sort by priority and then by weight
    priority_map = {'high': 0, 'medium': 1, 'low': 2}
    weighted_recommendations.sort(key=lambda x: (priority_map.get(x.get('priority', 'low'), 3), -x.get('weight', 1.0)))
    
    # Remove the weight attribute
    for rec in weighted_recommendations:
        if 'weight' in rec:
            del rec['weight']
    
    return weighted_recommendations
