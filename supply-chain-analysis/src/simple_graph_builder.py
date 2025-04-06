"""
simple_graph_builder.py - A simplified graph construction module for supply chain analysis
"""

import json
import networkx as nx
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GraphBuilder")

class SimpleGraphBuilder:
    """A simplified graph builder for supply chain analysis"""
    
    def __init__(self):
        """Initialize the graph builder"""
        self.graph = nx.DiGraph()
        self.node_counts = {}  # Tracking counts by node type
    
    def add_node(self, node_id: str, node_type: str, **properties):
        """
        Add a node to the graph
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (company, product, etc.)
            **properties: Additional properties for the node
        """
        # Combine all properties including node_type
        all_props = {"node_type": node_type, **properties}
        
        # Add node to graph
        self.graph.add_node(node_id, **all_props)
        
        # Update node counts
        if node_type not in self.node_counts:
            self.node_counts[node_type] = 0
        self.node_counts[node_type] += 1
    
    def add_edge(self, source_id: str, target_id: str, relationship_type: str, **properties):
        """
        Add an edge to the graph
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship
            **properties: Additional properties for the edge
        """
        # Combine all properties including relationship_type
        all_props = {"relationship_type": relationship_type, **properties}
        
        # Add edge to graph
        self.graph.add_edge(source_id, target_id, **all_props)
    
    def load_products(self, data: List[Dict], product_type: str):
        """
        Load product data into the graph
        
        Args:
            data: List of product dictionaries
            product_type: Type of product (e.g., smartphone, tablet)
        """
        logger.info(f"Loading {len(data)} {product_type} products")
        for product in data:
            product_id = product.get("product_id")
            
            # Add product node
            self.add_node(
                product_id,
                "product",
                name=product.get("product_name"),
                product_type=product_type,
                manufacturer=product.get("manufacturer"),
                category=product.get("category"),
                retail_price_usd=product.get("retail_price_usd"),
                release_year=product.get("release_year"),
                tariff_vulnerability_score=product.get("tariff_vulnerability_score")
            )
            
            # Add manufacturer relationship
            manufacturer_id = product.get("manufacturer")
            if manufacturer_id in self.graph:
                self.add_edge(manufacturer_id, product_id, "MANUFACTURES")
            
            # Add components
            for component in product.get("key_components", []):
                component_id = component.get("component_id")
                
                # Add component node if it doesn't exist
                if component_id not in self.graph:
                    self.add_node(
                        component_id,
                        "component",
                        name=component.get("name"),
                        tariff_vulnerable=component.get("tariff_vulnerable", False),
                        critical=component.get("critical", False)
                    )
                
                # Add component relationship
                self.add_edge(product_id, component_id, "CONTAINS")
                
                # Add supplier relationship
                supplier_id = component.get("supplier")
                if supplier_id in self.graph:
                    self.add_edge(supplier_id, component_id, "SUPPLIES")
                
                # Add country relationship
                country = component.get("country_of_origin")
                country_id = f"country_{country.lower().replace(' ', '_')}"
                
                # Add country node if it doesn't exist
                if country_id not in self.graph:
                    self.add_node(country_id, "country", name=country)
                
                # Add origin relationship
                self.add_edge(component_id, country_id, "ORIGINATES_FROM")
        
        logger.info(f"Loaded {len(data)} {product_type} products")
    
    def load_companies(self, data: List[Dict]):
        """
        Load company data into the graph
        
        Args:
            data: List of company dictionaries
        """
        logger.info(f"Loading {len(data)} companies")
        for company in data:
            company_id = company.get("company_id")
            
            # Add company node
            self.add_node(
                company_id,
                "company",
                name=company.get("name"),
                hq_country=company.get("hq_country"),
                hq_city=company.get("hq_city"),
                founded_year=company.get("founded_year"),
                market_cap_usd=company.get("market_cap_usd"),
                annual_revenue_usd=company.get("annual_revenue_usd"),
                employee_count=company.get("employee_count"),
                public_company=company.get("public_company", False),
                ticker=company.get("ticker")
            )
            
            # Add market relationships
            for market in company.get("key_markets", []):
                market_id = f"region_{market.lower().replace(' ', '_')}"
                
                # Add region node if it doesn't exist
                if market_id not in self.graph:
                    self.add_node(market_id, "region", name=market)
                
                # Add market relationship
                self.add_edge(company_id, market_id, "HAS_MARKET")
        
        logger.info(f"Loaded {len(data)} companies")
    
    def load_data_from_file(self, file_path: str, data_type: str):
        """
        Load data from a JSON file
        
        Args:
            file_path: Path to the JSON file
            data_type: Type of data (companies, products, etc.)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                if data_type == "electronics_companies":
                    self.load_companies(data.get("electronics_companies", []))
                elif data_type in ["smartphones", "tablets", "laptops", "wearables", "gaming_consoles", "tv_entertainment"]:
                    # Extract the appropriate key from the data
                    key = f"product_components_{data_type}"
                    product_data = data.get(key, [])
                    self.load_products(product_data, data_type)
                else:
                    logger.warning(f"Unsupported data type: {data_type}")
        
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
    
    def get_statistics(self):
        """Get statistics about the graph"""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "node_types": self.node_counts
        }
    def find_critical_components(self, manufacturer_id):

        critical_components = []
    
    # Find products from this manufacturer
        manufacturer_products = []
    # Properly traverse outgoing edges from manufacturer
        for _, target, edge_attrs in self.graph.out_edges(manufacturer_id, data=True):
            if edge_attrs.get("relationship_type") == "MANUFACTURES":
                manufacturer_products.append(target)
    
    # For each product, find critical components
        for product_id in manufacturer_products:
            product_name = self.graph.nodes[product_id].get("name", "Unknown")
        
        # Properly traverse outgoing edges from product
        for _, component_id, edge_attrs in self.graph.out_edges(product_id, data=True):
            if edge_attrs.get("relationship_type") == "CONTAINS":
                component_data = self.graph.nodes[component_id]
                
                if component_data.get("critical", False) and component_data.get("tariff_vulnerable", False):
                    critical_components.append({
                        "product": product_name,
                        "product_id": product_id,
                        "component": component_data.get("name", "Unknown"),
                        "component_id": component_id
                    })
    
        return critical_components
    
   