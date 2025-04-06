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
import pickle
from datetime import datetime
from pathlib import Path

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

def load_graph(graph_file):
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
    
    # 1.2 Analyze resilience
    resilience_parser = analyze_subparsers.add_parser('resilience', help='Analyze supply chain resilience')
    resilience_parser.add_argument('--company', help='Optional company ID to focus on')
    resilience_parser.add_argument('--output', help='Output file for the report')
    
    # 1.3 Analyze critical components
    critical_parser = analyze_subparsers.add_parser('critical', help='Identify critical components')
    critical_parser.add_argument('--company', help='Optional company ID to focus on')
    critical_parser.add_argument('--threshold', type=float, default=0.7, help='Criticality threshold (0.0-1.0)')
    critical_parser.add_argument('--output', help='Output file for the report')
    
    # 1.4 Analyze geographical
    geo_parser = analyze_subparsers.add_parser('geographical', help='Analyze geographical concentration')
    geo_parser.add_argument('--output', help='Output file for the report')
    
    # 1.5 Analyze single points
    spof_parser = analyze_subparsers.add_parser('single-points', help='Identify single points of failure')
    spof_parser.add_argument('--output', help='Output file for the report')
    
    # 1.6 Analyze tariff vulnerability
    tariff_vuln_parser = analyze_subparsers.add_parser('tariff-vulnerability', help='Assess tariff vulnerability')
    tariff_vuln_parser.add_argument('--country', help='Optional country to focus on')
    tariff_vuln_parser.add_argument('--output', help='Output file for the report')
    
    # 2. Predict command
    predict_parser = subparsers.add_parser('predict', help='Run predictions on the supply chain')
    predict_subparsers = predict_parser.add_subparsers(dest='predict_type', help='Type of prediction')
    
    # 2.1 Predict tariff impacts
    tariff_parser = predict_subparsers.add_parser('tariff', help='Predict impact of tariff changes')
    tariff_parser.add_argument('--country', required=True, help='Country implementing the tariff')
    tariff_parser.add_argument('--increase', type=float, required=True, help='Percentage increase in tariffs')
    tariff_parser.add_argument('--components', nargs='+', help='Optional list of component types affected')
    tariff_parser.add_argument('--output', help='Output file for the results')
    
    # 2.2 Predict supplier disruption
    disruption_parser = predict_subparsers.add_parser('disruption', help='Predict impact of supplier disruption')
    disruption_parser.add_argument('--supplier', required=True, help='ID of the affected supplier')
    disruption_parser.add_argument('--level', choices=['partial', 'complete'], default='complete', help='Level of disruption')
    disruption_parser.add_argument('--duration', type=int, default=3, help='Duration in months')
    disruption_parser.add_argument('--output', help='Output file for the results')
    
    # 2.3 Predict geopolitical event
    geopolitical_parser = predict_subparsers.add_parser('geopolitical', help='Predict impact of geopolitical event')
    geopolitical_parser.add_argument('--country', required=True, help='Affected country')
    geopolitical_parser.add_argument('--event-type', required=True, 
                                    choices=['trade_restriction', 'conflict', 'natural_disaster', 'political_change'],
                                    help='Type of event')
    geopolitical_parser.add_argument('--severity', choices=['low', 'medium', 'high'], default='medium', help='Severity of event')
    geopolitical_parser.add_argument('--duration', type=int, default=6, help='Duration in months')
    geopolitical_parser.add_argument('--output', help='Output file for the results')
    
    # 2.4 Predict component shortage
    shortage_parser = predict_subparsers.add_parser('shortage', help='Predict impact of component shortage')
    shortage_parser.add_argument('--component-type', required=True, help='Type of component experiencing shortage')
    shortage_parser.add_argument('--level', choices=['moderate', 'severe'], default='severe', help='Level of shortage')
    shortage_parser.add_argument('--duration', type=int, default=6, help='Duration in months')
    shortage_parser.add_argument('--output', help='Output file for the results')
    
    # 2.5 Generate optimization recommendations
    optimize_parser = predict_subparsers.add_parser('optimize', help='Generate optimization recommendations')
    optimize_parser.add_argument('--company', help='Optional company ID to focus recommendations on')
    optimize_parser.add_argument('--output', help='Output file for the results')
    
    # 2.6 Find alternative sources
    alternatives_parser = predict_subparsers.add_parser('alternatives', help='Find alternative sources for a component')
    alternatives_parser.add_argument('--component', required=True, help='ID of the component')
    alternatives_parser.add_argument('--max', type=int, default=5, help='Maximum number of alternatives to find')
    alternatives_parser.add_argument('--output', help='Output file for the results')
    
    # 3. Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_subparsers = report_parser.add_subparsers(dest='report_type', help='Type of report')
    
    # 3.1 Comprehensive report
    comprehensive_parser = report_subparsers.add_parser('comprehensive', help='Generate comprehensive analysis')
    comprehensive_parser.add_argument('--company', help='Optional company ID to focus on')
    comprehensive_parser.add_argument('--output-dir', default='output/comprehensive', help='Directory for output files')
    comprehensive_parser.add_argument('--no-scenarios', action='store_true', help='Skip scenario analysis')
    
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
    
    # Make sure logs directory exists
    logs_dir = Path(__file__).parent.parent / 'logs'
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    
    # Load the graph
    try:
        # Add the src directory to Python path for imports
        sys.path.append(str(Path(__file__).parent.parent / 'src'))
        
        graph = load_graph(args.graph)
    except Exception as e:
        print(f"Error loading graph: {e}")
        return
    
    # Initialize modules
    try:
        # Import required modules with proper path handling
        sys.path.append(str(Path(__file__).parent.parent))
        
        # Import Veritas analyzer
        from veritas import SupplyChainAnalyzer, InsightExtractor
        analyzer = SupplyChainAnalyzer(graph)
        
        # Import Nova Prophet prediction engine
        from prophet.prediction_engine import PredictionEngine
        engine = PredictionEngine(graph, analyzer)
        
        logger.info("Initialized analysis and prediction modules")
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        print(f"Error: {e}")
        print("Make sure you're running this script from the proper location and all dependencies are installed.")
        return
    except Exception as e:
        logger.error(f"Error initializing modules: {e}")
        print(f"Error: {e}")
        return
    
    # Handle analyze commands
    if args.command == 'analyze':
        if not args.analyze_type:
            logger.error("No analyze type specified")
            analyze_parser.print_help()
            return
        
        if args.analyze_type == 'company':
            logger.info(f"Analyzing company: {args.company_id}")
            
            extractor = InsightExtractor(analyzer)
            report = extractor.generate_summary_report(company_id=args.company_id)
            
            output_file = args.output
            if not output_file:
                output_file = output_dir / f"company_analysis_{args.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == 'json':
                from veritas import save_report_to_json
                save_report_to_json(report, str(output_file))
            else:
                from veritas import save_report_to_markdown
                save_report_to_markdown(report, str(output_file))
            
            logger.info(f"Company analysis saved to {output_file}")
            print(f"Analysis complete. Results saved to {output_file}")
        
        elif args.analyze_type == 'resilience':
            logger.info("Analyzing supply chain resilience")
            resilience = analyzer.calculate_resilience_score(company_id=args.company)
            
            output_file = args.output
            if not output_file:
                suffix = f"_{args.company}" if args.company else ""
                output_file = output_dir / f"resilience_analysis{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(output_file), 'w') as f:
                json.dump(resilience, f, indent=2)
            
            logger.info(f"Resilience analysis saved to {output_file}")
            print(f"Resilience score: {resilience['total_resilience_score']}/100 ({resilience['risk_level']} risk)")
            print(f"Results saved to {output_file}")
        
        elif args.analyze_type == 'critical':
            logger.info("Identifying critical components")
            critical_components = analyzer.find_critical_components(
                manufacturer_id=args.company,
                threshold=args.threshold
            )
            
            output_file = args.output
            if not output_file:
                suffix = f"_{args.company}" if args.company else ""
                output_file = output_dir / f"critical_components{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(output_file), 'w') as f:
                json.dump(critical_components, f, indent=2)
            
            logger.info(f"Critical components analysis saved to {output_file}")
            print(f"Found {len(critical_components)} critical components with threshold {args.threshold}")
            print(f"Results saved to {output_file}")
        
        elif args.analyze_type == 'geographical':
            logger.info("Analyzing geographical concentration")
            geo_concentration = analyzer.identify_geographical_concentration()
            
            output_file = args.output
            if not output_file:
                output_file = output_dir / f"geographical_concentration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(output_file), 'w') as f:
                json.dump(geo_concentration, f, indent=2)
            
            logger.info(f"Geographical concentration analysis saved to {output_file}")
            print(f"Analyzed geographical concentration across {len(geo_concentration['country_concentration'])} countries")
            print(f"Results saved to {output_file}")
        
        elif args.analyze_type == 'single-points':
            logger.info("Identifying single points of failure")
            single_points = analyzer.detect_single_points_of_failure()
            
            output_file = args.output
            if not output_file:
                output_file = output_dir / f"single_points_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(output_file), 'w') as f:
                json.dump(single_points, f, indent=2)
            
            logger.info(f"Single points of failure analysis saved to {output_file}")
            print(f"Found {len(single_points)} single points of failure")
            print(f"Results saved to {output_file}")
        
        elif args.analyze_type == 'tariff-vulnerability':
            logger.info("Assessing tariff vulnerability")
            tariff_vulnerability = analyzer.assess_tariff_vulnerability(country=args.country)
            
            output_file = args.output
            if not output_file:
                suffix = f"_{args.country}" if args.country else ""
                output_file = output_dir / f"tariff_vulnerability{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(output_file), 'w') as f:
                json.dump(tariff_vulnerability, f, indent=2)
            
            logger.info(f"Tariff vulnerability assessment saved to {output_file}")
            print(f"Found {tariff_vulnerability['affected_components_count']} components vulnerable to tariffs")
            print(f"Affecting {tariff_vulnerability['affected_products_count']} products")
            print(f"Results saved to {output_file}")
    
    # Handle predict commands
    elif args.command == 'predict':
        if not args.predict_type:
            logger.error("No prediction type specified")
            predict_parser.print_help()
            return
        
        if args.predict_type == 'tariff':
            logger.info(f"Predicting tariff impacts for {args.country} with {args.increase}% increase")
            results = engine.predict_tariff_impact(
                country=args.country,
                increase_percentage=args.increase,
                affected_component_types=args.components,
                output_file=args.output
            )
            logger.info(f"Tariff prediction completed")
            
            # Print summary results
            print(f"Tariff Impact Prediction Results:")
            print(f"- {args.country} tariff increase of {args.increase}%")
            print(f"- Affected components: {results['affected_components_count']}")
            print(f"- Affected products: {results['affected_products_count']}")
            print(f"- Average price increase: {results['price_impacts'].get('average_product_price_increase', 0)}%")
            print(f"- Resilience score change: {results['resilience_impact']['change']}")
            
            if args.output:
                print(f"Full results saved to {args.output}")
        
        elif args.predict_type == 'disruption':
            logger.info(f"Predicting supplier disruption for {args.supplier}")
            results = engine.predict_supplier_disruption(
                supplier_id=args.supplier,
                disruption_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            logger.info(f"Supplier disruption prediction completed")
            
            # Print summary results
            print(f"Supplier Disruption Prediction Results:")
            print(f"- {args.level} disruption of supplier {results.get('supplier_name', args.supplier)} for {args.duration} months")
            print(f"- Affected components: {results.get('affected_components_count', 0)}")
            print(f"- Affected products: {results.get('affected_products_count', 0)}")
            if 'lead_time_impacts' in results:
                print(f"- Average lead time increase: {results['lead_time_impacts'].get('average_lead_time_increase_weeks', 0)} weeks")
            print(f"- Resilience score change: {results.get('resilience_impact', {}).get('change', 0)}")
            
            if args.output:
                print(f"Full results saved to {args.output}")
        
        elif args.predict_type == 'geopolitical':
            logger.info(f"Predicting impact of {args.severity} {args.event_type} in {args.country}")
            results = engine.predict_geopolitical_event(
                country=args.country,
                event_type=args.event_type,
                severity=args.severity,
                duration_months=args.duration,
                output_file=args.output
            )
            logger.info(f"Geopolitical event prediction completed")
            
            # Print summary results
            print(f"Geopolitical Event Prediction Results:")
            print(f"- {args.severity} {args.event_type} in {args.country} for {args.duration} months")
            print(f"- Affected components: {results.get('affected_components_count', 0)}")
            print(f"- Affected products: {results.get('affected_products_count', 0)}")
            if 'impact_assessment' in results:
                print(f"- Overall impact level: {results['impact_assessment'].get('overall_impact_level', 'unknown')}")
            print(f"- Resilience score change: {results.get('resilience_impact', {}).get('change', 0)}")
            
            if args.output:
                print(f"Full results saved to {args.output}")
        
        elif args.predict_type == 'shortage':
            logger.info(f"Predicting impact of {args.level} shortage of {args.component_type}")
            # Use simpler arg name for function
            component_type = getattr(args, 'component_type', None)
            if not component_type:
                component_type = getattr(args, 'component-type', None)
                
            results = engine.predict_component_shortage(
                component_type=component_type,
                shortage_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            logger.info(f"Component shortage prediction completed")
            
            # Print summary results
            print(f"Component Shortage Prediction Results:")
            print(f"- {args.level} shortage of {component_type} for {args.duration} months")
            print(f"- Affected components: {results.get('affected_components_count', 0)}")
            print(f"- Affected products: {results.get('affected_products_count', 0)}")
            if 'impact_assessment' in results:
                print(f"- Average price increase: {results['impact_assessment'].get('average_price_increase', 0)}%")
                print(f"- Average lead time increase: {results['impact_assessment'].get('average_lead_time_increase', 0)} weeks")
            print(f"- Resilience score change: {results.get('resilience_impact', {}).get('change', 0)}")
            
            if args.output:
                print(f"Full results saved to {args.output}")
        
        elif args.predict_type == 'optimize':
            logger.info(f"Generating optimization recommendations")
            results = engine.generate_recommendations(
                company_id=args.company,
                output_file=args.output
            )
            logger.info(f"Optimization recommendations generated")
            
            # Print summary results
            print(f"Optimization Recommendations:")
            print(f"- Company: {results.get('company_id', 'All companies')}")
            print(f"- Resilience score: {results.get('resilience_score', 0)}/100 ({results.get('risk_level', 'unknown')} risk)")
            print(f"- Top recommendations: {len(results.get('recommendations', []))}")
            
            if 'recommendations' in results and len(results['recommendations']) > 0:
                print(f"\nTop recommendation:")
                print(f"- {results['recommendations'][0]['description']}")
            
            if args.output:
                print(f"Full results saved to {args.output}")
        
        elif args.predict_type == 'alternatives':
            logger.info(f"Finding alternative sources for component {args.component}")
            # Use simpler arg name for function
            max_alternatives = getattr(args, 'max', 5)
                
            results = engine.find_alternative_sources(
                component_id=args.component,
                max_alternatives=max_alternatives,
                output_file=args.output
            )
            logger.info(f"Alternative sources identified")
            
            # Print summary results
            print(f"Alternative Sources Results:")
            print(f"- Component: {results.get('component_name', args.component)}")
            print(f"- Alternatives found: {len(results.get('alternatives', []))}")
            
            if 'alternatives' in results and len(results['alternatives']) > 0:
                print(f"\nTop alternatives:")
                for i, alt in enumerate(results['alternatives'][:3]):
                    print(f"- {i+1}. {alt.get('component_name', 'Unknown')} (similarity: {alt.get('similarity_score', 0)})")
            
            if args.output:
                print(f"Full results saved to {args.output}")
    
    # Handle report commands
    elif args.command == 'report':
        if not args.report_type:
            logger.error("No report type specified")
            report_parser.print_help()
            return
        
        if args.report_type == 'comprehensive':
            logger.info(f"Generating comprehensive analysis")
            include_scenarios = not args.no_scenarios
            results = engine.run_comprehensive_analysis(
                company_id=args.company,
                output_dir=args.output_dir,
                include_scenarios=include_scenarios
            )
            logger.info(f"Comprehensive analysis completed and saved to {args.output_dir}")
            
            company_name = results.get('company_name', 'All companies')
            
            # Print summary results
            print(f"Comprehensive Analysis Results for {company_name}:")
            print(f"- Resilience score: {results.get('baseline', {}).get('resilience_score', 0)}/100 ({results.get('baseline', {}).get('risk_level', 'unknown')} risk)")
            print(f"- Critical components: {results.get('baseline', {}).get('critical_components_count', 0)}")
            print(f"- Single points of failure: {results.get('baseline', {}).get('single_points_count', 0)}")
            
            if 'top_insights' in results:
                insights = results['top_insights']
                if 'critical_components' in insights and insights['critical_components']:
                    print(f"\nCritical components: {', '.join(insights['critical_components'])}")
                if 'high_risk_suppliers' in insights and insights['high_risk_suppliers']:
                    print(f"High risk suppliers: {', '.join(insights['high_risk_suppliers'])}")
                if 'high_risk_countries' in insights and insights['high_risk_countries']:
                    print(f"High risk countries: {', '.join(insights['high_risk_countries'])}")
            
            if 'scenarios' in results and results['scenarios']:
                print(f"\nScenario Analysis:")
                for scenario in results['scenarios']:
                    print(f"- {scenario['type']}: {scenario['impact_level']} impact")
            
            print(f"\nResults saved to {args.output_dir}")
    
    logger.info("Nova Prophet CLI command completed successfully")


if __name__ == "__main__":
    main()
