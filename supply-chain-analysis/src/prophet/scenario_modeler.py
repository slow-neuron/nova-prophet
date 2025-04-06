"""
scenario_modeler.py - Models different supply chain scenarios

This module handles the creation and simulation of various supply chain scenarios
such as tariff changes, supplier disruptions, geopolitical events, and component shortages.
"""

import networkx as nx
import logging
import copy
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import utility functions
from prophet.utils import find_affected_products, get_component_countries
from prophet.impact_calculator import calculate_price_impacts, estimate_lead_time_impacts
from prophet.recommendation_generator import generate_tariff_recommendations, generate_disruption_recommendations

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.ScenarioModeler")

class ScenarioModeler:
    """
    Models different supply chain scenarios by simulating changes and disruptions.
    """
    
    def __init__(self, graph, analyzer=None):
        """
        Initialize the scenario modeler with a NetworkX graph.
        
        Args:
            graph: NetworkX DiGraph object representing the supply chain
            analyzer: Optional SupplyChainAnalyzer instance (will be imported if None)
        """
        self.original_graph = graph
        self.graph = copy.deepcopy(graph)  # Work with a copy to avoid modifying original
        
        # Import the analyzer here to avoid circular imports
        if analyzer is None:
            from veritas import SupplyChainAnalyzer
            self.analyzer = SupplyChainAnalyzer(self.graph)
        else:
            self.analyzer = analyzer
            
        self.base_resilience = self.analyzer.calculate_resilience_score()
        logger.info(f"Initialized ScenarioModeler with graph containing {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        logger.info(f"Base resilience score: {self.base_resilience['total_resilience_score']}/100")
    
    def reset_scenario(self):
        """Reset the graph to its original state."""
        self.graph = copy.deepcopy(self.original_graph)
        
        # Reinitialize the analyzer with the fresh graph
        from veritas import SupplyChainAnalyzer
        self.analyzer = SupplyChainAnalyzer(self.graph)
        
        logger.info("Reset scenario to original state")
    
    def model_tariff_change(self, country: str, increase_percentage: float, 
                            affected_component_types: List[str] = None) -> Dict:
        """
        Model the impact of tariff changes from a specific country.
        
        Args:
            country: Country implementing the tariff change
            increase_percentage: Percentage increase in tariffs
            affected_component_types: Optional list of component types affected
            
        Returns:
            Dictionary with impact analysis
        """
        logger.info(f"Modeling tariff change: {increase_percentage}% increase from {country}")
        
        # Start with a fresh graph
        self.reset_scenario()
        
        # Format country_id
        country_id = f"country_{country.lower().replace(' ', '_')}"
        
        # Find components originating from this country
        affected_components = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component':
                # Check if component is from affected country
                component_countries = self._get_component_countries(node_id)
                
                if country in component_countries:
                    # Check if component type is in affected types
                    component_type = node_data.get('category', 'unknown')
                    if affected_component_types is None or component_type in affected_component_types:
                        # Mark as tariff vulnerable
                        self.graph.nodes[node_id]['tariff_vulnerable'] = True
                        
                        # Record affected component
                        affected_components.append({
                            'component_id': node_id,
                            'component_name': node_data.get('name', 'Unknown'),
                            'tariff_increase': increase_percentage,
                            'component_type': component_type
                        })
        
        logger.info(f"Found {len(affected_components)} components affected by tariff change")
        
        # Analyze impact
        if affected_components:
            # Get new resilience score
            new_resilience = self.analyzer.calculate_resilience_score()
            
            # Calculate impact on products
            affected_products = self._find_affected_products(affected_components)
            
            # Estimate price impacts
            price_impacts = calculate_price_impacts(affected_components, affected_products, increase_percentage)
            
            # Generate recommendations
            recommendations = generate_tariff_recommendations(affected_components, affected_products)
            
            result = {
                'scenario_type': 'tariff_change',
                'country': country,
                'increase_percentage': increase_percentage,
                'affected_components': affected_components,
                'affected_products_count': len(affected_products),
                'affected_products': affected_products[:10] if len(affected_products) > 10 else affected_products,
                'resilience_impact': {
                    'before': self.base_resilience['total_resilience_score'],
                    'after': new_resilience['total_resilience_score'],
                    'change': round(new_resilience['total_resilience_score'] - self.base_resilience['total_resilience_score'], 2)
                },
                'price_impacts': price_impacts,
                'recommendations': recommendations
            }
        else:
            result = {
                'scenario_type': 'tariff_change',
                'country': country,
                'increase_percentage': increase_percentage,
                'affected_components': [],
                'affected_products_count': 0,
                'affected_products': [],
                'resilience_impact': {
                    'before': self.base_resilience['total_resilience_score'],
                    'after': self.base_resilience['total_resilience_score'],
                    'change': 0
                },
                'price_impacts': {'average_product_price_increase': 0},
                'recommendations': []
            }
        
        return result
    
    def model_supplier_disruption(self, supplier_id: str, disruption_level: str, 
                                 duration_months: int) -> Dict:
        """
        Model the impact of a supplier disruption.
        
        Args:
            supplier_id: ID of the affected supplier
            disruption_level: 'partial' or 'complete'
            duration_months: Duration of disruption in months
            
        Returns:
            Dictionary with impact analysis
        """
        logger.info(f"Modeling {disruption_level} supplier disruption for {supplier_id} lasting {duration_months} months")
        
        # Start with a fresh graph
        self.reset_scenario()
        
        if supplier_id not in self.graph:
            logger.warning(f"Supplier {supplier_id} not found in graph")
            return {
                'scenario_type': 'supplier_disruption',
                'supplier': 'Unknown',
                'disruption_level': disruption_level,
                'duration_months': duration_months,
                'affected_components': [],
                'affected_products': [],
                'impact_assessment': 'Supplier not found in graph'
            }
        
        supplier_name = self.graph.nodes[supplier_id].get('name', 'Unknown')
        
        # Find components supplied by this supplier
        affected_components = []
        for _, target, edge_data in self.graph.out_edges(supplier_id, data=True):
            if edge_data.get('relationship_type') == 'SUPPLIES':
                component_id = target
                component_data = self.graph.nodes[component_id]
                
                # Add to affected components
                affected_components.append({
                    'component_id': component_id,
                    'component_name': component_data.get('name', 'Unknown'),
                    'critical': component_data.get('critical', False)
                })
        
        logger.info(f"Found {len(affected_components)} components supplied by {supplier_name}")
        
        # Find products using these components
        affected_products = self._find_affected_products(affected_components)
        
        # Calculate impact severity
        severity_factor = 1.0 if disruption_level == 'complete' else 0.6
        duration_factor = min(1.0, duration_months / 12)  # Cap at 1.0 for durations longer than a year
        
        # Temporarily modify graph to simulate disruption
        for component in affected_components:
            component_id = component['component_id']
            
            # Simulate disruption by marking components as unavailable
            if disruption_level == 'complete':
                # Remove supply relationship
                if self.graph.has_edge(supplier_id, component_id):
                    self.graph.remove_edge(supplier_id, component_id)
            else:
                # Mark as constrained
                self.graph.nodes[component_id]['supply_constrained'] = True
        
        # Get new resilience score
        new_resilience = self.analyzer.calculate_resilience_score()
        
        # Calculate lead time impacts
        lead_time_impacts = estimate_lead_time_impacts(affected_components, affected_products, 
                                                      severity_factor, duration_factor)
        
        # Generate recommendations
        recommendations = generate_disruption_recommendations(supplier_id, affected_components, 
                                                           affected_products, disruption_level, 
                                                           duration_months)
        
        result = {
            'scenario_type': 'supplier_disruption',
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'disruption_level': disruption_level,
            'duration_months': duration_months,
            'affected_components_count': len(affected_components),
            'affected_components': affected_components,
            'affected_products_count': len(affected_products),
            'affected_products': affected_products[:10] if len(affected_products) > 10 else affected_products,
            'resilience_impact': {
                'before': self.base_resilience['total_resilience_score'],
                'after': new_resilience['total_resilience_score'],
                'change': round(new_resilience['total_resilience_score'] - self.base_resilience['total_resilience_score'], 2)
            },
            'lead_time_impacts': lead_time_impacts,
            'recommendations': recommendations
        }
        
        return result
    
    def model_geopolitical_event(self, country: str, event_type: str,
                               severity: str, duration_months: int) -> Dict:
        """
        Model the impact of a geopolitical event in a specific country.
        
        Args:
            country: Affected country
            event_type: Type of event ('trade_restriction', 'conflict', 'natural_disaster', 'political_change')
            severity: 'low', 'medium', or 'high'
            duration_months: Duration of impact in months
            
        Returns:
            Dictionary with impact analysis
        """
        # Import here to avoid circular imports
        from prophet.geopolitical_modeler import model_geopolitical_event
        
        return model_geopolitical_event(
            graph=self.graph,
            analyzer=self.analyzer,
            country=country,
            event_type=event_type,
            severity=severity,
            duration_months=duration_months
        )
    
    def model_component_shortage(self, component_type: str, shortage_level: str,
                               duration_months: int) -> Dict:
        """
        Model the impact of a global component shortage.
        
        Args:
            component_type: Type of component experiencing shortage
            shortage_level: 'moderate' or 'severe'
            duration_months: Duration of shortage in months
            
        Returns:
            Dictionary with impact analysis
        """
        # Import here to avoid circular imports
        from prophet.shortage_modeler import model_component_shortage
        
        return model_component_shortage(
            graph=self.graph,
            analyzer=self.analyzer,
            component_type=component_type,
            shortage_level=shortage_level,
            duration_months=duration_months
        )
    
    def _get_component_countries(self, component_id: str) -> List[str]:
        """Get countries associated with a component."""
        countries = []
        for source, target, edge_data in self.graph.out_edges(component_id, data=True):
            if edge_data.get('relationship_type') == 'ORIGINATES_FROM' and self.graph.nodes[target].get('node_type') == 'country':
                countries.append(self.graph.nodes[target].get('name', 'Unknown'))
        return countries
    
    def _find_affected_products(self, affected_components: List[Dict]) -> List[Dict]:
        """Find products affected by component changes."""
        return find_affected_products(self.graph, affected_components)
    
    def combine_scenarios(self, scenarios: List[Dict]) -> Dict:
        """
        Combine multiple scenarios to model compound disruptions.
        
        Args:
            scenarios: List of scenario result dictionaries
            
        Returns:
            Dictionary with combined impact analysis
        """
        logger.info(f"Combining {len(scenarios)} scenarios for compound analysis")
        
        # Start with a fresh graph
        self.reset_scenario()
        
        # Apply all scenario modifications to the graph
        for scenario in scenarios:
            scenario_type = scenario.get('scenario_type')
            
            if scenario_type == 'tariff_change':
                # Mark components as tariff vulnerable
                for component in scenario.get('affected_components', []):
                    component_id = component.get('component_id')
                    if component_id in self.graph:
                        self.graph.nodes[component_id]['tariff_vulnerable'] = True
            
            elif scenario_type == 'supplier_disruption':
                supplier_id = scenario.get('supplier_id')
                disruption_level = scenario.get('disruption_level')
                
                # Apply supplier disruption impacts
                for component in scenario.get('affected_components', []):
                    component_id = component.get('component_id')
                    
                    if disruption_level == 'complete' and self.graph.has_edge(supplier_id, component_id):
                        self.graph.remove_edge(supplier_id, component_id)
                    elif component_id in self.graph:
                        self.graph.nodes[component_id]['supply_constrained'] = True
            
            elif scenario_type == 'geopolitical_event':
                # Mark components as affected by geopolitical event
                for component in scenario.get('affected_components', []):
                    component_id = component.get('component_id')
                    if component_id in self.graph:
                        self.graph.nodes[component_id]['affected_by_event'] = True
                        self.graph.nodes[component_id]['event_impact_level'] = scenario.get('severity', 'medium')
            
            elif scenario_type == 'component_shortage':
                # Mark components as affected by shortage
                for component in scenario.get('affected_components', []):
                    component_id = component.get('component_id')
                    if component_id in self.graph:
                        self.graph.nodes[component_id]['affected_by_shortage'] = True
                        self.graph.nodes[component_id]['shortage_level'] = scenario.get('shortage_level', 'moderate')
        
        # Collect all affected components
        affected_components = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if (node_data.get('node_type') == 'component' and
                (node_data.get('tariff_vulnerable', False) or
                 node_data.get('supply_constrained', False) or
                 node_data.get('affected_by_event', False) or
                 node_data.get('affected_by_shortage', False))):
                
                affected_components.append({
                    'component_id': node_id,
                    'component_name': node_data.get('name', 'Unknown'),
                    'critical': node_data.get('critical', False),
                    'impact_sources': self._get_component_impact_sources(node_data)
                })
        
        # Find products using these components
        affected_products = self._find_affected_products(affected_components)
        
        # Get new resilience score
        new_resilience = self.analyzer.calculate_resilience_score()
        
        # Generate compound recommendations
        recommendations = self._generate_compound_recommendations(scenarios, affected_components, affected_products)
        
        result = {
            'scenario_type': 'compound',
            'scenarios_combined': len(scenarios),
            'scenario_types': [s.get('scenario_type') for s in scenarios],
            'affected_components_count': len(affected_components),
            'affected_components': affected_components[:15] if len(affected_components) > 15 else affected_components,
            'affected_products_count': len(affected_products),
            'affected_products': affected_products[:10] if len(affected_products) > 10 else affected_products,
            'resilience_impact': {
                'before': self.base_resilience['total_resilience_score'],
                'after': new_resilience['total_resilience_score'],
                'change': round(new_resilience['total_resilience_score'] - self.base_resilience['total_resilience_score'], 2)
            },
            'impact_assessment': {
                'severity': 'high' if (new_resilience['total_resilience_score'] - self.base_resilience['total_resilience_score']) < -15 else 'medium'
            },
            'recommendations': recommendations
        }
        
        logger.info(f"Completed compound scenario analysis with {len(affected_components)} affected components")
        return result
    
    def _get_component_impact_sources(self, node_data: Dict) -> List[str]:
        """
        Get the impact sources for a component.
        
        Args:
            node_data: Component node data
            
        Returns:
            List of impact source descriptions
        """
        sources = []
        
        if node_data.get('tariff_vulnerable', False):
            sources.append('tariff_vulnerable')
        
        if node_data.get('supply_constrained', False):
            sources.append('supply_constrained')
        
        if node_data.get('affected_by_event', False):
            event_level = node_data.get('event_impact_level', 'medium')
            sources.append(f'affected_by_{event_level}_event')
        
        if node_data.get('affected_by_shortage', False):
            shortage_level = node_data.get('shortage_level', 'moderate')
            sources.append(f'affected_by_{shortage_level}_shortage')
        
        return sources
    
    def _generate_compound_recommendations(self, scenarios: List[Dict], 
                                         affected_components: List[Dict],
                                         affected_products: List[Dict]) -> List[Dict]:
        """
        Generate recommendations for compound scenarios.
        
        Args:
            scenarios: List of scenario result dictionaries
            affected_components: List of affected components
            affected_products: List of affected products
            
        Returns:
            List of recommendation dictionaries
        """
        # Collect all individual recommendations
        all_recommendations = []
        for scenario in scenarios:
            all_recommendations.extend(scenario.get('recommendations', []))
        
        # Group by action to avoid duplicates
        action_groups = {}
        for rec in all_recommendations:
            action = rec.get('action')
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(rec)
        
        # Take the highest priority recommendation from each action group
        priority_map = {'high': 0, 'medium': 1, 'low': 2}
        consolidated_recommendations = []
        
        for action, recs in action_groups.items():
            # Sort by priority (high first)
            sorted_recs = sorted(recs, key=lambda x: priority_map.get(x.get('priority', 'low'), 3))
            consolidated_recommendations.append(sorted_recs[0])
        
        # Sort final recommendations by priority
        consolidated_recommendations.sort(key=lambda x: priority_map.get(x.get('priority', 'low'), 3))
        
        # Add an overall strategy recommendation for compound disruptions
        if len(scenarios) > 1:
            consolidated_recommendations.insert(0, {
                'action': 'compound_strategy',
                'description': f"Develop a coordinated response strategy for multiple simultaneous disruptions affecting {len(affected_components)} components",
                'priority': 'high',
                'estimated_benefit': 'Coordinated response to minimize compound impacts',
                'implementation_difficulty': 'high',
                'timeframe': 'immediate'
            })
        
        return consolidated_recommendations
