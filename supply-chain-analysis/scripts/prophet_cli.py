#!/usr/bin/env python3
"""
prophet_cli.py - Command Line Interface for Nova Prophet

This script provides a command-line interface to the Nova Prophet
supply chain prediction system.
"""

import argparse
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path(__file__).parent.parent / "logs" / "nova_prophet.log"), mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NovaProphet.CLI")

def main():
    """Main entry point for the CLI"""
    
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description='Nova Prophet - Supply Chain Prediction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prophet_cli.py analyze company EC001 --graph output/supply_chain.pickle
  python prophet_cli.py predict tariff --country China --increase 25 --graph output/supply_chain.pickle
  python prophet_cli.py predict disruption --supplier EC006 --graph output/supply_chain.pickle
  python prophet_cli.py predict optimize --company EC001 --graph output/supply_chain.pickle
  python prophet_cli.py report comprehensive --company EC001 --graph output/supply_chain.pickle
        """
    )
    
    parser.add_argument('--version', action='version', version='Nova Prophet v0.1.0')
    parser.add_argument('--graph', help='Path to pickled NetworkX graph file (required for all commands)')
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # 1. Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run Veritas analysis on the supply chain')
    analyze_subparsers = analyze_parser.add_subparsers(dest='analyze_type', help='Type of analysis')
    
    # 1.1 Analyze company
    company_parser = analyze_subparsers.add_parser('company', help='Analyze a specific company')
    company_parser.add_argument('company_id', help='ID of the company to analyze')
    company_parser.add_argument('--output', help='Output file for the report')
    company_parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='Output format')
    
    # ... rest of your argument definitions ...
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if a command was specified
    if not args.command:
        parser.print_help()
        return
    
    # Check if graph path was provided
    if not args.graph:
        print("Error: --graph argument is required")
        return
    
    # Set default output directory
    output_dir = Path(__file__).parent.parent / 'output'
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Load the graph
    try:
        # Import from the new location
        from prophet.prediction_engine import load_graph
        graph = load_graph(args.graph)
    except Exception as e:
        print(f"Error loading graph: {e}")
        return
    
    # ... rest of your command handling ...

    # The rest of your main function content would follow here, with paths adjusted
    # to use the output_dir variable where needed.


if __name__ == "__main__":
    main()
