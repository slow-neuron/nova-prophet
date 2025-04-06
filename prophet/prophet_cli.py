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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nova_prophet.log"),
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
  python prophet_cli.py analyze company EC001 --graph supply_chain.pickle
  python prophet_cli.py predict tariff --country China --increase 25 --graph supply_chain.pickle
  python prophet_cli.py predict disruption --supplier EC006 --graph supply_chain.pickle
  python prophet_cli.py predict optimize --company EC001 --graph supply_chain.pickle
  python prophet_cli.py report comprehensive --company EC001 --graph supply_chain.pickle
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
    
    # 1.2 Analyze component
    component_parser = analyze_subparsers.add_parser('component', help='Analyze a specific component')
    component_parser.add_argument('component_id', help='ID of the component to analyze')
    component_parser.add_argument('--output', help='Output file for the report')
    
    # 1.3 Analyze product
    product_parser = analyze_subparsers.add_parser('product', help='Analyze a specific product')
    product_parser.add_argument('product_id', help='ID of the product to analyze')
    product_parser.add_argument('--output', help='Output file for the report')
    
    # 1.4 Analyze vulnerabilities
    vuln_parser = analyze_subparsers.add_parser('vulnerabilities', help='Find vulnerabilities in the supply chain')
    vuln_parser.add_argument('--threshold', type=float, default=0.7, help='Criticality threshold (0.0-1.0)')
    vuln_parser.add_argument('--output', help='Output file for the report')
    
    # 2. Predict command
    predict_parser = subparsers.add_parser('predict', help='Run Nova Prophet predictions')
    predict_subparsers = predict_parser.add_subparsers(dest='predict_type', help='Type of prediction')
    
    # 2.1 Predict tariff changes
    tariff_parser = predict_subparsers.add_parser('tariff', help='Predict impact of tariff changes')
    tariff_parser.add_argument('--country', required=True, help='Country implementing the tariff')
    tariff_parser.add_argument('--increase', type=float, required=True, help='Percentage increase in tariffs')
    tariff_parser.add_argument('--components', nargs='+', help='Component types affected (optional)')
    tariff_parser.add_argument('--output', help='Output file for the results')
    
    # 2.2 Predict supplier disruption
    disruption_parser = predict_subparsers.add_parser('disruption', help='Predict impact of supplier disruption')
    disruption_parser.add_argument('--supplier', required=True, help='ID of the supplier')
    disruption_parser.add_argument('--level', choices=['partial', 'complete'], default='complete', help='Disruption level')
    disruption_parser.add_argument('--duration', type=int, default=3, help='Disruption duration in months')
    disruption_parser.add_argument('--output', help='Output file for the results')
    
    # 2.3 Predict geopolitical event
    geo_parser = predict_subparsers.add_parser('geopolitical', help='Predict impact of geopolitical event')
    geo_parser.add_argument('--country', required=True, help='Affected country')
    geo_parser.add_argument('--event', choices=['trade_restriction', 'conflict', 'natural_disaster', 'political_change'], 
                           required=True, help='Type of event')
    geo_parser.add_argument('--severity', choices=['low', 'medium', 'high'], default='medium', help='Event severity')
    geo_parser.add_argument('--duration', type=int, default=6, help='Event duration in months')
    geo_parser.add_argument('--output', help='Output file for the results')
    
    # 2.4 Predict component shortage
    shortage_parser = predict_subparsers.add_parser('shortage', help='Predict impact of component shortage')
    shortage_parser.add_argument('--component-type', required=True, help='Type of component experiencing shortage')
    shortage_parser.add_argument('--level', choices=['moderate', 'severe'], default='severe', help='Shortage level')
    shortage_parser.add_argument('--duration', type=int, default=6, help='Shortage duration in months')
    shortage_parser.add_argument('--output', help='Output file for the results')
    
    # 2.5 Predict optimization recommendations
    optimize_parser = predict_subparsers.add_parser('optimize', help='Generate optimization recommendations')
    optimize_parser.add_argument('--company', help='Company ID (optional)')
    optimize_parser.add_argument('--output', help='Output file for the results')
    
    # 2.6 Find alternatives
    alternatives_parser = predict_subparsers.add_parser('alternatives', help='Find alternative sources for component')
    alternatives_parser.add_argument('--component', required=True, help='Component ID')
    alternatives_parser.add_argument('--max', type=int, default=5, help='Maximum number of alternatives')
    alternatives_parser.add_argument('--output', help='Output file for the results')
    
    # 3. Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_subparsers = report_parser.add_subparsers(dest='report_type', help='Type of report')
    
    # 3.1 Comprehensive report
    comprehensive_parser = report_subparsers.add_parser('comprehensive', help='Generate comprehensive report')
    comprehensive_parser.add_argument('--company', help='Company ID (optional)')
    comprehensive_parser.add_argument('--output-dir', default='output/comprehensive', help='Output directory')
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
    
    # Load the graph
    try:
        from prophet.prediction_engine import load_graph
        graph = load_graph(args.graph)
    except Exception as e:
        print(f"Error loading graph: {e}")
        return
    
    # Handle analyze commands
    if args.command == 'analyze':
        from veritas import SupplyChainAnalyzer, InsightExtractor
        
        analyzer = SupplyChainAnalyzer(graph)
        extractor = InsightExtractor(analyzer)
        
        if args.analyze_type == 'company':
            # Generate company report
            report = extractor.generate_summary_report(args.company_id)
            
            # Save report
            if args.format == 'json':
                from prophet.utils import save_scenario_results
                output_file = args.output or f"output/company_analysis_{args.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                save_scenario_results(report, output_file)
                print(f"Company analysis saved to {output_file}")
            else:
                from veritas import save_report_to_markdown
                output_file = args.output or f"output/company_analysis_{args.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                save_report_to_markdown(report, output_file)
                print(f"Company analysis saved to {output_file}")
        
        elif args.analyze_type == 'component':
            # Analyze component
            from prophet.utils import calculate_component_criticality, find_alternative_components
            
            if args.component_id not in graph:
                print(f"Error: Component {args.component_id} not found in graph")
                return
            
            component_data = graph.nodes[args.component_id]
            
            # Find products using this component
            products_using = []
            for source, target, edge_data in graph.in_edges(args.component_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    product_name = graph.nodes[source].get('name', 'Unknown')
                    products_using.append({
                        'product_id': source,
                        'product_name': product_name
                    })
            
            # Find suppliers
            suppliers = []
            for source, target, edge_data in graph.in_edges(args.component_id, data=True):
                if edge_data.get('relationship_type') == 'SUPPLIES':
                    supplier_name = graph.nodes[source].get('name', 'Unknown')
                    suppliers.append({
                        'supplier_id': source,
                        'supplier_name': supplier_name
                    })
            
            # Calculate criticality
            criticality = calculate_component_criticality(graph, args.component_id)
            
            # Find alternatives
            alternatives = find_alternative_components(graph, args.component_id)
            
            # Create report
            report = {
                'component_id': args.component_id,
                'component_name': component_data.get('name', 'Unknown'),
                'criticality_score': criticality,
                'risk_level': 'high' if criticality > 0.7 else 'medium' if criticality > 0.4 else 'low',
                'products_using': products_using,
                'suppliers': suppliers,
                'alternatives': alternatives,
                'tariff_vulnerable': component_data.get('tariff_vulnerable', False),
                'critical': component_data.get('critical', False)
            }
            
            # Save report
            from prophet.utils import save_scenario_results
            output_file = args.output or f"output/component_analysis_{args.component_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(report, output_file)
            print(f"Component analysis saved to {output_file}")
        
        elif args.analyze_type == 'product':
            # Analyze product
            if args.product_id not in graph:
                print(f"Error: Product {args.product_id} not found in graph")
                return
            
            product_data = graph.nodes[args.product_id]
            
            # Find components in this product
            components = []
            for source, target, edge_data in graph.out_edges(args.product_id, data=True):
                if edge_data.get('relationship_type') == 'CONTAINS':
                    component_data = graph.nodes[target]
                    criticality = calculate_component_criticality(graph, target, args.product_id)
                    
                    components.append({
                        'component_id': target,
                        'component_name': component_data.get('name', 'Unknown'),
                        'criticality_score': criticality,
                        'risk_level': 'high' if criticality > 0.7 else 'medium' if criticality > 0.4 else 'low',
                        'tariff_vulnerable': component_data.get('tariff_vulnerable', False),
                        'critical': component_data.get('critical', False)
                    })
            
            # Sort by criticality
            components.sort(key=lambda x: x['criticality_score'], reverse=True)
            
            # Find manufacturer
            manufacturer = None
            for source, target, edge_data in graph.in_edges(args.product_id, data=True):
                if edge_data.get('relationship_type') == 'MANUFACTURES':
                    manufacturer = {
                        'company_id': source,
                        'company_name': graph.nodes[source].get('name', 'Unknown')
                    }
                    break
            
            # Create report
            report = {
                'product_id': args.product_id,
                'product_name': product_data.get('name', 'Unknown'),
                'manufacturer': manufacturer,
                'components_count': len(components),
                'critical_components_count': sum(1 for c in components if c['criticality_score'] > 0.7),
                'components': components,
                'risk_level': 'high' if any(c['criticality_score'] > 0.7 for c in components) else 'medium' if any(c['criticality_score'] > 0.4 for c in components) else 'low'
            }
            
            # Save report
            from prophet.utils import save_scenario_results
            output_file = args.output or f"output/product_analysis_{args.product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(report, output_file)
            print(f"Product analysis saved to {output_file}")
        
        elif args.analyze_type == 'vulnerabilities':
            # Find vulnerabilities
            critical_components = analyzer.find_critical_components(threshold=args.threshold)
            single_points = analyzer.detect_single_points_of_failure()
            geo_concentration = analyzer.identify_geographical_concentration()
            
            # Create report
            report = {
                'critical_components': critical_components,
                'single_points_of_failure': single_points,
                'geographical_concentration': geo_concentration,
                'threshold': args.threshold,
                'summary': {
                    'critical_components_count': len(critical_components),
                    'single_points_count': len(single_points),
                    'high_risk_countries_count': sum(1 for c in geo_concentration['country_concentration'] if c['risk_level'] == 'high')
                }
            }
            
            # Save report
            from prophet.utils import save_scenario_results
            output_file = args.output or f"output/vulnerabilities_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_scenario_results(report, output_file)
            print(f"Vulnerabilities analysis saved to {output_file}")
        
        else:
            analyze_parser.print_help()
    
    # Handle predict commands
    elif args.command == 'predict':
        from prophet.prediction_engine import PredictionEngine
        engine = PredictionEngine(graph)
        
        if args.predict_type == 'tariff':
            # Predict tariff impact
            results = engine.predict_tariff_impact(
                country=args.country,
                increase_percentage=args.increase,
                affected_component_types=args.components,
                output_file=args.output
            )
            
            # Print summary
            print(f"\nTariff Impact Analysis: {args.increase}% increase from {args.country}")
            print(f"Affected components: {results['affected_components_count']}")
            print(f"Affected products: {results['affected_products_count']}")
            print(f"Average lead time increase: {results['lead_time_impacts']['average_lead_time_increase_weeks']} weeks")
            print(f"Resilience impact: {results['resilience_impact']['change']}")
            
            # Print recommendations
            if results['recommendations']:
                print("\nTop Recommendations:")
                for i, rec in enumerate(results['recommendations'][:3]):
                    print(f"{i+1}. [{rec['priority'].upper()}] {rec['description']}")
        
        elif args.predict_type == 'geopolitical':
            # Predict geopolitical event
            results = engine.predict_geopolitical_event(
                country=args.country,
                event_type=args.event,
                severity=args.severity,
                duration_months=args.duration,
                output_file=args.output
            )
            
            # Print summary
            print(f"\nGeopolitical Event Analysis: {args.severity} {args.event} in {args.country} for {args.duration} months")
            print(f"Affected components: {results['affected_components_count']}")
            print(f"Affected products: {results['affected_products_count']}")
            print(f"Overall impact level: {results['impact_assessment']['overall_impact_level'].upper()}")
            print(f"Estimated recovery: {results['recovery_timeline']['estimated_months']} months")
            print(f"Resilience impact: {results['resilience_impact']['change']}")
            
            # Print recommendations
            if results['recommendations']:
                print("\nTop Recommendations:")
                for i, rec in enumerate(results['recommendations'][:3]):
                    print(f"{i+1}. [{rec['priority'].upper()}] {rec['description']}")
        
        elif args.predict_type == 'shortage':
            # Predict component shortage
            results = engine.predict_component_shortage(
                component_type=args.component_type,
                shortage_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            
            # Print summary
            print(f"\nComponent Shortage Analysis: {args.level} shortage of {args.component_type} for {args.duration} months")
            print(f"Affected components: {results['affected_components_count']}")
            print(f"Affected products: {results['affected_products_count']}")
            print(f"Lead time impact: {results['impact_assessment']['average_lead_time_increase']} weeks")
            print(f"Price impact: {results['impact_assessment']['average_price_increase']}%")
            print(f"Allocation reduction: {results['impact_assessment']['average_allocation_reduction']}%")
            print(f"Resilience impact: {results['resilience_impact']['change']}")
            
            # Print recommendations
            if results['recommendations']:
                print("\nTop Recommendations:")
                for i, rec in enumerate(results['recommendations'][:3]):
                    print(f"{i+1}. [{rec['priority'].upper()}] {rec['description']}")
        
        elif args.predict_type == 'optimize':
            # Generate optimization recommendations
            results = engine.generate_recommendations(
                company_id=args.company,
                output_file=args.output
            )
            
            # Print summary
            company_str = f" for {results.get('company_id', 'all companies')}"
            print(f"\nOptimization Recommendations{company_str}")
            print(f"Resilience score: {results['resilience_score']}/100 ({results['risk_level'].upper()} risk)")
            
            # Print recommendations
            if results['recommendations']:
                print("\nTop Recommendations:")
                for i, rec in enumerate(results['recommendations']):
                    print(f"{i+1}. [{rec['priority'].upper()}] {rec['description']}")
        
        elif args.predict_type == 'alternatives':
            # Find alternative sources
            results = engine.find_alternative_sources(
                component_id=args.component,
                max_alternatives=args.max,
                output_file=args.output
            )
            
            # Print summary
            print(f"\nAlternative Sources for {results['component_name']} ({results['component_id']})")
            
            # Print current suppliers
            if results['current_suppliers']:
                print("\nCurrent Suppliers:")
                for i, supplier in enumerate(results['current_suppliers']):
                    print(f"  - {supplier['supplier_name']} ({supplier['hq_country']})")
            
            # Print alternatives
            if results['alternatives']:
                print("\nAlternative Components:")
                for i, alt in enumerate(results['alternatives']):
                    print(f"{i+1}. {alt['component_name']} (Similarity: {alt['similarity_score']*100:.0f}%)")
                    print(f"   Suppliers: {', '.join(alt['suppliers']) if alt['suppliers'] else 'None'}")
                    print(f"   Countries: {', '.join(alt['countries']) if alt['countries'] else 'Unknown'}")
            else:
                print("\nNo viable alternatives found")
        
        else:
            predict_parser.print_help()
    
    # Handle report commands
    elif args.command == 'report':
        from prophet.prediction_engine import PredictionEngine
        engine = PredictionEngine(graph)
        
        if args.report_type == 'comprehensive':
            # Generate comprehensive report
            include_scenarios = not args.no_scenarios
            
            print(f"Generating comprehensive report{' with scenarios' if include_scenarios else ' without scenarios'}...")
            print(f"This may take a few minutes...")
            
            results = engine.run_comprehensive_analysis(
                company_id=args.company,
                output_dir=args.output_dir,
                include_scenarios=include_scenarios
            )
            
            # Print summary
            print(f"\nComprehensive Analysis for {results['company_name']}")
            print(f"Resilience score: {results['baseline']['resilience_score']}/100 ({results['baseline']['risk_level'].upper()} risk)")
            print(f"Critical components: {results['baseline']['critical_components_count']}")
            print(f"Single points of failure: {results['baseline']['single_points_count']}")
            
            # Print top insights
            if results['top_insights']['critical_components']:
                print("\nTop Critical Components:")
                for comp in results['top_insights']['critical_components']:
                    print(f"  - {comp}")
            
            if results['top_insights']['high_risk_suppliers']:
                print("\nHigh Risk Suppliers:")
                for supplier in results['top_insights']['high_risk_suppliers']:
                    print(f"  - {supplier}")
            
            if results['top_insights']['high_risk_countries']:
                print("\nHigh Risk Countries:")
                for country in results['top_insights']['high_risk_countries']:
                    print(f"  - {country}")
            
            # Print top recommendations
            if results['top_recommendations']:
                print("\nTop Recommendations:")
                for i, rec in enumerate(results['top_recommendations']):
                    print(f"{i+1}. {rec}")
            
            # Print scenarios
            if results['scenarios']:
                print("\nScenario Analysis:")
                for scenario in results['scenarios']:
                    print(f"  - {scenario['type']} ({scenario['impact_level'].upper()} impact)")
                    if scenario['type'] == 'supplier_disruption':
                        print(f"    Supplier: {scenario['supplier_name']}")
                    elif scenario['type'] == 'tariff_change':
                        print(f"    Country: {scenario['country']}, Increase: {scenario['increase_percentage']}%")
            
            # Print output location
            print(f"\nDetailed reports saved to: {args.output_dir}")
            print(f"Summary file: {os.path.basename(results['output_files']['baseline'])}")
        
        else:
            report_parser.print_help()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

    print(f"Average price increase: {results['price_impacts']['average_product_price_increase']}%")
    print(f"Resilience impact: {results['resilience_impact']['change']}")
            
    # Print recommendations
    if results['recommendations']:
        print("\nTop Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3]):
                    print(f"{i+1}. [{rec['priority'].upper()}] {rec['description']}")
        
    elif args.predict_type == 'disruption':
            # Predict supplier disruption
        results = engine.predict_supplier_disruption(
                supplier_id=args.supplier,
                disruption_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            
            # Print summary
    print(f"\nSupplier Disruption Analysis: {args.level} disruption of {results.get('supplier_name', args.supplier)} for {args.duration} months")
    print(f"Affected components: {results['affected_components_count']}")
    print(f"Affected products: {results['affected_products_count']}")