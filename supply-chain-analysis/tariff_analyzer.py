#!/usr/bin/env python3
"""
tariff_analyzer.py - User-friendly service for running tariff analysis with Nova Prophet

This script provides a convenient interface for analyzing the impact of tariff
changes on a supply chain, with nicely formatted output and visualization.
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Import our modules
from reports.text_report import colorize, print_header, print_section, generate_text_report
from reports.html_report import generate_html_report
from reports.markdown_report import generate_markdown_report
from visualization.charts import create_charts

def run_prophet_command(args, graph_file):
    """Run a Nova Prophet CLI command and return the results as a dict."""
    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        output_file = temp_file.name
    
    # Construct the command
    cmd = [sys.executable, "scripts/prophet_cli.py"]
    cmd.extend(["--graph", graph_file])
    cmd.extend(args)
    cmd.extend(["--output", output_file])
    print("=" * 80)
    print("EXECUTING COMMAND:")
    print(" ".join(cmd))
    print("=" * 80)
    
    # Run the command
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Read the results
        with open(output_file, 'r') as f:
            results = json.load(f)
        
        # Clean up
        os.unlink(output_file)
        
        return results
    except subprocess.CalledProcessError as e:
        print(colorize(f"Error running command: {e}", "red"))
        print(colorize(f"Command output: {e.stdout.decode('utf-8')}", "red"))
        print(colorize(f"Command error: {e.stderr.decode('utf-8')}", "red"))
        return None
    except Exception as e:
        print(colorize(f"Error: {e}", "red"))
        if os.path.exists(output_file):
            os.unlink(output_file)
        return None

def analyze_tariff_impact(country, increase_percentage, component_types=None, graph_file=None, output_format="text"):
    """Run a tariff impact analysis and display the results nicely."""
    print_header(f"TARIFF IMPACT ANALYSIS: {country} {increase_percentage:+}%")
    
    # Set up the command
    cmd = ["predict", "tariff", "--country", country, "--increase", str(increase_percentage)]
    if component_types:
        cmd.extend(["--components"] + component_types)
    
    # Run the command
    results = run_prophet_command(cmd, graph_file)
    if not results:
        print(colorize("Failed to run tariff impact analysis.", "red"))
        return
    
    # Generate charts for visualization
    charts_data = create_charts(results)
    
    # Display the report in the desired format
    if output_format.lower() == "html":
        report_file = generate_html_report(country, results, charts_data)
        print(f"\nHTML report generated: {colorize(str(report_file), 'green')}")
    elif output_format.lower() == "markdown":
        report_file = generate_markdown_report(country, results, charts_data)
        print(f"\nMarkdown report generated: {colorize(str(report_file), 'green')}")
    else:
        # Default to text report in console
        generate_text_report(country, increase_percentage, results, charts_data)

def compare_tariff_scenarios(scenarios, graph_file=None, output_format="text"):
    """Compare multiple tariff scenarios and display the results side by side."""
    print_header("TARIFF SCENARIO COMPARISON")
    
    # Run each scenario
    scenario_results = []
    for scenario in scenarios:
        print(f"Running scenario: {scenario['name']}...")
        cmd = ["predict", "tariff", "--country", scenario['country'], "--increase", str(scenario['increase'])]
        if 'components' in scenario and scenario['components']:
            cmd.extend(["--components"] + scenario['components'])
        
        results = run_prophet_command(cmd, graph_file)
        if results:
            results['scenario_name'] = scenario['name']
            scenario_results.append(results)
    
    if not scenario_results:
        print(colorize("Failed to run any scenarios.", "red"))
        return
    
    # Generate charts for visualization
    charts_data = create_charts(scenario_results, is_comparison=True)
    
    # Display the report in the desired format
    if output_format.lower() == "html":
        from reports.html_report import generate_html_comparison_report
        report_file = generate_html_comparison_report(scenario_results, charts_data)
        print(f"\nHTML comparison report generated: {colorize(str(report_file), 'green')}")
    elif output_format.lower() == "markdown":
        from reports.markdown_report import generate_markdown_comparison_report
        report_file = generate_markdown_comparison_report(scenario_results, charts_data)
        print(f"\nMarkdown comparison report generated: {colorize(str(report_file), 'green')}")
    else:
        # Default to text report in console
        from reports.text_report import generate_text_comparison_report
        generate_text_comparison_report(scenario_results, charts_data)

def export_tariff_vulnerability_report(country, graph_file=None, output_format="text"):
    """Generate and export a tariff vulnerability report for a specific country."""
    print_header(f"TARIFF VULNERABILITY ANALYSIS: {country}")
    
    # Run the vulnerability analysis
    cmd = ["analyze", "tariff-vulnerability", "--country", country]
    results = run_prophet_command(cmd, graph_file)
    if not results:
        print(colorize("Failed to run tariff vulnerability analysis.", "red"))
        return
    
    # Display basic information in console
    print_section("VULNERABILITY OVERVIEW")
    print(f"Country: {colorize(country, 'yellow')}")
    print(f"Affected Components: {colorize(str(results.get('affected_components_count', 0)), 'yellow')}")
    print(f"Affected Products: {colorize(str(results.get('affected_products_count', 0)), 'yellow')}")
    print(f"Affected Companies: {colorize(str(results.get('affected_companies_count', 0)), 'yellow')}")
    
    # Generate charts for visualization
    charts_data = create_charts(results, is_vulnerability=True)
    
    # Generate and save the report
    if output_format.lower() == "html":
        from reports.html_report import generate_html_vulnerability_report
        report_file = generate_html_vulnerability_report(country, results, charts_data)
        print(f"\nHTML vulnerability report generated: {colorize(str(report_file), 'green')}")
    elif output_format.lower() == "markdown":
        from reports.markdown_report import generate_markdown_vulnerability_report
        report_file = generate_markdown_vulnerability_report(country, results, charts_data)
        print(f"\nMarkdown vulnerability report generated: {colorize(str(report_file), 'green')}")
    elif output_format.lower() == "json":
        # Save the raw JSON
        export_dir = Path("./reports")
        export_dir.mkdir(exist_ok=True)
        filename = f"tariff_vulnerability_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"{export_dir}/{filename}", 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nJSON report saved to: {colorize(f'{export_dir}/{filename}', 'green')}")
    else:
        # Text report
        from reports.text_report import generate_text_vulnerability_report
        report_file = generate_text_vulnerability_report(country, results)
        print(f"\nText vulnerability report generated: {colorize(str(report_file), 'green')}")

def main():
    """Main entry point for the tariff analyzer."""
    parser = argparse.ArgumentParser(
        description="User-friendly Tariff Analysis Service for Nova Prophet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tariff_analyzer.py analyze --country China --increase 25
  python tariff_analyzer.py analyze --country "United States" --increase -10 --components semiconductors displays --format html
  python tariff_analyzer.py compare --scenarios "scenarios.json" --format markdown
  python tariff_analyzer.py vulnerability --country Taiwan --format html
        """
    )
    
    parser.add_argument('--graph', default='output/supply_chain.pickle', help='Path to supply chain graph file')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze impact of a tariff change')
    analyze_parser.add_argument('--country', required=True, help='Country implementing the tariff')
    analyze_parser.add_argument('--increase', type=float, required=True, help='Percentage increase in tariffs')
    analyze_parser.add_argument('--components', nargs='+', help='Optional list of component types affected')
    analyze_parser.add_argument('--format', choices=['text', 'html', 'markdown'], default='text', help='Output format')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple tariff scenarios')
    compare_parser.add_argument('--scenarios', required=True, help='JSON file with scenario definitions or comma-separated scenario strings')
    compare_parser.add_argument('--format', choices=['text', 'html', 'markdown'], default='text', help='Output format')
    
    # Vulnerability command
    vulnerability_parser = subparsers.add_parser('vulnerability', help='Generate tariff vulnerability report')
    vulnerability_parser.add_argument('--country', required=True, help='Country to analyze')
    vulnerability_parser.add_argument('--format', choices=['text', 'markdown', 'html', 'json'], default='text', help='Output format')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if a command was specified
    if not args.command:
        parser.print_help()
        return
    
    # Check if the graph file exists
    if not os.path.exists(args.graph):
        print(colorize(f"Error: Graph file not found: {args.graph}", "red"))
        print("Make sure to build your supply chain graph first using 'build_graph.py'")
        return
    
    # Handle commands
    if args.command == 'analyze':
        analyze_tariff_impact(
            graph_file=args.graph,
            country=args.country,
            increase_percentage=args.increase,
            component_types=args.components,
            output_format=args.format
        )
    
    elif args.command == 'compare':
        # Parse scenarios
        if os.path.exists(args.scenarios) and args.scenarios.endswith('.json'):
            # Load scenarios from JSON file
            try:
                with open(args.scenarios, 'r') as f:
                    scenarios = json.load(f)
                if not isinstance(scenarios, list):
                    scenarios = [scenarios]
            except Exception as e:
                print(colorize(f"Error loading scenarios file: {e}", "red"))
                return
        else:
            # Parse comma-separated scenario strings
            # Format: "name:country:increase[:components]"
            # Example: "China25:China:25:processors,displays"
            try:
                scenario_strings = args.scenarios.split(',')
                scenarios = []
                
                for scenario_str in scenario_strings:
                    parts = scenario_str.split(':')
                    if len(parts) < 3:
                        print(colorize(f"Invalid scenario format: {scenario_str}", "red"))
                        continue
                    
                    scenario = {
                        'name': parts[0],
                        'country': parts[1],
                        'increase': float(parts[2])
                    }
                    
                    if len(parts) > 3 and parts[3]:
                        scenario['components'] = parts[3].split(',')
                    
                    scenarios.append(scenario)
            except Exception as e:
                print(colorize(f"Error parsing scenarios: {e}", "red"))
                return
        
        if not scenarios:
            print(colorize("No valid scenarios found.", "red"))
            return
        
        compare_tariff_scenarios(scenarios, graph_file=args.graph, output_format=args.format)
    
    elif args.command == 'vulnerability':
        export_tariff_vulnerability_report(
            country=args.country,
            graph_file=args.graph,
            output_format=args.format
        )
        
if __name__ == "__main__":
    # Check for matplotlib
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print(colorize("Warning: matplotlib not found. Visualizations will be disabled.", "yellow"))
        print("To install required packages, run: pip install matplotlib numpy tabulate")
    
    # Check for tabulate
    try:
        from tabulate import tabulate
    except ImportError:
        print(colorize("Error: tabulate package not found.", "red"))
        print("To install required packages, run: pip install tabulate")
        sys.exit(1)
    
    main()
