"""
graph_visualization.py - Module for visualizing supply chain graphs
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Visualization")

class SupplyChainVisualizer:
    """Class for visualizing supply chain graphs"""
    
    def __init__(self, graph):
        """
        Initialize the visualizer
        
        Args:
            graph: NetworkX graph object
        """
        self.graph = graph
        
        # Define color scheme for nodes
        self.node_colors = {
            "company": "#4285F4",    # Google Blue
            "product": "#EA4335",    # Google Red
            "component": "#FBBC05",  # Google Yellow
            "facility": "#34A853",   # Google Green
            "country": "#8958E8",    # Purple
            "region": "#673AB7",     # Deep Purple
            "material": "#FF9800",   # Orange
            "tariff": "#F44336",     # Red
            "export_control": "#9C27B0",  # Purple
            "disruption": "#E91E63",  # Pink
            "supply_relationship": "#009688",  # Teal
            "logistics_route": "#3F51B5",  # Indigo
            "regulation": "#607D8B"   # Blue Gray
        }
        
        # Define edge color scheme
        self.edge_colors = {
            "CONTAINS": "#1E88E5",   # Blue
            "MANUFACTURES": "#43A047",  # Green
            "SUPPLIES": "#FFA000",   # Amber
            "ORIGINATES_FROM": "#6D4C41",  # Brown
            "LOCATED_IN": "#5E35B1",  # Deep Purple
            "HAS_MARKET": "#D81B60",  # Pink
            "default": "#757575"    # Gray
        }
        
        # Define node sizes
        self.node_sizes = {
            "company": 800,
            "product": 600,
            "component": 400,
            "country": 700,
            "region": 700,
            "default": 500
        }
    
    def visualize_product_supply_chain(self, product_id: str, figsize: Tuple[int, int] = (12, 10), 
                                      save_path: Optional[str] = None):
        """
        Visualize the supply chain for a specific product
        
        Args:
            product_id: ID of the product
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the visualization
        """
        if product_id not in self.graph:
            logger.error(f"Product {product_id} not found in graph")
            return
        
        logger.info(f"Creating supply chain visualization for product {product_id}")
        
        # Create a subgraph for visualization
        subgraph = nx.DiGraph()
        
        # Add the product node
        product_data = self.graph.nodes[product_id]
        subgraph.add_node(product_id, **product_data)
        
        # Add components and their relationships
        for _, component_id, edge_attrs in self.graph.out_edges(product_id, data=True):
            if edge_attrs.get("relationship_type") == "CONTAINS":
                # Add component node
                component_data = self.graph.nodes[component_id]
                subgraph.add_node(component_id, **component_data)
                subgraph.add_edge(product_id, component_id, **edge_attrs)
                
                # Add suppliers
                for supplier_id, _, supplier_edge in self.graph.in_edges(component_id, data=True):
                    if supplier_edge.get("relationship_type") == "SUPPLIES" and supplier_id in self.graph:
                        supplier_data = self.graph.nodes[supplier_id]
                        subgraph.add_node(supplier_id, **supplier_data)
                        subgraph.add_edge(supplier_id, component_id, **supplier_edge)
                
                # Add countries of origin
                for _, country_id, origin_edge in self.graph.out_edges(component_id, data=True):
                    if origin_edge.get("relationship_type") == "ORIGINATES_FROM" and country_id in self.graph:
                        country_data = self.graph.nodes[country_id]
                        subgraph.add_node(country_id, **country_data)
                        subgraph.add_edge(component_id, country_id, **origin_edge)
        
        # Add manufacturer
        for manufacturer_id, _, edge_attrs in self.graph.in_edges(product_id, data=True):
            if edge_attrs.get("relationship_type") == "MANUFACTURES" and manufacturer_id in self.graph:
                manufacturer_data = self.graph.nodes[manufacturer_id]
                subgraph.add_node(manufacturer_id, **manufacturer_data)
                subgraph.add_edge(manufacturer_id, product_id, **edge_attrs)
        
        # Create figure and draw the graph
        plt.figure(figsize=figsize)
        
        # Use a spring layout with some randomness for better visualization
        pos = nx.spring_layout(subgraph, seed=42, k=0.3)
        
        # Draw nodes with different colors based on type
        node_colors = []
        node_sizes = []
        
        for node in subgraph:
            node_type = subgraph.nodes[node].get("node_type", "default")
            node_colors.append(self.node_colors.get(node_type, "#CCCCCC"))
            node_sizes.append(self.node_sizes.get(node_type, 500))
        
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        
        # Draw edges with different colors based on relationship type
        edge_colors = []
        for _, _, edge_attrs in subgraph.edges(data=True):
            rel_type = edge_attrs.get("relationship_type", "default")
            edge_colors.append(self.edge_colors.get(rel_type, self.edge_colors["default"]))
        
        nx.draw_networkx_edges(subgraph, pos, edge_color=edge_colors, width=1.5, alpha=0.7, arrows=True, arrowsize=15)
        
        # Draw node labels
        labels = {}
        for node in subgraph:
            labels[node] = subgraph.nodes[node].get("name", node)
        
        nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=10, font_weight="bold")
        
        # Create legend for node types
        legend_elements = []
        node_types_in_graph = set()
        
        for node in subgraph:
            node_types_in_graph.add(subgraph.nodes[node].get("node_type", "default"))
        
        for node_type in node_types_in_graph:
            if node_type in self.node_colors:
                legend_elements.append(
                    mpatches.Patch(color=self.node_colors[node_type], label=node_type.capitalize())
                )
        
        plt.legend(handles=legend_elements, loc="upper right")
        
        # Set title
        product_name = subgraph.nodes[product_id].get("name", product_id)
        plt.title(f"Supply Chain for {product_name}", fontsize=16)
        
        plt.axis("off")
        plt.tight_layout()
        
        # Save or show the figure
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved visualization to {save_path}")
        
        plt.show()
        
        return subgraph  # Return the subgraph for further analysis
    
    def visualize_component_origins(self, product_id: str, figsize: Tuple[int, int] = (10, 8),
                                   save_path: Optional[str] = None):
        """
        Visualize the countries of origin for components in a product
        
        Args:
            product_id: ID of the product
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the visualization
        """
        if product_id not in self.graph:
            logger.error(f"Product {product_id} not found in graph")
            return
        
        logger.info(f"Creating component origins visualization for product {product_id}")
        
        # Get product name
        product_name = self.graph.nodes[product_id].get("name", product_id)
        
        # Get components and their countries
        components_by_country = {}
        critical_by_country = {}
        
        for _, component_id, edge_attrs in self.graph.out_edges(product_id, data=True):
            if edge_attrs.get("relationship_type") == "CONTAINS":
                component_data = self.graph.nodes[component_id]
                component_name = component_data.get("name", component_id)
                
                # Get country of origin
                country = None
                for _, country_id, origin_edge in self.graph.out_edges(component_id, data=True):
                    if origin_edge.get("relationship_type") == "ORIGINATES_FROM" and country_id in self.graph:
                        country = self.graph.nodes[country_id].get("name", "Unknown")
                        break
                
                if country:
                    if country not in components_by_country:
                        components_by_country[country] = []
                        critical_by_country[country] = 0
                    
                    components_by_country[country].append(component_name)
                    
                    # Count critical components
                    if component_data.get("critical", False):
                        critical_by_country[country] += 1
        
        # Create the visualization
        plt.figure(figsize=figsize)
        
        # Sort countries by number of components
        countries = sorted(components_by_country.keys(), 
                          key=lambda x: len(components_by_country[x]), 
                          reverse=True)
        
        # Prepare data for plotting
        component_counts = [len(components_by_country[country]) for country in countries]
        critical_counts = [critical_by_country[country] for country in countries]
        
        # Create bar chart
        bar_width = 0.35
        x = np.arange(len(countries))
        
        plt.bar(x - bar_width/2, component_counts, bar_width, label="All Components", color="#1976D2")
        plt.bar(x + bar_width/2, critical_counts, bar_width, label="Critical Components", color="#D32F2F")
        
        plt.xlabel("Country of Origin")
        plt.ylabel("Number of Components")
        plt.title(f"Component Origins for {product_name}")
        plt.xticks(x, countries, rotation=45, ha="right")
        plt.legend()
        
        plt.tight_layout()
        
        # Save or show the figure
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved visualization to {save_path}")
        
        plt.show()
    
    def visualize_tariff_vulnerability(self, product_ids: List[str], figsize: Tuple[int, int] = (10, 6),
                                     save_path: Optional[str] = None):
        """
        Visualize tariff vulnerability for multiple products
        
        Args:
            product_ids: List of product IDs
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the visualization
        """
        logger.info(f"Creating tariff vulnerability visualization for {len(product_ids)} products")
        
        # Collect data for visualization
        product_names = []
        vulnerability_scores = []
        critical_component_counts = []
        tariff_vulnerable_counts = []
        
        for product_id in product_ids:
            if product_id not in self.graph:
                logger.warning(f"Product {product_id} not found in graph")
                continue
            
            product_data = self.graph.nodes[product_id]
            product_names.append(product_data.get("name", product_id))
            vulnerability_scores.append(product_data.get("tariff_vulnerability_score", 0))
            
            # Count critical and tariff-vulnerable components
            critical_count = 0
            tariff_vulnerable_count = 0
            
            for _, component_id, edge_attrs in self.graph.out_edges(product_id, data=True):
                if edge_attrs.get("relationship_type") == "CONTAINS":
                    component_data = self.graph.nodes[component_id]
                    
                    if component_data.get("critical", False):
                        critical_count += 1
                    
                    if component_data.get("tariff_vulnerable", False):
                        tariff_vulnerable_count += 1
            
            critical_component_counts.append(critical_count)
            tariff_vulnerable_counts.append(tariff_vulnerable_count)
        
        # Create the visualization
        plt.figure(figsize=figsize)
        
        # Sort data by vulnerability score
        sorted_indices = np.argsort(vulnerability_scores)[::-1]  # Descending order
        
        product_names = [product_names[i] for i in sorted_indices]
        vulnerability_scores = [vulnerability_scores[i] for i in sorted_indices]
        critical_component_counts = [critical_component_counts[i] for i in sorted_indices]
        tariff_vulnerable_counts = [tariff_vulnerable_counts[i] for i in sorted_indices]
        
        # Create bar chart
        x = np.arange(len(product_names))
        
        fig, ax1 = plt.subplots(figsize=figsize)
        
        # Plot vulnerability score as line
        color = '#1976D2'
        ax1.set_xlabel('Product')
        ax1.set_ylabel('Vulnerability Score', color=color)
        ax1.plot(x, vulnerability_scores, color=color, marker='o', linestyle='-', linewidth=2, markersize=8)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(0, max(vulnerability_scores) * 1.1)
        
        # Plot component counts as bars on secondary axis
        ax2 = ax1.twinx()
        color = '#D32F2F'
        ax2.set_ylabel('Component Count', color=color)
        ax2.bar(x - 0.2, critical_component_counts, 0.4, label='Critical', color='#FFA000', alpha=0.7)
        ax2.bar(x + 0.2, tariff_vulnerable_counts, 0.4, label='Tariff Vulnerable', color='#D32F2F', alpha=0.7)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, max(max(critical_component_counts), max(tariff_vulnerable_counts)) * 1.2)
        
        # Set x-axis ticks and labels
        plt.xticks(x, product_names, rotation=45, ha='right')
        
        # Add legend
        ax2.legend(loc='upper right')
        
        plt.title('Tariff Vulnerability Analysis')
        plt.tight_layout()
        
        # Save or show the figure
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved visualization to {save_path}")
        
        plt.show()
    
    def visualize_company_network(self, company_id: str, depth: int = 2, figsize: Tuple[int, int] = (12, 10),
                               save_path: Optional[str] = None):
        """
        Visualize a company's network of suppliers, products, and relationships
        
        Args:
            company_id: ID of the company
            depth: How many relationship hops to include
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the visualization
        """
        if company_id not in self.graph:
            logger.error(f"Company {company_id} not found in graph")
            return
        
        logger.info(f"Creating company network visualization for {company_id} with depth {depth}")
        
        # Extract subgraph around the company
        subgraph = nx.DiGraph()
        
        # Add the company node
        company_data = self.graph.nodes[company_id]
        subgraph.add_node(company_id, **company_data)
        
        # Helper function to extract a node's neighborhood
        def extract_neighborhood(node_id, current_depth, max_depth):
            if current_depth >= max_depth:
                return
            
            # Get outgoing edges
            for _, target, edge_attrs in self.graph.out_edges(node_id, data=True):
                if target not in subgraph:
                    # Add target node
                    target_data = self.graph.nodes[target]
                    subgraph.add_node(target, **target_data)
                
                # Add edge
                if not subgraph.has_edge(node_id, target):
                    subgraph.add_edge(node_id, target, **edge_attrs)
                
                # Recurse
                extract_neighborhood(target, current_depth + 1, max_depth)
            
            # Get incoming edges
            for source, _, edge_attrs in self.graph.in_edges(node_id, data=True):
                if source not in subgraph:
                    # Add source node
                    source_data = self.graph.nodes[source]
                    subgraph.add_node(source, **source_data)
                
                # Add edge
                if not subgraph.has_edge(source, node_id):
                    subgraph.add_edge(source, node_id, **edge_attrs)
                
                # Recurse
                extract_neighborhood(source, current_depth + 1, max_depth)
        
        # Extract neighborhood up to specified depth
        extract_neighborhood(company_id, 0, depth)
        
        # If the subgraph is too large, limit it
        if len(subgraph) > 50:
            logger.warning(f"Subgraph is very large ({len(subgraph)} nodes). Consider reducing depth.")
        
        # Create visualization
        plt.figure(figsize=figsize)
        
        # Use a spring layout with some randomness
        pos = nx.spring_layout(subgraph, seed=42, k=0.3)
        
        # Draw nodes with different colors based on type
        node_colors = []
        node_sizes = []
        
        for node in subgraph:
            node_type = subgraph.nodes[node].get("node_type", "default")
            node_colors.append(self.node_colors.get(node_type, "#CCCCCC"))
            node_sizes.append(self.node_sizes.get(node_type, 500))
        
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        
        # Draw edges
        edge_colors = []
        for _, _, edge_attrs in subgraph.edges(data=True):
            rel_type = edge_attrs.get("relationship_type", "default")
            edge_colors.append(self.edge_colors.get(rel_type, self.edge_colors["default"]))
        
        nx.draw_networkx_edges(subgraph, pos, edge_color=edge_colors, width=1.5, alpha=0.7, arrows=True, arrowsize=15)
        
        # Draw node labels (only for important nodes)
        labels = {}
        for node in subgraph:
            node_type = subgraph.nodes[node].get("node_type", "")
            # Only label companies, products, and selected other types
            if node_type in ["company", "product"]:
                labels[node] = subgraph.nodes[node].get("name", node)
        
        nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=10, font_weight="bold")
        
        # Create legend for node types
        legend_elements = []
        node_types_in_graph = set()
        
        for node in subgraph:
            node_types_in_graph.add(subgraph.nodes[node].get("node_type", "default"))
        
        for node_type in node_types_in_graph:
            if node_type in self.node_colors:
                legend_elements.append(
                    mpatches.Patch(color=self.node_colors[node_type], label=node_type.capitalize())
                )
        
        plt.legend(handles=legend_elements, loc="upper right")
        
        # Set title
        company_name = subgraph.nodes[company_id].get("name", company_id)
        plt.title(f"Network for {company_name}", fontsize=16)
        
        plt.axis("off")
        plt.tight_layout()
        
        # Save or show the figure
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved visualization to {save_path}")
        
        plt.show()
        
        return subgraph  # Return the subgraph for further analysis
