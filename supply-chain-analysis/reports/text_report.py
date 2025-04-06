"""
text_report.py - Text report generation for tariff analysis

This module generates text-based reports for tariff analysis.
"""

from datetime import datetime
from pathlib import Path
import os
from tabulate import tabulate

def colorize(text, color):
    """Add color to terminal text."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(colorize(f" {title} ".center(80, " "), "bold"))
    print("="*80)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + colorize(f"▶ {title}", "cyan"))
    print("-"*80)

def generate_text_report(country, increase_percentage, results, charts_data):
    """
    Generate a text report for tariff impact analysis.
    
    Args:
        country: Country being analyzed
        increase_percentage: Tariff increase percentage
        results: Dictionary containing analysis results
        charts_data: Dictionary containing chart data
    """
    # Display basic information
    print_section("ANALYSIS OVERVIEW")
    print(f"Country: {colorize(country, 'yellow')}")
    print(f"Tariff Change: {colorize(f'{increase_percentage:+}%', 'yellow')}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display affected components summary
    print_section("AFFECTED COMPONENTS")
    affected_count = results.get('affected_components_count', 0)
    print(f"Total Affected Components: {colorize(str(affected_count), 'yellow')}")
    
    # Display affected components in a table
    if affected_count > 0 and 'affected_components' in results:
        components = results['affected_components'][:10]  # Limit to top 10
        component_data = []
        for comp in components:
            component_data.append([
                comp.get('component_name', 'Unknown'),
                comp.get('component_type', 'Unknown'),
                f"{comp.get('tariff_increase', increase_percentage):+}%",
                comp.get('estimated_price_increase', 0)
            ])
        
        headers = ["Component", "Type", "Tariff Change", "Est. Price Impact"]
        print("\n" + tabulate(component_data, headers=headers, tablefmt="pretty"))
        
        if affected_count > 10:
            print(f"\n... and {affected_count - 10} more components")
    
    # Display affected products summary
    print_section("AFFECTED PRODUCTS")
    affected_products_count = results.get('affected_products_count', 0)
    print(f"Total Affected Products: {colorize(str(affected_products_count), 'yellow')}")
    
    # Display affected products in a table
    if affected_products_count > 0 and 'affected_products' in results:
        products = results['affected_products'][:10]  # Limit to top 10
        product_data = []
        for prod in products:
            # Calculate impact level
            impact = prod.get('estimated_price_increase_percentage', 0)
            if impact > 5:
                impact_str = colorize(f"{impact:.1f}%", "red")
            elif impact > 2:
                impact_str = colorize(f"{impact:.1f}%", "yellow")
            else:
                impact_str = colorize(f"{impact:.1f}%", "green")
                
            product_data.append([
                prod.get('product_name', 'Unknown'),
                prod.get('manufacturer', 'Unknown'),
                impact_str,
                prod.get('critical_components_count', 0)
            ])
        
        headers = ["Product", "Manufacturer", "Price Impact", "Critical Components"]
        print("\n" + tabulate(product_data, headers=headers, tablefmt="pretty"))
        
        if affected_products_count > 10:
            print(f"\n... and {affected_products_count - 10} more products")
    
    # Display price impacts
    print_section("PRICE IMPACT ANALYSIS")
    price_impacts = results.get('price_impacts', {})
    avg_price_increase = price_impacts.get('average_product_price_increase', 0)
    max_product_price_increase = price_impacts.get('max_product_price_increase',0)
    min_product_price_increase = price_impacts.get('min_product_price_increase',0)
    
    print(f"Average Product Price Increase: {colorize(f'{avg_price_increase:.2f}%', 'yellow')}")
    print(f"Max Product Price Increase: {colorize(f'{max_product_price_increase:.2f}%', 'yellow')}")
    print(f"Min Product Price Increase: {colorize(f'{min_product_price_increase:.2f}%', 'yellow')}")

    # Display resilience impact
    print_section("SUPPLY CHAIN RESILIENCE IMPACT")
    resilience = results.get('resilience_impact', {})
    before = resilience.get('before', 0)
    after = resilience.get('after', 0)
    change = resilience.get('change', 0)
    
    change_color = "green" if change >= 0 else "red"
    print(f"Resilience Score Before: {colorize(f'{before:.1f}/100', 'yellow')}")
    print(f"Resilience Score After: {colorize(f'{after:.1f}/100', 'yellow')}")
    print(f"Change: {colorize(f'{change:+.1f}', change_color)}")
    
    # Display recommendations
    print_section("RECOMMENDATIONS")
    recommendations = results.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            priority = rec.get('priority', 'medium').upper()
            priority_color = "red" if priority == "HIGH" else "yellow" if priority == "MEDIUM" else "green"
            
            print(f"{i}. {rec.get('description', 'No description available')}")
            print(f"   Priority: {colorize(priority, priority_color)}")
            print(f"   Benefit: {rec.get('estimated_benefit', 'Unknown')}")
            print()
    else:
        print("No specific recommendations available.")
    
    # Display visualization file locations
    if charts_data:
        print_section("VISUALIZATIONS")
        for chart_name, chart_file in charts_data.items():
            if chart_file and "_file" in chart_name:
                print(f"{chart_name.replace('_file', '').replace('_', ' ').title()}: {colorize(chart_file, 'green')}")
    
    return True

def generate_text_comparison_report(scenario_results, charts_data):
    """
    Generate a text report for tariff scenario comparison.
    
    Args:
        scenario_results: List of dictionaries containing scenario results
        charts_data: Dictionary containing chart data
    """
    # Display comparison table
    print_section("SCENARIO OVERVIEW")
    
    # Basic comparison table
    comparison_data = []
    for result in scenario_results:
        scenario_name = result.get('scenario_name', 'Unknown')
        country = result.get('country', 'Unknown')
        increase = result.get('increase_percentage', 0)
        affected_components = result.get('affected_components_count', 0)
        affected_products = result.get('affected_products_count', 0)
        avg_price_impact = result.get('price_impacts', {}).get('average_product_price_increase', 0)
        resilience_change = result.get('resilience_impact', {}).get('change', 0)
        
        comparison_data.append([
            scenario_name,
            f"{country} {increase:+}%",
            affected_components,
            affected_products,
            f"{avg_price_impact:.2f}%",
            f"{resilience_change:+.2f}"
        ])
    
    headers = ["Scenario", "Tariff Change", "Components", "Products", "Avg Price Impact", "Resilience Δ"]
    print("\n" + tabulate(comparison_data, headers=headers, tablefmt="pretty"))
    
    # Display best and worst scenarios
    print_section("SCENARIO RANKING")
    
    # Calculate min/max values for normalization
    price_impacts = [r.get('price_impacts', {}).get('average_product_price_increase', 0) for r in scenario_results]
    resilience_changes = [r.get('resilience_impact', {}).get('change', 0) for r in scenario_results]
    min_price_impact = min(price_impacts)
    max_price_impact = max(price_impacts)
    min_resilience_change = min(resilience_changes)
    max_resilience_change = max(resilience_changes)
    
    # Rank by resilience impact (higher is better)
    resilience_ranking = sorted(scenario_results, 
                               key=lambda x: x.get('resilience_impact', {}).get('change', -999), 
                               reverse=True)
    
    # Rank by price impact (lower is better)
    price_ranking = sorted(scenario_results, 
                          key=lambda x: x.get('price_impacts', {}).get('average_product_price_increase', 999))
    
    # Display best scenario for resilience
    if resilience_ranking:
        best = resilience_ranking[0]
        change = best.get('resilience_impact', {}).get('change', 0)
        change_str = f"{change:+.2f}" if change else "0.00"
        print(f"Best Scenario for Supply Chain Resilience: {colorize(best.get('scenario_name', 'Unknown'), 'green')}")
        print(f"  Resilience Change: {colorize(change_str, 'green')}")
    
    # Display best scenario for price
    if price_ranking:
        best = price_ranking[0]
        price_impact = best.get('price_impacts', {}).get('average_product_price_increase', 0)
        print(f"Best Scenario for Price Impact: {colorize(best.get('scenario_name', 'Unknown'), 'green')}")
        print(f"  Average Price Increase: {colorize(f'{price_impact:.2f}%', 'green')}")
    
    print("\nOverall Recommendation:")
    # Simple scoring system combining resilience and price impact
    if scenario_results:
        for result in scenario_results:
            resilience_change = result.get('resilience_impact', {}).get('change', 0)
            price_impact = result.get('price_impacts', {}).get('average_product_price_increase', 0)
            # Normalize scores (resilience: higher is better, price: lower is better)
            resilience_score = (resilience_change - min_resilience_change) / (max_resilience_change - min_resilience_change) if max_resilience_change != min_resilience_change else 0.5
            price_score = 1 - ((price_impact - min_price_impact) / (max_price_impact - min_price_impact)) if max_price_impact != min_price_impact else 0.5
            # Combined score (weight resilience higher than price)
            result['combined_score'] = resilience_score * 0.6 + price_score * 0.4
        
        # Get overall best scenario
        overall_best = max(scenario_results, key=lambda x: x.get('combined_score', 0))
        best_scenario=overall_best.get('scenario_name', 'Unknown')
        best_county=overall_best.get('country', 'Unknown')
        best_pct=overall_best.get('increase_percentage', 0)
        print(f"The most balanced scenario appears to be: {colorize(best_scenario, 'cyan')}")
        print(f"  Country: {best_county}")
        print(f"  Tariff Change: {colorize(best_pct, 'cyan')}")
        
        # Print top recommendation for this scenario
        if 'recommendations' in overall_best and overall_best['recommendations']:
            top_rec = overall_best['recommendations'][0]
            print(f"\nRecommended Action: {colorize(top_rec.get('description', 'No action available'), 'yellow')}")
    
    # Display visualization file locations
    if charts_data:
        print_section("VISUALIZATIONS")
        for chart_name, chart_file in charts_data.items():
            if chart_file and "_file" in chart_name:
                print(f"{chart_name.replace('_file', '').replace('_', ' ').title()}: {colorize(chart_file, 'green')}")
    
    return True

def generate_text_vulnerability_report(country, results):
    """
    Generate a text vulnerability report and save to file.
    
    Args:
        country: Country being analyzed
        results: Dictionary containing vulnerability analysis results
        
    Returns:
        Path to the generated report
    """
    # Format the report content
    report_content = f"TARIFF VULNERABILITY ANALYSIS: {country}\n"
    report_content += "="*80 + "\n\n"
    
    report_content += "VULNERABILITY OVERVIEW\n"
    report_content += "-"*80 + "\n"
    report_content += f"Country: {country}\n"
    report_content += f"Affected Components: {results.get('affected_components_count', 0)}\n"
    report_content += f"Affected Products: {results.get('affected_products_count', 0)}\n"
    report_content += f"Affected Companies: {results.get('affected_companies_count', 0)}\n\n"
    
    report_content += "HIGH-RISK COMPONENTS\n"
    report_content += "-"*80 + "\n"
    
    high_risk_components = results.get('highest_risk_components', [])
    if high_risk_components:
        for comp in high_risk_components:
            report_content += f"Component: {comp.get('component_name', 'Unknown')}\n"
            report_content += f"  Countries: {', '.join(comp.get('countries', ['Unknown']))}\n"
            report_content += f"  Products Affected: {len(comp.get('products', []))}\n"
            report_content += f"  Tariff Vulnerable: {'Yes' if comp.get('tariff_vulnerable', False) else 'No'}\n\n"
    else:
        report_content += "No high-risk components identified.\n"
    
    # Add summary section
    report_content += "\nVULNERABILITY SUMMARY\n"
    report_content += "-"*80 + "\n"
    
    if 'country_concentration' in results:
        countries_data = results.get('country_concentration', [])
        high_risk_countries = [c for c in countries_data if c.get('risk_level') == 'high']
        
        if high_risk_countries:
            report_content += "High Risk Countries:\n"
            for country_data in high_risk_countries[:5]:  # Top 5 high risk countries
                report_content += f"  - {country_data.get('country', 'Unknown')}: "
                report_content += f"{country_data.get('critical_components', 0)} critical components, "
                report_content += f"{country_data.get('total_components', 0)} total components\n"
        
        report_content += f"\nConcentration by Risk Level:\n"
        report_content += f"  High Risk: {sum(1 for c in countries_data if c.get('risk_level') == 'high')}\n"
        report_content += f"  Medium Risk: {sum(1 for c in countries_data if c.get('risk_level') == 'medium')}\n"
        report_content += f"  Low Risk: {sum(1 for c in countries_data if c.get('risk_level') == 'low')}\n"
    
    # Add generation timestamp
    report_content += f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Create output directory if it doesn't exist
    export_dir = Path("./reports")
    export_dir.mkdir(exist_ok=True)
    
    # Generate filename and save
    filename = f"tariff_vulnerability_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = export_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(report_content)
    
    return filepath
