"""
markdown_report.py - Markdown report generation for tariff analysis

This module generates Markdown reports for tariff analysis.
"""

from datetime import datetime
from pathlib import Path
import os
from tabulate import tabulate

def generate_markdown_report(country, results, charts_data):
    """
    Generate a Markdown report for tariff impact analysis.
    
    Args:
        country: Country being analyzed
        results: Dictionary containing analysis results
        charts_data: Dictionary containing chart data
        
    Returns:
        Path to the generated report
    """
    # Extract needed data
    affected_components_count = results.get('affected_components_count', 0)
    affected_components = results.get('affected_components', [])
    affected_products_count = results.get('affected_products_count', 0)
    affected_products = results.get('affected_products', [])
    price_impacts = results.get('price_impacts', {})
    resilience_impact = results.get('resilience_impact', {})
    recommendations = results.get('recommendations', [])
    
    # Get increase percentage
    increase_percentage = results.get('increase_percentage', 0)
    
    # Create output directory if it doesn't exist
    report_dir = Path("./reports")
    report_dir.mkdir(exist_ok=True)
    
    # Generate filename
    filename = f"tariff_analysis_{country.lower().replace(' ', '_')}_{increase_percentage:+}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = report_dir / filename
    
    # Begin building Markdown content
    md_content = f"# Tariff Impact Analysis: {country} {increase_percentage:+}%\n\n"
    md_content += f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    # Overview section
    md_content += "## Analysis Overview\n\n"
    md_content += f"- **Country:** {country}\n"
    md_content += f"- **Tariff Change:** {increase_percentage:+}%\n"
    md_content += f"- **Affected Components:** {affected_components_count}\n"
    md_content += f"- **Affected Products:** {affected_products_count}\n\n"
    
    # Components section
    md_content += "## Affected Components\n\n"
    
    if affected_components:
        md_content += "| Component | Type | Tariff Change | Price Impact |\n"
        md_content += "|-----------|------|--------------|-------------|\n"
        
        for comp in affected_components[:10]:  # Limit to top 10
            md_content += f"| {comp.get('component_name', 'Unknown')} | "
            md_content += f"{comp.get('component_type', 'Unknown')} | "
            md_content += f"{comp.get('tariff_increase', increase_percentage):+}% | "
            md_content += f"{comp.get('estimated_price_increase', 0):.1f}% |\n"
        
        if len(affected_components) > 10:
            md_content += f"\n*... and {len(affected_components) - 10} more components*\n"
    else:
        md_content += "*No affected components found*\n"
    
    # Add component chart if available
    if 'component_chart_file' in charts_data:
        relative_path = os.path.relpath(charts_data['component_chart_file'], str(report_dir.parent))
        md_content += f"\n![Component Price Impact]({relative_path})\n\n"
    
    # Products section
    md_content += "## Affected Products\n\n"
    
    if affected_products:
        md_content += "| Product | Manufacturer | Price Impact | Critical Components |\n"
        md_content += "|---------|--------------|--------------|--------------------|\n"
        
        for prod in affected_products[:10]:  # Limit to top 10
            md_content += f"| {prod.get('product_name', 'Unknown')} | "
            md_content += f"{prod.get('manufacturer', 'Unknown')} | "
            md_content += f"{prod.get('estimated_price_increase_percentage', 0):.1f}% | "
            md_content += f"{prod.get('critical_components_count', 0)} |\n"
        
        if len(affected_products) > 10:
            md_content += f"\n*... and {len(affected_products) - 10} more products*\n"
    else:
        md_content += "*No affected products found*\n"
    
    # Add product chart if available
    if 'product_chart_file' in charts_data:
        relative_path = os.path.relpath(charts_data['product_chart_file'], str(report_dir.parent))
        md_content += f"\n![Product Price Impact]({relative_path})\n\n"
    
    # Price Impact section
    md_content += "## Price Impact Analysis\n\n"
    md_content += f"- **Average Product Price Increase:** {price_impacts.get('average_product_price_increase', 0):.2f}%\n"
    md_content += f"- **Maximum Product Price Increase:** {price_impacts.get('max_product_price_increase', 0):.2f}%\n"
    md_content += f"- **Minimum Product Price Increase:** {price_impacts.get('min_product_price_increase', 0):.2f}%\n\n"
    
    # Add risk distribution chart if available
    if 'risk_chart_file' in charts_data:
        relative_path = os.path.relpath(charts_data['risk_chart_file'], str(report_dir.parent))
        md_content += f"![Product Risk Distribution]({relative_path})\n\n"
    
    # Resilience Impact section
    md_content += "## Supply Chain Resilience Impact\n\n"
    
    before = resilience_impact.get('before', 0)
    after = resilience_impact.get('after', 0)
    change = resilience_impact.get('change', 0)
    
    md_content += f"- **Resilience Score Before:** {before:.1f}/100\n"
    md_content += f"- **Resilience Score After:** {after:.1f}/100\n"
    md_content += f"- **Change:** {change:+.1f}\n\n"
    
    # Add resilience chart if available
    if 'resilience_chart_file' in charts_data:
        relative_path = os.path.relpath(charts_data['resilience_chart_file'], str(report_dir.parent))
        md_content += f"![Resilience Impact]({relative_path})\n\n"
    
    # Recommendations section
    md_content += "## Strategic Recommendations\n\n"
    
    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            priority = rec.get('priority', 'medium').upper()
            
            md_content += f"### {i}. {rec.get('description', 'No description available')}\n\n"
            md_content += f"- **Priority:** {priority}\n"
            md_content += f"- **Benefit:** {rec.get('estimated_benefit', 'Unknown')}\n\n"
    else:
        md_content += "*No specific recommendations available*\n\n"
    
    # Add footer
    md_content += "---\n\n"
    md_content += "*This report was generated by Nova Prophet Supply Chain Prediction System*\n"
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filepath