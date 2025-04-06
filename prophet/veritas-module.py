"""
veritas.py - Truth Analysis Engine for Supply Chain Intelligence

This module analyzes supply chain graphs to extract meaningful insights
and identify critical vulnerabilities, single points of failure,
and other significant patterns in the supply chain.

The Veritas engine serves as the analytical core of the Nova Prophet system.
"""

import networkx as nx
import logging
import json
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from data_models import NodeType, RelationshipType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Veritas")

class SupplyChainAnalyzer:
    """
    Core analysis engine for examining supply chain graphs and extracting critical insights.
    """
    
    def __init__(self, graph):
        """
        Initialize the supply chain analyzer with a NetworkX graph.
        
        Args:
            graph: NetworkX DiGraph object representing the supply chain
        """
        self.graph = graph
        logger.info(f"Initialized SupplyChainAnalyzer with graph containing {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    def find_critical_components(self, manufacturer_id: str = None, threshold: float = 0.7) -> List[Dict]:
        """
        Identify critical components in the supply chain based on multiple criteria.
        
        Args:
            manufacturer_id: Optional ID of manufacturer to filter by
            threshold: Criticality threshold (0.0 to 1.0)
            
        Returns:
            List of dictionaries containing critical component information
        """
        logger.info(f"Finding critical components{' for manufacturer '+manufacturer_id if manufacturer_id else ''}")
        
        critical_components = []
        products_to_analyze = []
        
        # If manufacturer specified, find all their products
        if manufacturer_id:
            for source, target, edge_data in self.graph.out_edges(manufacturer_id, data=True):
                if edge_data.get('relationship_type') == 'MANUFACTURES':
                    products_to_analyze.append(target)
            logger.info(f"Found {len(products_to_analyze)} products for manufacturer {manufacturer_id}")
        else:
            # Otherwise analyze all products
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get('node_type') == 'product':
                    products_to_analyze.append(node_id)
            logger.info(f"Analyzing {len(products_to_analyze)} products across all manufacturers")
        
        # Analyze each product
        for product_id in products_to_analyze:
            product_data = self.graph.nodes[product_id]
            product_name = product_data.get('name', 'Unknown')
            
            # Find components used in the product
            product_components = []
            for source, target, edge_data in self.graph.out_edges(product_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    component_data = self.graph.nodes[target]
                    component_id = target
                    
                    # Calculate criticality score
                    criticality_score = self._calculate_component_criticality(component_id, product_id)
                    
                    # Only include components above the threshold
                    if criticality_score >= threshold:
                        # Find suppliers of this component
                        suppliers = []
                        for s, _, s_edge in self.graph.in_edges(component_id, data=True):
                            if s_edge.get('relationship_type') == 'SUPPLIES':
                                supplier_name = self.graph.nodes[s].get('name', 'Unknown')
                                suppliers.append(supplier_name)
                        
                        # Add component to critical list
                        critical_components.append({
                            'component_id': component_id,
                            'component_name': component_data.get('name', 'Unknown'),
                            'product_id': product_id,
                            'product_name': product_name,
                            'criticality_score': criticality_score,
                            'tariff_vulnerable': component_data.get('tariff_vulnerable', False),
                            'suppliers': suppliers,
                            'countries': self._get_component_countries(component_id)
                        })
        
        # Sort by criticality score
        critical_components.sort(key=lambda x: x['criticality_score'], reverse=True)
        logger.info(f"Found {len(critical_components)} critical components above threshold {threshold}")
        
        return critical_components
    
    def _calculate_component_criticality(self, component_id: str, product_id: str) -> float:
        """
        Calculate a criticality score for a component based on multiple factors.
        
        Args:
            component_id: ID of the component
            product_id: ID of the product containing the component
            
        Returns:
            Float criticality score between 0.0 and 1.0
        """
        component_data = self.graph.nodes[component_id]
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
        for s, _, s_edge in self.graph.in_edges(component_id, data=True):
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
        countries = self._get_component_countries(component_id)
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
    
    def _get_component_countries(self, component_id: str) -> List[str]:
        """
        Get countries associated with a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of country names
        """
        countries = []
        for source, target, edge_data in self.graph.out_edges(component_id, data=True):
            if edge_data.get('relationship_type') == 'ORIGINATES_FROM' and self.graph.nodes[target].get('node_type') == 'country':
                countries.append(self.graph.nodes[target].get('name', 'Unknown'))
        
        return countries
    
    def detect_single_points_of_failure(self) -> List[Dict]:
        """
        Identify single points of failure in the supply chain.
        
        Returns:
            List of dictionaries containing single point of failure information
        """
        logger.info("Detecting single points of failure in supply chain")
        
        single_points = []
        
        # Analyze components with single suppliers
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component':
                # Find suppliers for this component
                suppliers = []
                for s, _, s_edge in self.graph.in_edges(node_id, data=True):
                    if s_edge.get('relationship_type') == 'SUPPLIES':
                        suppliers.append(s)
                
                # If only one supplier, this is a potential SPOF
                if len(suppliers) == 1:
                    # Find products using this component
                    products = []
                    for p, _, p_edge in self.graph.in_edges(node_id, data=True):
                        if p_edge.get('relationship_type') == 'CONTAINS':
                            products.append({
                                'id': p,
                                'name': self.graph.nodes[p].get('name', 'Unknown')
                            })
                    
                    if products:  # Only include if used in products
                        single_points.append({
                            'type': 'single_supplier',
                            'component_id': node_id,
                            'component_name': node_data.get('name', 'Unknown'),
                            'supplier_id': suppliers[0],
                            'supplier_name': self.graph.nodes[suppliers[0]].get('name', 'Unknown'),
                            'affected_products': products,
                            'risk_level': 'high' if node_data.get('critical', False) else 'medium'
                        })
        
        # Analyze components from a single country
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component':
                countries = self._get_component_countries(node_id)
                
                if len(countries) == 1:
                    # Find products using this component
                    products = []
                    for p, _, p_edge in self.graph.in_edges(node_id, data=True):
                        if p_edge.get('relationship_type') == 'CONTAINS':
                            products.append({
                                'id': p,
                                'name': self.graph.nodes[p].get('name', 'Unknown')
                            })
                    
                    if products:  # Only include if used in products
                        single_points.append({
                            'type': 'single_country',
                            'component_id': node_id,
                            'component_name': node_data.get('name', 'Unknown'),
                            'country': countries[0],
                            'affected_products': products,
                            'risk_level': 'high' if node_data.get('critical', False) else 'medium'
                        })
        
        logger.info(f"Found {len(single_points)} single points of failure")
        return single_points
    
    def assess_tariff_vulnerability(self, country: str = None) -> Dict:
        """
        Assess the vulnerability of the supply chain to tariffs.
        
        Args:
            country: Optional country name to focus on
            
        Returns:
            Dictionary containing tariff vulnerability analysis
        """
        logger.info(f"Assessing tariff vulnerability{' for country: '+country if country else ''}")
        
        # If country specified, convert to country_id format
        country_id = None
        if country:
            country_id = f"country_{country.lower().replace(' ', '_')}"
        
        # Counter for affected components
        affected_components = []
        affected_products = set()
        affected_companies = set()
        
        # Analyze each component
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component' and node_data.get('tariff_vulnerable', False):
                # If country specified, check if component is from that country
                if country:
                    from_specified_country = False
                    for _, target, edge_data in self.graph.out_edges(node_id, data=True):
                        if edge_data.get('relationship_type') == 'ORIGINATES_FROM' and target == country_id:
                            from_specified_country = True
                            break
                    
                    if not from_specified_country:
                        continue
                
                # Find products using this component
                component_products = []
                for source, _, edge_data in self.graph.in_edges(node_id, data=True):
                    if edge_data.get('relationship_type') == 'CONTAINS':
                        product_data = self.graph.nodes[source]
                        product_name = product_data.get('name', 'Unknown')
                        product_id = source
                        
                        # Find manufacturer
                        manufacturer = None
                        manufacturer_id = None
                        for m, _, m_edge in self.graph.in_edges(product_id, data=True):
                            if m_edge.get('relationship_type') == 'MANUFACTURES':
                                manufacturer = self.graph.nodes[m].get('name', 'Unknown')
                                manufacturer_id = m
                                break
                        
                        component_products.append({
                            'product_id': product_id,
                            'product_name': product_name,
                            'manufacturer': manufacturer,
                            'manufacturer_id': manufacturer_id
                        })
                        
                        affected_products.add(product_id)
                        if manufacturer_id:
                            affected_companies.add(manufacturer_id)
                
                # Add to the list of affected components
                if component_products:  # Only include if used in products
                    affected_components.append({
                        'component_id': node_id,
                        'component_name': node_data.get('name', 'Unknown'),
                        'tariff_vulnerable': True,
                        'countries': self._get_component_countries(node_id),
                        'products': component_products
                    })
        
        # Summarize findings
        result = {
            'affected_components_count': len(affected_components),
            'affected_products_count': len(affected_products),
            'affected_companies_count': len(affected_companies),
            'highest_risk_components': affected_components[:10] if len(affected_components) > 10 else affected_components,
            'country_focus': country
        }
        
        logger.info(f"Found {len(affected_components)} tariff-vulnerable components affecting {len(affected_products)} products")
        return result
    
    def identify_geographical_concentration(self) -> Dict:
        """
        Identify geographical concentration in the supply chain.
        
        Returns:
            Dictionary containing geographical concentration analysis
        """
        logger.info("Identifying geographical concentration in supply chain")
        
        # Count components by country
        country_components = defaultdict(list)
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component':
                countries = self._get_component_countries(node_id)
                for country in countries:
                    country_components[country].append({
                        'component_id': node_id,
                        'component_name': node_data.get('name', 'Unknown'),
                        'critical': node_data.get('critical', False),
                        'tariff_vulnerable': node_data.get('tariff_vulnerable', False)
                    })
        
        # Calculate concentration metrics
        countries_analysis = []
        for country, components in country_components.items():
            critical_count = sum(1 for c in components if c['critical'])
            tariff_vulnerable_count = sum(1 for c in components if c['tariff_vulnerable'])
            
            countries_analysis.append({
                'country': country,
                'total_components': len(components),
                'critical_components': critical_count,
                'tariff_vulnerable_components': tariff_vulnerable_count,
                'concentration_score': round((len(components) * 0.4 + critical_count * 0.6) / max(1, len(self.graph.nodes(data=True))), 3),
                'risk_level': 'high' if critical_count > 5 else 'medium' if critical_count > 2 else 'low'
            })
        
        # Sort by concentration score
        countries_analysis.sort(key=lambda x: x['concentration_score'], reverse=True)
        
        result = {
            'country_concentration': countries_analysis,
            'highest_concentration': countries_analysis[0] if countries_analysis else None,
            'concentration_summary': {
                'high_risk_countries': sum(1 for c in countries_analysis if c['risk_level'] == 'high'),
                'medium_risk_countries': sum(1 for c in countries_analysis if c['risk_level'] == 'medium'),
                'low_risk_countries': sum(1 for c in countries_analysis if c['risk_level'] == 'low')
            }
        }
        
        logger.info(f"Analyzed geographical concentration across {len(countries_analysis)} countries")
        return result
    
    def calculate_resilience_score(self, company_id: str = None) -> Dict:
        """
        Calculate a resilience score for the entire supply chain or a specific company.
        
        Args:
            company_id: Optional company ID to focus on
            
        Returns:
            Dictionary containing resilience score and factors
        """
        logger.info(f"Calculating resilience score{' for company: '+company_id if company_id else ''}")
        
        # Define scoring factors and weights
        factors = {
            'supplier_diversity': {'score': 0, 'weight': 0.25},
            'geographical_diversity': {'score': 0, 'weight': 0.2},
            'component_criticality': {'score': 0, 'weight': 0.3},
            'tariff_vulnerability': {'score': 0, 'weight': 0.15},
            'alternative_sources': {'score': 0, 'weight': 0.1}
        }
        
        products_to_analyze = []
        
        # If company specified, find all their products
        if company_id:
            for source, target, edge_data in self.graph.out_edges(company_id, data=True):
                if edge_data.get('relationship_type') == 'MANUFACTURES':
                    products_to_analyze.append(target)
        else:
            # Otherwise analyze all products
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get('node_type') == 'product':
                    products_to_analyze.append(node_id)
        
        if not products_to_analyze:
            logger.warning(f"No products found for analysis")
            return {'total_resilience_score': 0, 'factors': factors}
        
        # Analysis metrics
        total_components = 0
        unique_suppliers = set()
        unique_countries = set()
        critical_components = 0
        tariff_vulnerable_components = 0
        single_supplier_components = 0
        
        # Analyze each product
        for product_id in products_to_analyze:
            product_suppliers = set()
            product_countries = set()
            product_components = []
            
            # Find components for this product
            for source, target, edge_data in self.graph.out_edges(product_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    component_id = target
                    component_data = self.graph.nodes[component_id]
                    product_components.append(component_id)
                    
                    # Count critical and tariff_vulnerable
                    if component_data.get('critical', False):
                        critical_components += 1
                    if component_data.get('tariff_vulnerable', False):
                        tariff_vulnerable_components += 1
                    
                    # Find suppliers
                    component_suppliers = []
                    for s, _, s_edge in self.graph.in_edges(component_id, data=True):
                        if s_edge.get('relationship_type') == 'SUPPLIES':
                            component_suppliers.append(s)
                            product_suppliers.add(s)
                            unique_suppliers.add(s)
                    
                    if len(component_suppliers) <= 1:
                        single_supplier_components += 1
                    
                    # Find countries
                    countries = self._get_component_countries(component_id)
                    for country in countries:
                        product_countries.add(country)
                        unique_countries.add(country)
            
            total_components += len(product_components)
        
        # Calculate factor scores (0-100 scale, higher is better)
        
        # Supplier diversity - higher is better
        avg_suppliers_per_component = len(unique_suppliers) / max(1, total_components)
        factors['supplier_diversity']['score'] = min(100, max(0, avg_suppliers_per_component * 50))
        
        # Geographical diversity - higher is better
        avg_countries_per_component = len(unique_countries) / max(1, total_components)
        factors['geographical_diversity']['score'] = min(100, max(0, avg_countries_per_component * 60))
        
        # Component criticality - lower percentage is better
        critical_percentage = critical_components / max(1, total_components)
        factors['component_criticality']['score'] = min(100, max(0, 100 - (critical_percentage * 100)))
        
        # Tariff vulnerability - lower percentage is better
        tariff_percentage = tariff_vulnerable_components / max(1, total_components)
        factors['tariff_vulnerability']['score'] = min(100, max(0, 100 - (tariff_percentage * 100)))
        
        # Alternative sources - lower percentage of single-sourced is better
        single_source_percentage = single_supplier_components / max(1, total_components)
        factors['alternative_sources']['score'] = min(100, max(0, 100 - (single_source_percentage * 100)))
        
        # Calculate total weighted score
        total_score = sum(factor['score'] * factor['weight'] for factor in factors.values())
        
        # Add helpful interpretation
        risk_level = 'high'
        if total_score >= 80:
            risk_level = 'low'
        elif total_score >= 60:
            risk_level = 'medium'
        
        result = {
            'total_resilience_score': round(total_score, 1),
            'risk_level': risk_level,
            'factors': {
                name: {
                    'score': round(data['score'], 1),
                    'weight': data['weight']
                } for name, data in factors.items()
            },
            'metrics': {
                'total_components': total_components,
                'unique_suppliers': len(unique_suppliers),
                'unique_countries': len(unique_countries),
                'critical_components': critical_components,
                'tariff_vulnerable_components': tariff_vulnerable_components,
                'single_supplier_components': single_supplier_components
            }
        }
        
        logger.info(f"Calculated resilience score: {round(total_score, 1)}/100 (Risk Level: {risk_level})")
        return result


class InsightExtractor:
    """
    Extracts insights and generates reports from supply chain analysis.
    """
    
    def __init__(self, analyzer):
        """
        Initialize the insight extractor with a SupplyChainAnalyzer.
        
        Args:
            analyzer: SupplyChainAnalyzer instance
        """
        self.analyzer = analyzer
        self.graph = analyzer.graph
        logger.info("Initialized InsightExtractor")
    
    def extract_component_insights(self, top_n: int = 10) -> Dict:
        """
        Extract insights about the most critical components.
        
        Args:
            top_n: Number of top components to analyze
            
        Returns:
            Dictionary containing component insights
        """
        logger.info(f"Extracting insights for top {top_n} critical components")
        
        # Get critical components
        critical_components = self.analyzer.find_critical_components(threshold=0.6)
        
        # Limit to top N
        top_components = critical_components[:top_n]
        
        # Additional analysis for each component
        component_insights = []
        
        for component in top_components:
            component_id = component['component_id']
            
            # Find how many products use this component
            usage_count = 0
            products_using = []
            for source, target, edge_data in self.graph.in_edges(component_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    usage_count += 1
                    product_name = self.graph.nodes[source].get('name', 'Unknown')
                    products_using.append(product_name)
            
            # Find viable alternatives if any
            alternatives = self._find_component_alternatives(component_id)
            
            # Add insights
            component_insights.append({
                'component_id': component_id,
                'component_name': component['component_name'],
                'criticality_score': component['criticality_score'],
                'usage_count': usage_count,
                'products_using': products_using,
                'suppliers': component['suppliers'],
                'countries': component['countries'],
                'alternatives': alternatives,
                'recommendation': self._generate_component_recommendation(component, alternatives)
            })
        
        result = {
            'top_critical_components': component_insights,
            'summary': {
                'average_criticality': round(sum(c['criticality_score'] for c in component_insights) / max(1, len(component_insights)), 2),
                'most_used_component': max(component_insights, key=lambda x: x['usage_count']) if component_insights else None,
                'least_alternatives': min(component_insights, key=lambda x: len(x['alternatives'])) if component_insights else None
            }
        }
        
        logger.info(f"Extracted insights for {len(component_insights)} components")
        return result
    
    def _find_component_alternatives(self, component_id: str) -> List[Dict]:
        """
        Find potential alternative components that could replace the given component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of alternative component dictionaries
        """
        component_data = self.graph.nodes[component_id]
        component_name = component_data.get('name', 'Unknown')
        
        # Find all components of similar type
        alternatives = []
        
        for node_id, node_data in self.graph.nodes(data=True):
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
                for s, _, s_edge in self.graph.in_edges(node_id, data=True):
                    if s_edge.get('relationship_type') == 'SUPPLIES':
                        supplier_name = self.graph.nodes[s].get('name', 'Unknown')
                        suppliers.append(supplier_name)
                
                alternatives.append({
                    'component_id': node_id,
                    'component_name': node_name,
                    'similarity_score': round(len(common_words) / max(len(original_words), len(alt_words)), 2),
                    'suppliers': suppliers,
                    'countries': self.analyzer._get_component_countries(node_id)
                })
        
        # Sort by similarity
        alternatives.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def _generate_component_recommendation(self, component: Dict, alternatives: List[Dict]) -> str:
        """
        Generate a recommendation based on component analysis.
        
        Args:
            component: Component dictionary
            alternatives: List of alternative components
            
        Returns:
            Recommendation string
        """
        if component['criticality_score'] >= 0.8:
            if not alternatives:
                return "HIGH RISK: This critical component has no viable alternatives. Urgent action needed to diversify suppliers or identify alternative components."
            else:
                return f"HIGH RISK: Consider alternatives like {alternatives[0]['component_name']} to reduce dependency on this critical component."
        elif component['criticality_score'] >= 0.6:
            if len(component['suppliers']) <= 1:
                return "MEDIUM RISK: Single supplier dependency. Establish relationships with additional suppliers."
            else:
                return "MEDIUM RISK: Monitor this component closely and maintain relationships with multiple suppliers."
        else:
            return "LOW RISK: Maintain current supply chain strategy for this component."
    
    def extract_supplier_insights(self, top_n: int = 5) -> Dict:
        """
        Extract insights about key suppliers in the supply chain.
        
        Args:
            top_n: Number of top suppliers to analyze
            
        Returns:
            Dictionary containing supplier insights
        """
        logger.info(f"Extracting insights for top {top_n} suppliers")
        
        # Count components and critical components by supplier
        supplier_data = defaultdict(lambda: {
            'component_count': 0,
            'critical_component_count': 0,
            'components': [],
            'countries': set(),
            'tariff_vulnerable_count': 0
        })
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'component':
                component_name = node_data.get('name', 'Unknown')
                is_critical = node_data.get('critical', False)
                is_tariff_vulnerable = node_data.get('tariff_vulnerable', False)
                
                # Find suppliers
                for s, _, s_edge in self.graph.in_edges(node_id, data=True):
                    if s_edge.get('relationship_type') == 'SUPPLIES':
                        supplier_id = s
                        supplier_name = self.graph.nodes[s].get('name', 'Unknown')
                        
                        # Update supplier data
                        supplier_data[supplier_id]['name'] = supplier_name
                        supplier_data[supplier_id]['component_count'] += 1
                        if is_critical:
                            supplier_data[supplier_id]['critical_component_count'] += 1
                        if is_tariff_vulnerable:
                            supplier_data[supplier_id]['tariff_vulnerable_count'] += 1
                        
                        supplier_data[supplier_id]['components'].append({
                            'component_id': node_id,
                            'component_name': component_name,
                            'critical': is_critical,
                            'tariff_vulnerable': is_tariff_vulnerable
                        })
                        
                        # Add countries
                        countries = self.analyzer._get_component_countries(node_id)
                        for country in countries:
                            supplier_data[supplier_id]['countries'].add(country)
        
        # Convert to list and calculate importance score
        suppliers_list = []
        for supplier_id, data in supplier_data.items():
            # Calculate importance score based on critical components and total components
            importance_score = (data['critical_component_count'] * 3 + data['component_count']) / 4
            
            suppliers_list.append({
                'supplier_id': supplier_id,
                'supplier_name': data['name'],
                'importance_score': round(importance_score, 2),
                'component_count': data['component_count'],
                'critical_component_count': data['critical_component_count'],
                'tariff_vulnerable_count': data['tariff_vulnerable_count'],
                'countries': list(data['countries']),
                'key_components': sorted(data['components'], key=lambda x: x['critical'], reverse=True)[:5]
            })
        
        # Sort by importance score
        suppliers_list.sort(key=lambda x: x['importance_score'], reverse=True)
        top_suppliers = suppliers_list[:top_n]
        
        # Generate recommendations
        for supplier in top_suppliers:
            if supplier['critical_component_count'] > 3:
                supplier['risk_level'] = 'high'
                supplier['recommendation'] = f"HIGH DEPENDENCY: {supplier['supplier_name']} supplies {supplier['critical_component_count']} critical components. Develop alternate sources for key components."
            elif supplier['critical_component_count'] > 0:
                supplier['risk_level'] = 'medium'
                supplier['recommendation'] = f"MODERATE DEPENDENCY: Maintain strong relationship with {supplier['supplier_name']} while developing alternatives for critical components."
            else:
                supplier['risk_level'] = 'low'
                supplier['recommendation'] = f"LOW RISK: Continue standard supplier management practices with {supplier['supplier_name']}."
        
        result = {
            'top_suppliers': top_suppliers,
            'summary': {
                'total_suppliers': len(suppliers_list),
                'high_risk_suppliers': sum(1 for s in top_suppliers if s['risk_level'] == 'high'),
                'medium_risk_suppliers': sum(1 for s in top_suppliers if s['risk_level'] == 'medium'),
                'low_risk_suppliers': sum(1 for s in top_suppliers if s['risk_level'] == 'low')
            }
        }
        
        logger.info(f"Extracted insights for {len(top_suppliers)} suppliers out of {len(suppliers_list)} total")
        return result
    
    def extract_geographical_insights(self) -> Dict:
        """
        Extract geographical insights from the supply chain.
        
        Returns:
            Dictionary containing geographical insights
        """
        logger.info("Extracting geographical insights")
        
        # Get geographical concentration analysis
        geo_concentration = self.analyzer.identify_geographical_concentration()
        
        # Identify top risk countries
        high_risk_countries = [c for c in geo_concentration['country_concentration'] if c['risk_level'] == 'high']
        
        # Analyze regional dependencies
        region_analysis = {}
        for country_data in geo_concentration['country_concentration']:
            country = country_data['country']
            region = self._get_region_for_country(country)
            
            if region not in region_analysis:
                region_analysis[region] = {
                    'region': region,
                    'countries': [],
                    'total_components': 0,
                    'critical_components': 0,
                    'tariff_vulnerable_components': 0
                }
            
            region_analysis[region]['countries'].append(country)
            region_analysis[region]['total_components'] += country_data['total_components']
            region_analysis[region]['critical_components'] += country_data['critical_components']
            region_analysis[region]['tariff_vulnerable_components'] += country_data['tariff_vulnerable_components']
        
        # Convert to list and calculate risk level
        regions_list = []
        for region, data in region_analysis.items():
            # Calculate risk score
            risk_score = (data['critical_components'] * 0.7 + data['tariff_vulnerable_components'] * 0.3) / max(1, data['total_components'])
            
            risk_level = 'low'
            if risk_score > 0.4:
                risk_level = 'high'
            elif risk_score > 0.2:
                risk_level = 'medium'
            
            regions_list.append({
                'region': region,
                'countries': data['countries'],
                'total_components': data['total_components'],
                'critical_components': data['critical_components'],
                'tariff_vulnerable_components': data['tariff_vulnerable_components'],
                'risk_level': risk_level,
                'risk_score': round(risk_score, 2)
            })
        
        # Sort by risk score
        regions_list.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Generate recommendations
        recommendations = []
        
        if high_risk_countries:
            recommendations.append({
                'priority': 'high',
                'recommendation': f"Diversify supply sources away from high-risk countries: {', '.join([c['country'] for c in high_risk_countries[:3]])}"
            })
        
        # Find regions with high concentration
        high_risk_regions = [r for r in regions_list if r['risk_level'] == 'high']
        if high_risk_regions:
            recommendations.append({
                'priority': 'high',
                'recommendation': f"Reduce dependency on {high_risk_regions[0]['region']} region by developing alternate sources in other regions."
            })
        
        # Look for countries with export restrictions
        export_restricted_countries = self._find_countries_with_export_restrictions()
        if export_restricted_countries:
            recommendations.append({
                'priority': 'medium',
                'recommendation': f"Monitor export policies in {', '.join(export_restricted_countries[:3])} which may affect component availability."
            })
        
        result = {
            'high_risk_countries': high_risk_countries[:5] if len(high_risk_countries) > 5 else high_risk_countries,
            'regional_analysis': regions_list,
            'recommendations': recommendations,
            'summary': {
                'most_critical_region': regions_list[0]['region'] if regions_list else None,
                'countries_analyzed': len(geo_concentration['country_concentration']),
                'regions_analyzed': len(regions_list)
            }
        }
        
        logger.info(f"Extracted geographical insights across {len(regions_list)} regions and {len(geo_concentration['country_concentration'])} countries")
        return result
    
    def _get_region_for_country(self, country: str) -> str:
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
    
    def _find_countries_with_export_restrictions(self) -> List[str]:
        """
        Find countries with export restrictions in the graph.
        
        Returns:
            List of country names
        """
        # This would ideally use actual export control data from the graph
        # For this implementation, we'll return a placeholder list
        return ['United States', 'China', 'Japan']
    
    def generate_summary_report(self, company_id: str = None) -> Dict:
        """
        Generate a comprehensive summary report of the supply chain.
        
        Args:
            company_id: Optional company ID to focus on
            
        Returns:
            Dictionary containing comprehensive report
        """
        logger.info(f"Generating comprehensive supply chain report{' for company: '+company_id if company_id else ''}")
        
        # Get resilience score
        resilience = self.analyzer.calculate_resilience_score(company_id)
        
        # Get critical components
        critical_threshold = 0.7
        critical_components = self.analyzer.find_critical_components(
            manufacturer_id=company_id, 
            threshold=critical_threshold
        )
        
        # Get single points of failure
        single_points = self.analyzer.detect_single_points_of_failure()
        
        # Get tariff vulnerability
        tariff_vulnerability = self.analyzer.assess_tariff_vulnerability()
        
        # Get geographical concentration
        geo_concentration = self.analyzer.identify_geographical_concentration()
        
        # Compile top risks
        top_risks = []
        
        # Risk 1: Low resilience score
        if resilience['total_resilience_score'] < 60:
            top_risks.append({
                'risk_type': 'low_resilience',
                'description': f"Low overall supply chain resilience score: {resilience['total_resilience_score']}/100",
                'priority': 'high'
            })
        
        # Risk 2: Critical components
        if len(critical_components) > 0:
            critical_names = ", ".join([c['component_name'] for c in critical_components[:3]])
            top_risks.append({
                'risk_type': 'critical_components',
                'description': f"Found {len(critical_components)} critical components with high vulnerability (e.g., {critical_names})",
                'priority': 'high' if len(critical_components) > 5 else 'medium'
            })
        
        # Risk 3: Single points of failure
        if len(single_points) > 0:
            top_risks.append({
                'risk_type': 'single_points',
                'description': f"Found {len(single_points)} single points of failure in the supply chain",
                'priority': 'high' if len(single_points) > 3 else 'medium'
            })
        
        # Risk 4: Geographical concentration
        high_risk_countries = [c for c in geo_concentration['country_concentration'] if c['risk_level'] == 'high']
        if high_risk_countries:
            country_names = ", ".join([c['country'] for c in high_risk_countries[:2]])
            top_risks.append({
                'risk_type': 'geographical_concentration',
                'description': f"High geographical concentration in {len(high_risk_countries)} countries (e.g., {country_names})",
                'priority': 'high' if len(high_risk_countries) > 1 else 'medium'
            })
        
        # Risk 5: Tariff vulnerability
        if tariff_vulnerability['affected_components_count'] > 0:
            top_risks.append({
                'risk_type': 'tariff_vulnerability',
                'description': f"Found {tariff_vulnerability['affected_components_count']} components vulnerable to tariffs affecting {tariff_vulnerability['affected_products_count']} products",
                'priority': 'high' if tariff_vulnerability['affected_components_count'] > 10 else 'medium'
            })
        
        # Sort risks by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        top_risks.sort(key=lambda x: priority_order[x['priority']])
        
        # Generate strategic recommendations
        strategic_recommendations = []
        
        # Recommendation 1: Improve resilience
        if resilience['total_resilience_score'] < 70:
            lowest_factor = min(resilience['factors'].items(), key=lambda x: x[1]['score'])
            strategic_recommendations.append({
                'category': 'resilience',
                'recommendation': f"Improve overall supply chain resilience by focusing on {lowest_factor[0].replace('_', ' ')}",
                'priority': 'high' if resilience['total_resilience_score'] < 60 else 'medium'
            })
        
        # Recommendation 2: Diversify suppliers
        if resilience['metrics']['single_supplier_components'] > 0:
            strategic_recommendations.append({
                'category': 'diversification',
                'recommendation': f"Diversify suppliers for {resilience['metrics']['single_supplier_components']} components that currently have single suppliers",
                'priority': 'high' if resilience['metrics']['single_supplier_components'] > 5 else 'medium'
            })
        
        # Recommendation 3: Geographical diversification
        if high_risk_countries:
            strategic_recommendations.append({
                'category': 'geographical',
                'recommendation': f"Reduce dependency on components from {high_risk_countries[0]['country']} by finding alternative sources",
                'priority': 'high'
            })
        
        # Recommendation 4: Tariff mitigation
        if tariff_vulnerability['affected_components_count'] > 0:
            strategic_recommendations.append({
                'category': 'tariff',
                'recommendation': f"Develop mitigation strategies for tariff-vulnerable components, particularly those used in multiple products",
                'priority': 'medium'
            })
        
        # Recommendation 5: Monitoring system
        strategic_recommendations.append({
            'category': 'monitoring',
            'recommendation': "Implement real-time monitoring system for supply chain disruptions and geopolitical risks",
            'priority': 'medium'
        })
        
        # Sort recommendations by priority
        strategic_recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        # Compile complete report
        report = {
            'report_title': f"Supply Chain Analysis Report{' for '+self.graph.nodes[company_id]['name'] if company_id else ''}",
            'executive_summary': {
                'resilience_score': resilience['total_resilience_score'],
                'risk_level': resilience['risk_level'],
                'critical_components_count': len(critical_components),
                'single_points_count': len(single_points),
                'affected_by_tariffs_count': tariff_vulnerability['affected_components_count'],
                'top_risks': top_risks
            },
            'key_metrics': resilience['metrics'],
            'critical_components': critical_components[:10] if len(critical_components) > 10 else critical_components,
            'single_points_of_failure': single_points[:10] if len(single_points) > 10 else single_points,
            'geographical_analysis': {
                'high_risk_countries': high_risk_countries,
                'highest_concentration': geo_concentration['highest_concentration']
            },
            'strategic_recommendations': strategic_recommendations,
            'generated_timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"Generated comprehensive report with {len(top_risks)} top risks and {len(strategic_recommendations)} strategic recommendations")
        return report


def save_report_to_json(report: Dict, filename: str) -> None:
    """
    Save a report to a JSON file.
    
    Args:
        report: Report dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Saved report to {filename}")


def save_report_to_markdown(report: Dict, filename: str) -> None:
    """
    Save a report to a Markdown file.
    
    Args:
        report: Report dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        # Write title
        f.write(f"# {report['report_title']}\n\n")
        f.write(f"*Generated: {report['generated_timestamp']}*\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        summary = report['executive_summary']
        f.write(f"- **Supply Chain Resilience Score**: {summary['resilience_score']}/100 ({summary['risk_level'].upper()} RISK)\n")
        f.write(f"- **Critical Components**: {summary['critical_components_count']}\n")
        f.write(f"- **Single Points of Failure**: {summary['single_points_count']}\n")
        f.write(f"- **Components Affected by Tariffs**: {summary['affected_by_tariffs_count']}\n\n")
        
        # Top Risks
        f.write("### Top Risks\n\n")
        for i, risk in enumerate(summary['top_risks']):
            f.write(f"{i+1}. **{risk['priority'].upper()}**: {risk['description']}\n")
        f.write("\n")
        
        # Strategic Recommendations
        f.write("## Strategic Recommendations\n\n")
        for i, rec in enumerate(report['strategic_recommendations']):
            f.write(f"{i+1}. **{rec['category'].title()} ({rec['priority'].upper()})**: {rec['recommendation']}\n")
        f.write("\n")
        
        # Critical Components
        f.write("## Critical Components\n\n")
        if report['critical_components']:
            f.write("| Component | Product | Criticality | Suppliers | Countries |\n")
            f.write("|-----------|---------|------------|-----------|-----------|\n")
            for comp in report['critical_components']:
                f.write(f"| {comp['component_name']} | {comp['product_name']} | {comp['criticality_score']} | {', '.join(comp['suppliers'][:2])} | {', '.join(comp['countries'][:2])} |\n")
        else:
            f.write("*No critical components identified*\n")
        f.write("\n")
        
        # Single Points of Failure
        f.write("## Single Points of Failure\n\n")
        if report['single_points_of_failure']:
            f.write("| Type | Component | Risk Factor | Affected Products |\n")
            f.write("|------|-----------|------------|-------------------|\n")
            for spof in report['single_points_of_failure']:
                spof_type = spof['type'].replace('_', ' ').title()
                risk_factor = spof.get('supplier_name', spof.get('country', 'Unknown'))
                affected = ', '.join([p['name'] for p in spof['affected_products'][:2]])
                f.write(f"| {spof_type} | {spof['component_name']} | {risk_factor} | {affected} |\n")
        else:
            f.write("*No single points of failure identified*\n")
        f.write("\n")
        
        # Geographical Analysis
        f.write("## Geographical Analysis\n\n")
        if report['geographical_analysis']['high_risk_countries']:
            f.write("### High Risk Countries\n\n")
            f.write("| Country | Total Components | Critical Components | Risk Level |\n")
            f.write("|---------|------------------|---------------------|------------|\n")
            for country in report['geographical_analysis']['high_risk_countries']:
                f.write(f"| {country['country']} | {country['total_components']} | {country['critical_components']} | {country['risk_level'].upper()} |\n")
        else:
            f.write("*No high risk countries identified*\n")
        f.write("\n")
        
        # Key Metrics
        f.write("## Key Metrics\n\n")
        metrics = report['key_metrics']
        f.write(f"- Total Components: {metrics['total_components']}\n")
        f.write(f"- Unique Suppliers: {metrics['unique_suppliers']}\n")
        f.write(f"- Unique Countries: {metrics['unique_countries']}\n")
        f.write(f"- Critical Components: {metrics['critical_components']}\n")
        f.write(f"- Tariff Vulnerable Components: {metrics['tariff_vulnerable_components']}\n")
        f.write(f"- Single Supplier Components: {metrics['single_supplier_components']}\n")
        
    logger.info(f"Saved report to {filename}")


def main():
    """
    Main function for running the Veritas module from command line.
    """
    import argparse
    import pickle
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Veritas - Supply Chain Truth Analysis Engine')
    parser.add_argument('--graph', required=True, help='Path to pickled NetworkX graph file')
    parser.add_argument('--output', required=True, help='Output file for report (JSON or Markdown)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='Output format')
    parser.add_argument('--company', help='Optional company ID to focus analysis on')
    parser.add_argument('--critical-threshold', type=float, default=0.7, help='Threshold for critical components (0.0-1.0)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load graph
    try:
        with open(args.graph, 'rb') as f:
            graph = pickle.load(f)
        logger.info(f"Loaded graph from {args.graph} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    except Exception as e:
        logger.error(f"Failed to load graph: {e}")
        return
    
    # Create analyzer and extractor
    analyzer = SupplyChainAnalyzer(graph)
    extractor = InsightExtractor(analyzer)
    
    # Generate report
    report = extractor.generate_summary_report(company_id=args.company)
    
    # Save report
    if args.format == 'json':
        save_report_to_json(report, args.output)
    else:
        save_report_to_markdown(report, args.output)


if __name__ == "__main__":
    main()
