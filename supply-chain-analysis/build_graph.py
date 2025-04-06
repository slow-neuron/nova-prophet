"""
build_graph.py - Script to build and save the supply chain graph
"""

import os
import pickle
import logging
import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from simple_graph_builder import SimpleGraphBuilder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GraphBuilder")

def main():
    """Build and save the supply chain graph"""
    logger.info("Starting graph construction")
    
    # Initialize the graph builder
    builder = SimpleGraphBuilder()
    
    # Define data directory
    data_dir = Path(__file__).parent.parent / 'data'
    output_dir = Path(__file__).parent.parent / 'output'
    
    # Create output directory if it doesn't exist
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        logger.info(f"Created output directory: {output_dir}")
    
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
    for data_type, file_name in data_files.items():
        file_path = data_dir / file_name
        if file_path.exists():
            logger.info(f"Loading {data_type} from {file_path}")
            builder.load_data_from_file(str(file_path), data_type)
        else:
            logger.warning(f"File not found: {file_path}")
    
    # Load additional files if they exist
    tariff_file = data_dir / 'global-trade-tariffs.json'
    if tariff_file.exists():
        logger.info(f"Loading trade data from {tariff_file}")
        # You'll need to implement this functionality in SimpleGraphBuilder
        # or use the GraphBuilder from your original code
        # builder.load_trade_data(str(tariff_file))
    
    relationships_file = data_dir / 'supply-chain-relationships.json'
    if relationships_file.exists():
        logger.info(f"Loading supply chain relationships from {relationships_file}")
        # Similar to above, this would need to be implemented
        # builder.load_relationships(str(relationships_file))
    
    # Print graph statistics
    stats = builder.get_statistics()
    logger.info(f"Graph built with {stats['nodes']} nodes and {stats['edges']} edges")
    
    # Save the graph
    output_file = output_dir / "supply_chain.pickle"
    
    with open(output_file, 'wb') as f:
        pickle.dump(builder.graph, f)
    
    logger.info(f"Graph saved to {output_file}")
    logger.info(f"Node types: {builder.node_counts}")

if __name__ == "__main__":
    main()
