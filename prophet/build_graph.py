"""
build_graph.py - Script to build and save the supply chain graph
"""

import os
import pickle
import logging
from simple_graph_builder import SimpleGraphBuilder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GraphBuilder")

def main():
    """Build and save the supply chain graph"""
    logger.info("Starting graph construction")
    
    # Initialize the graph builder
    builder = SimpleGraphBuilder()
    
    # Define data files
    data_files = {
        "electronics_companies": "electronics-tech-companies.json",
        "smartphones": "product_components_smartphones.json",
        "tablets": "product_components_tablets.json",
        "laptops": "product_components_laptops.json",
        "wearables": "product_components_wearables.json",
        "gaming_consoles": "product_components_gaming_consoles.json",
        "tv_entertainment": "product_components_tv_entertainment.json"
    }
    
    # Load data files
    for data_type, file_path in data_files.items():
        if os.path.exists(file_path):
            logger.info(f"Loading {data_type} from {file_path}")
            builder.load_data_from_file(file_path, data_type)
        else:
            logger.warning(f"File not found: {file_path}")
    
    # Load additional files if they exist
    if os.path.exists('global-trade-tariffs.json'):
        logger.info("Loading trade data from global-trade-tariffs.json")
        # You'll need to implement this functionality in SimpleGraphBuilder
        # or use the GraphBuilder from your original code
        # builder.load_trade_data('global-trade-tariffs.json')
    
    if os.path.exists('supply-chain-relationships.json'):
        logger.info("Loading supply chain relationships")
        # Similar to above, this would need to be implemented
        # builder.load_relationships('supply-chain-relationships.json')
    
    # Print graph statistics
    stats = builder.get_statistics()
    logger.info(f"Graph built with {stats['nodes']} nodes and {stats['edges']} edges")
    
    # Save the graph
    output_file = "supply_chain.pickle"
    
    with open(output_file, 'wb') as f:
        pickle.dump(builder.graph, f)
    
    logger.info(f"Graph saved to {output_file}")
    logger.info(f"Node types: {builder.node_counts}")

if __name__ == "__main__":
    main()