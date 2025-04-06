"""
prediction_engine.py - Main prediction engine for Nova Prophet

This module provides the PredictionEngine class which serves as the main interface
for running predictions and generating recommendations based on supply chain data.
"""

import logging
import json
import os
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import Prophet modules
from prophet.scenario_modeler import ScenarioModeler
from prophet.utils import save_scenario_results
from prophet.recommendation_generator import generate_optimization_recommendations

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaProphet.PredictionEngine")

class PredictionEngine:
    """
    Main prediction engine for the Nova Prophet system.
    
    This class serves as the primary interface for running supply chain
    predictions and generating recommendations.
    """
    
    def __init__(self, graph, analyzer=None):
        """
        Initialize the prediction engine.
        
        Args:
            graph: NetworkX DiGraph object representing the supply chain
            analyzer: Optional SupplyChainAnalyzer instance
        """
        self.graph = graph
        
        # Import the analyzer here to avoid circular imports
        if analyzer is None:
            from veritas import SupplyChainAnalyzer
            self.analyzer = SupplyChainAnalyzer(self.graph)
        else:
            self.analyzer = analyzer
        
        # Initialize the scenario modeler
        self.scenario_modeler = ScenarioModeler(self.graph, self.analyzer)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        logger.info(f"Initialized PredictionEngine with graph containing {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    def predict_tariff_impact(self, country: str, increase_percentage: float, 
                             affected_component_types: List[str] = None,
                             output_file: Optional[str] = None) -> Dict:
        """
        Predict the impact of tariff changes.
        
        Args:
            country: Country implementing the tariff change
            increase_percentage: Percentage increase in tariffs
            affected_component_types: Optional list of component types affected
            output_file: Optional file to save results
            
        Returns:
            Dictionary with tariff impact analysis
        """
        logger.info(f"Running tariff impact prediction for {country} with {increase_percentage}% increase")
        
        # Run the scenario
        results = self.scenario_modeler.model_tariff_change(
            country=country,
            increase_percentage=increase_percentage,
            affected_component_types=affected_component_types
        )
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            default_output = f"output/tariff_impact_{country.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def predict_supplier_disruption(self, supplier_id: str, disruption_level: str = 'complete', 
                                  duration_months: int = 3, output_file: Optional[str] = None) -> Dict:
        """
        Predict the impact of a supplier disruption.
        
        Args:
            supplier_id: ID of the affected supplier
            disruption_level: 'partial' or 'complete'
            duration_months: Duration of disruption in months
            output_file: Optional file to save results
            
        Returns:
            Dictionary with supplier disruption impact analysis
        """
        logger.info(f"Running supplier disruption prediction for {supplier_id}")
        
        # Run the scenario
        results = self.scenario_modeler.model_supplier_disruption(
            supplier_id=supplier_id,
            disruption_level=disruption_level,
            duration_months=duration_months
        )
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            default_output = f"output/supplier_disruption_{supplier_id.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def predict_geopolitical_event(self, country: str, event_type: str, severity: str = 'medium',
                                 duration_months: int = 6, output_file: Optional[str] = None) -> Dict:
        """
        Predict the impact of a geopolitical event.
        
        Args:
            country: Affected country
            event_type: Type of event ('trade_restriction', 'conflict', 'natural_disaster', 'political_change')
            severity: 'low', 'medium', or 'high'
            duration_months: Duration of impact in months
            output_file: Optional file to save results
            
        Returns:
            Dictionary with geopolitical event impact analysis
        """
        logger.info(f"Running geopolitical event prediction for {severity} {event_type} in {country}")
        
        # Import the needed module directly here
        from prophet.geopolitical_modeler import model_geopolitical_event
        
        # Run the scenario
        results = model_geopolitical_event(
            graph=self.graph,
            analyzer=self.analyzer,
            country=country,
            event_type=event_type,
            severity=severity,
            duration_months=duration_months
        )
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            default_output = f"output/geopolitical_{event_type}_{country.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def predict_component_shortage(self, component_type: str, shortage_level: str = 'severe',
                                 duration_months: int = 6, output_file: Optional[str] = None) -> Dict:
        """
        Predict the impact of a component shortage.
        
        Args:
            component_type: Type of component experiencing shortage
            shortage_level: 'moderate' or 'severe'
            duration_months: Duration of shortage in months
            output_file: Optional file to save results
            
        Returns:
            Dictionary with component shortage impact analysis
        """
        logger.info(f"Running component shortage prediction for {shortage_level} shortage of {component_type}")
        
        # Import the needed module directly here
        from prophet.shortage_modeler import model_component_shortage
        
        # Run the scenario
        results = model_component_shortage(
            graph=self.graph,
            analyzer=self.analyzer,
            component_type=component_type,
            shortage_level=shortage_level,
            duration_months=duration_months
        )
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            default_output = f"output/component_shortage_{component_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def generate_recommendations(self, company_id: Optional[str] = None, 
                               output_file: Optional[str] = None) -> Dict:
        """
        Generate general supply chain optimization recommendations.
        
        Args:
            company_id: Optional company ID to focus recommendations on
            output_file: Optional file to save results
            
        Returns:
            Dictionary with recommendations
        """
        logger.info(f"Generating optimization recommendations{' for '+company_id if company_id else ''}")
        
        # Get resilience analysis
        resilience = self.analyzer.calculate_resilience_score(company_id)
        
        # Generate recommendations
        recommendations = generate_optimization_recommendations(resilience)
        
        # Compile results
        results = {
            'recommendation_type': 'optimization',
            'company_id': company_id,
            'resilience_score': resilience['total_resilience_score'],
            'risk_level': resilience['risk_level'],
            'recommendations': recommendations,
            'resilience_factors': resilience['factors'],
            'metrics': resilience['metrics'],
            'generated_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            company_suffix = f"_{company_id.lower()}" if company_id else ""
            default_output = f"output/recommendations{company_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def find_alternative_sources(self, component_id: str, max_alternatives: int = 5,
                              output_file: Optional[str] = None) -> Dict:
        """
        Find alternative sources for a specific component.
        
        Args:
            component_id: ID of the component to find alternatives for
            max_alternatives: Maximum number of alternatives to find
            output_file: Optional file to save results
            
        Returns:
            Dictionary with alternative sources
        """
        logger.info(f"Finding alternative sources for component {component_id}")
        
        # Import utility function
        from prophet.utils import find_alternative_components, get_component_countries
        
        if component_id not in self.graph:
            logger.warning(f"Component {component_id} not found in graph")
            return {
                'component_id': component_id,
                'component_name': 'Unknown',
                'alternatives': [],
                'error': 'Component not found in graph'
            }
        
        component_data = self.graph.nodes[component_id]
        component_name = component_data.get('name', 'Unknown')
        
        # Find current suppliers
        current_suppliers = []
        for s, _, s_edge in self.graph.in_edges(component_id, data=True):
            if s_edge.get('relationship_type') == 'SUPPLIES':
                supplier_data = self.graph.nodes[s]
                current_suppliers.append({
                    'supplier_id': s,
                    'supplier_name': supplier_data.get('name', 'Unknown'),
                    'hq_country': supplier_data.get('hq_country', 'Unknown')
                })
        
        # Find current countries
        current_countries = get_component_countries(self.graph, component_id)
        
        # Find alternative components
        alternatives = find_alternative_components(self.graph, component_id, max_alternatives)
        
        # Compile results
        results = {
            'component_id': component_id,
            'component_name': component_name,
            'component_type': component_data.get('category', 'Unknown'),
            'current_suppliers': current_suppliers,
            'current_countries': current_countries,
            'alternatives': alternatives,
            'generated_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save results if output file specified
        if output_file:
            save_scenario_results(results, output_file)
        else:
            default_output = f"output/alternatives_{component_id.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(results, default_output)
        
        return results
    
    def run_comprehensive_analysis(self, company_id: Optional[str] = None,
                                 output_dir: str = "output/comprehensive",
                                 include_scenarios: bool = True) -> Dict:
        """
        Run a comprehensive analysis including baseline and scenario predictions.
        
        Args:
            company_id: Optional company ID to focus analysis on
            output_dir: Directory to save output files
            include_scenarios: Whether to include scenario analysis
            
        Returns:
            Dictionary with analysis summary
        """
        logger.info(f"Running comprehensive analysis{' for '+company_id if company_id else ''}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Import insight extractor
        from veritas import InsightExtractor
        extractor = InsightExtractor(self.analyzer)
        
        # Part 1: Baseline Analysis
        baseline_file = os.path.join(output_dir, f"baseline_analysis_{timestamp}.json")
        baseline_report = extractor.generate_summary_report(company_id)
        save_scenario_results(baseline_report, baseline_file)
        
        # Part 2: Component Analysis
        component_file = os.path.join(output_dir, f"component_insights_{timestamp}.json")
        component_insights = extractor.extract_component_insights()
        save_scenario_results(component_insights, component_file)
        
        # Part 3: Supplier Analysis
        supplier_file = os.path.join(output_dir, f"supplier_insights_{timestamp}.json")
        supplier_insights = extractor.extract_supplier_insights()
        save_scenario_results(supplier_insights, supplier_file)
        
        # Part 4: Geographical Analysis
        geo_file = os.path.join(output_dir, f"geographical_insights_{timestamp}.json")
        geo_insights = extractor.extract_geographical_insights()
        save_scenario_results(geo_insights, geo_file)
        
        # Part 5: Optimization Recommendations
        recommendations_file = os.path.join(output_dir, f"recommendations_{timestamp}.json")
        recommendations = self.generate_recommendations(company_id, recommendations_file)
        
        # Part 6: Scenario Analysis (optional)
        scenarios = []
        if include_scenarios:
            # Scenario 1: Major supplier disruption
            if company_id:
                # Find a major supplier for this company
                major_suppliers = []
                for node_id, node_data in self.graph.nodes(data=True):
                    if node_data.get('node_type') == 'company':
                        # Check if this supplier supplies to the company
                        for _, component_id, edge_data in self.graph.out_edges(node_id, data=True):
                            if edge_data.get('relationship_type') == 'SUPPLIES':
                                # Check if this component is used in any of the company's products
                                for product_source, product_target, product_edge in self.graph.in_edges(component_id, data=True):
                                    if product_edge.get('relationship_type') == 'CONTAINS':
                                        # Check if this product is made by the company
                                        for mfg_source, mfg_target, mfg_edge in self.graph.in_edges(product_source, data=True):
                                            if mfg_edge.get('relationship_type') == 'MANUFACTURES' and mfg_source == company_id:
                                                major_suppliers.append(node_id)
                                                break
                if major_suppliers:
                    supplier_id = major_suppliers[0]
                    supplier_file = os.path.join(output_dir, f"scenario_supplier_disruption_{timestamp}.json")
                    supplier_scenario = self.predict_supplier_disruption(supplier_id, 'complete', 3, supplier_file)
                    scenarios.append({
                        'type': 'supplier_disruption',
                        'supplier_id': supplier_id,
                        'supplier_name': self.graph.nodes[supplier_id].get('name', 'Unknown'),
                        'impact_level': 'high' if supplier_scenario['resilience_impact']['change'] < -10 else 'medium'
                    })
            
            # Scenario 2: Tariff change
            # Find a major sourcing country
            country_components = {}
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get('node_type') == 'component':
                    countries = []
                    for _, country_id, edge_data in self.graph.out_edges(node_id, data=True):
                        if edge_data.get('relationship_type') == 'ORIGINATES_FROM':
                            country_name = self.graph.nodes[country_id].get('name', 'Unknown')
                            countries.append(country_name)
                    
                    for country in countries:
                        if country not in country_components:
                            country_components[country] = 0
                        country_components[country] += 1
            
            # Sort by number of components
            sorted_countries = sorted(country_components.items(), key=lambda x: x[1], reverse=True)
            if sorted_countries:
                major_country = sorted_countries[0][0]
                tariff_file = os.path.join(output_dir, f"scenario_tariff_change_{timestamp}.json")
                tariff_scenario = self.predict_tariff_impact(major_country, 25, None, tariff_file)
                scenarios.append({
                    'type': 'tariff_change',
                    'country': major_country,
                    'increase_percentage': 25,
                    'impact_level': 'high' if tariff_scenario['resilience_impact']['change'] < -10 else 'medium'
                })
        
        # Compile comprehensive summary
        summary = {
            'analysis_type': 'comprehensive',
            'company_id': company_id,
            'company_name': self.graph.nodes[company_id].get('name', 'Unknown') if company_id and company_id in self.graph else 'All Companies',
            'baseline': {
                'resilience_score': baseline_report['executive_summary']['resilience_score'],
                'risk_level': baseline_report['executive_summary']['risk_level'],
                'critical_components_count': baseline_report['executive_summary']['critical_components_count'],
                'single_points_count': baseline_report['executive_summary']['single_points_count']
            },
            'top_insights': {
                'critical_components': [c['component_name'] for c in component_insights['top_critical_components'][:3]] if component_insights['top_critical_components'] else [],
                'high_risk_suppliers': [s['supplier_name'] for s in supplier_insights['top_suppliers'] if s['risk_level'] == 'high'][:3] if supplier_insights['top_suppliers'] else [],
                'high_risk_countries': [c['country'] for c in geo_insights['high_risk_countries'][:3]] if geo_insights['high_risk_countries'] else []
            },
            'top_recommendations': [r['description'] for r in recommendations['recommendations'][:5]],
            'scenarios': scenarios,
            'output_files': {
                'baseline': baseline_file,
                'components': component_file,
                'suppliers': supplier_file,
                'geographical': geo_file,
                'recommendations': recommendations_file
            },
            'generated_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save summary
        summary_file = os.path.join(output_dir, f"analysis_summary_{timestamp}.json")
        save_scenario_results(summary, summary_file)
        
        logger.info(f"Completed comprehensive analysis, saved to {output_dir}")
        
        return summary

def load_graph(graph_file: str):
    """
    Load a graph from a pickle file.
    
    Args:
        graph_file: Path to the pickled graph file
        
    Returns:
        NetworkX graph object
    """
    try:
        with open(graph_file, 'rb') as f:
            graph = pickle.load(f)
        logger.info(f"Loaded graph from {graph_file} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        return graph
    except Exception as e:
        logger.error(f"Failed to load graph: {e}")
        raise