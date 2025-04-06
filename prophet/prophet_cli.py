# Complete the main function in prophet_cli.py to handle all commands
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
    
    # 2. Predict command
    predict_parser = subparsers.add_parser('predict', help='Run predictions on the supply chain')
    predict_subparsers = predict_parser.add_subparsers(dest='predict_type', help='Type of prediction')
    
    # 2.1 Predict tariff impacts
    tariff_parser = predict_subparsers.add_parser('tariff', help='Predict impact of tariff changes')
    tariff_parser.add_argument('--country', required=True, help='Country implementing the tariff')
    tariff_parser.add_argument('--increase', type=float, required=True, help='Percentage increase in tariffs')
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
    
    # Load the graph
    try:
        # Import from the new location
        from prophet.prediction_engine import load_graph
        graph = load_graph(args.graph)
        logger.info(f"Loaded graph from {args.graph} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    except Exception as e:
        logger.error(f"Error loading graph: {e}")
        return

    # Initialize the prediction engine
    try:
        from prophet.prediction_engine import PredictionEngine
        from veritas import SupplyChainAnalyzer
        
        analyzer = SupplyChainAnalyzer(graph)
        engine = PredictionEngine(graph, analyzer)
        logger.info("Initialized prediction engine")
    except Exception as e:
        logger.error(f"Error initializing prediction engine: {e}")
        return
    
    # Handle analyze commands
    if args.command == 'analyze':
        if not args.analyze_type:
            logger.error("No analyze type specified")
            analyze_parser.print_help()
            return
        
        if args.analyze_type == 'company':
            logger.info(f"Analyzing company: {args.company_id}")
            from veritas import InsightExtractor
            
            extractor = InsightExtractor(analyzer)
            report = extractor.generate_summary_report(company_id=args.company_id)
            
            output_file = args.output
            if not output_file:
                output_file = output_dir / f"company_analysis_{args.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            
            if args.format == 'json':
                from veritas import save_report_to_json
                save_report_to_json(report, output_file)
            else:
                from veritas import save_report_to_markdown
                save_report_to_markdown(report, output_file)
            
            logger.info(f"Company analysis saved to {output_file}")
        
        elif args.analyze_type == 'resilience':
            logger.info("Analyzing supply chain resilience")
            resilience = analyzer.calculate_resilience_score(company_id=args.company)
            
            output_file = args.output
            if not output_file:
                suffix = f"_{args.company}" if args.company else ""
                output_file = output_dir / f"resilience_analysis{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(output_file, 'w') as f:
                json.dump(resilience, f, indent=2)
            
            logger.info(f"Resilience analysis saved to {output_file}")
        
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
            
            with open(output_file, 'w') as f:
                json.dump(critical_components, f, indent=2)
            
            logger.info(f"Critical components analysis saved to {output_file}")
    
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
                output_file=args.output
            )
            logger.info(f"Tariff prediction completed")
        
        elif args.predict_type == 'disruption':
            logger.info(f"Predicting supplier disruption for {args.supplier}")
            results = engine.predict_supplier_disruption(
                supplier_id=args.supplier,
                disruption_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            logger.info(f"Supplier disruption prediction completed")
        
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
        
        elif args.predict_type == 'shortage':
            logger.info(f"Predicting impact of {args.level} shortage of {args.component_type}")
            results = engine.predict_component_shortage(
                component_type=args.component_type,
                shortage_level=args.level,
                duration_months=args.duration,
                output_file=args.output
            )
            logger.info(f"Component shortage prediction completed")
        
        elif args.predict_type == 'optimize':
            logger.info(f"Generating optimization recommendations")
            results = engine.generate_recommendations(
                company_id=args.company,
                output_file=args.output
            )
            logger.info(f"Optimization recommendations generated")
    
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
    
    logger.info("Nova Prophet CLI command completed successfully")