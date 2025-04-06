"""
charts.py - Chart generation for tariff analysis

This module creates visualizations for tariff analysis reports.
"""

import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

def create_charts(results, is_comparison=False, is_vulnerability=False):
    """
    Create visualization charts for tariff analysis results.
    
    Args:
        results: Dictionary containing analysis results
        is_comparison: Whether this is a comparison of multiple scenarios
        is_vulnerability: Whether this is a vulnerability analysis
        
    Returns:
        Dictionary with base64-encoded chart images
    """
    try:
        # Create viz directory if it doesn't exist
        viz_dir = Path("./viz")
        viz_dir.mkdir(exist_ok=True)
        
        charts_data = {}
        
        if is_comparison:
            # Comparison mode - create comparison charts
            charts_data = create_comparison_charts(results, viz_dir)
        elif is_vulnerability:
            # Vulnerability mode - create vulnerability charts
            charts_data = create_vulnerability_charts(results, viz_dir)
        else:
            # Standard mode - create standard tariff impact charts
            charts_data = create_standard_charts(results, viz_dir)
        
        return charts_data
    except Exception as e:
        print(f"Error creating charts: {e}")
        return {}

def create_standard_charts(results, viz_dir):
    """Create standard tariff impact charts."""
    charts_data = {}
    
    # Extract needed data
    affected_components = results.get('affected_components', [])
    affected_products = results.get('affected_products', [])
    price_impacts = results.get('price_impacts', {})
    resilience_impact = results.get('resilience_impact', {})
    country = results.get('country', 'Unknown')
    increase_percentage = results.get('increase_percentage', 0)
    
    # 1. Component Impact Chart
    if affected_components:
        plt.figure(figsize=(10, 6))
        components = affected_components[:8]  # Top 8 components
        names = [c.get('component_name', f"Component {i}") for i, c in enumerate(components)]
        impacts = [c.get('estimated_price_increase', 0) for c in components]
        
        colors = ['#3498db' if i < 4 else '#2980b9' for i in range(len(impacts))]
        plt.bar(names, impacts, color=colors)
        plt.ylabel('Estimated Price Increase (%)')
        plt.title('Component Price Impact')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to file and convert to base64
        component_chart_file = viz_dir / f"component_impact_{country.lower()}_{increase_percentage:+}.png"
        plt.savefig(component_chart_file)
        
        # Convert to base64 for embedding in reports
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        charts_data['component_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts_data['component_chart_file'] = str(component_chart_file)
        plt.close()
    
    # 2. Product Price Impact Chart
    if affected_products:
        plt.figure(figsize=(10, 6))
        products = affected_products[:8]  # Top 8 products
        names = [p.get('product_name', f"Product {i}") for i, p in enumerate(products)]
        impacts = [p.get('estimated_price_increase_percentage', 0) for p in products]
        
        # Color bars based on impact
        colors = []
        for impact in impacts:
            if impact > 5:
                colors.append('#e74c3c')  # High impact - red
            elif impact > 2:
                colors.append('#f39c12')  # Medium impact - orange
            else:
                colors.append('#2ecc71')  # Low impact - green
        
        plt.bar(names, impacts, color=colors)
        plt.ylabel('Price Increase (%)')
        plt.title(f'Product Price Impact - {country} {increase_percentage:+}% Tariff')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to file and convert to base64
        product_chart_file = viz_dir / f"product_impact_{country.lower()}_{increase_percentage:+}.png"
        plt.savefig(product_chart_file)
        
        # Convert to base64 for embedding in reports
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        charts_data['product_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts_data['product_chart_file'] = str(product_chart_file)
        plt.close()
    
    # 3. Resilience Impact Chart
    if resilience_impact:
        before = resilience_impact.get('before', 0)
        after = resilience_impact.get('after', 0)
        change = resilience_impact.get('change', 0)
        
        plt.figure(figsize=(8, 5))
        scores = [before, after]
        labels = ['Before Tariff', 'After Tariff']
        
        # Colors based on change
        bar_colors = ['#3498db', '#e74c3c' if change < 0 else '#2ecc71']
        
        bars = plt.bar(labels, scores, color=bar_colors)
        
        # Add threshold lines for risk levels
        plt.axhline(y=60, color='#e74c3c', linestyle='--', alpha=0.3, label='High Risk Threshold')
        plt.axhline(y=80, color='#2ecc71', linestyle='--', alpha=0.3, label='Low Risk Threshold')
        
        # Add text labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.title('Supply Chain Resilience Impact')
        plt.ylabel('Resilience Score (0-100)')
        plt.ylim(0, 100)
        plt.legend(loc='lower right')
        plt.tight_layout()
        
        # Save to file and convert to base64
        resilience_chart_file = viz_dir / f"resilience_impact_{country.lower()}_{increase_percentage:+}.png"
        plt.savefig(resilience_chart_file)
        
        # Convert to base64 for embedding in reports
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        charts_data['resilience_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts_data['resilience_chart_file'] = str(resilience_chart_file)
        plt.close()
    
    # 4. Risk Distribution Pie Chart
    if affected_products:
        # Count products by risk level
        high_risk = sum(1 for p in affected_products if p.get('estimated_price_increase_percentage', 0) > 5)
        medium_risk = sum(1 for p in affected_products if 2 < p.get('estimated_price_increase_percentage', 0) <= 5)
        low_risk = sum(1 for p in affected_products if p.get('estimated_price_increase_percentage', 0) <= 2)
        
        plt.figure(figsize=(8, 5))
        labels = ['High Risk', 'Medium Risk', 'Low Risk']
        sizes = [high_risk, medium_risk, low_risk]
        colors = ['#e74c3c', '#f39c12', '#2ecc71']
        explode = (0.1, 0.05, 0)  # explode the 1st slice (High Risk)
        
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Product Risk Distribution')
        plt.tight_layout()
        
        # Save to file and convert to base64
        risk_chart_file = viz_dir / f"risk_distribution_{country.lower()}_{increase_percentage:+}.png"
        plt.savefig(risk_chart_file)
        
        # Convert to base64 for embedding in reports
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        charts_data['risk_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts_data['risk_chart_file'] = str(risk_chart_file)
        plt.close()
    
    return charts_data

def create_comparison_charts(scenario_results, viz_dir):
    """Create charts for comparing multiple tariff scenarios."""
    charts_data = {}
    
    # Prepare data for visualization
    names = [r.get('scenario_name', f"Scenario {i}") for i, r in enumerate(scenario_results)]
    price_impacts = [r.get('price_impacts', {}).get('average_product_price_increase', 0) for r in scenario_results]
    resilience_changes = [r.get('resilience_impact', {}).get('change', 0) for r in scenario_results]
    
    # 1. Price Impact Comparison
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, price_impacts)
    
    # Color bars based on impact
    for i, bar in enumerate(bars):
        if price_impacts[i] > 5:
            bar.set_color('#e74c3c')  # High impact - red
        elif price_impacts[i] > 2:
            bar.set_color('#f39c12')  # Medium impact - orange
        else:
            bar.set_color('#2ecc71')  # Low impact - green
    
    plt.title('Average Price Impact by Scenario')
    plt.ylabel('Price Increase (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save to file and convert to base64
    price_comp_chart_file = viz_dir / f"price_impact_comparison_{len(scenario_results)}_scenarios.png"
    plt.savefig(price_comp_chart_file)
    
    # Convert to base64 for embedding in reports
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    charts_data['price_comparison_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
    charts_data['price_comparison_chart_file'] = str(price_comp_chart_file)
    plt.close()
    
    # 2. Resilience Impact Comparison
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, resilience_changes)
    
    # Color bars based on impact
    for i, bar in enumerate(bars):
        if resilience_changes[i] < 0:
            bar.set_color('#e74c3c')  # Negative impact - red
        else:
            bar.set_color('#2ecc71')  # Positive impact - green
    
    plt.title('Resilience Score Impact by Scenario')
    plt.ylabel('Resilience Score Change')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)  # Zero line
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save to file and convert to base64
    resilience_comp_chart_file = viz_dir / f"resilience_impact_comparison_{len(scenario_results)}_scenarios.png"
    plt.savefig(resilience_comp_chart_file)
    
    # Convert to base64 for embedding in reports
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    charts_data['resilience_comparison_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
    charts_data['resilience_comparison_chart_file'] = str(resilience_comp_chart_file)
    plt.close()
    
    # 3. Combined Product Count & Component Count
    plt.figure(figsize=(10, 6))
    affected_products = [r.get('affected_products_count', 0) for r in scenario_results]
    affected_components = [r.get('affected_components_count', 0) for r in scenario_results]
    
    # Create positions for the bars
    x = np.arange(len(names))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, affected_products, width, label='Affected Products', color='#3498db')
    plt.bar(x + width/2, affected_components, width, label='Affected Components', color='#9b59b6')
    
    plt.title('Scope of Impact by Scenario')
    plt.xlabel('Scenarios')
    plt.ylabel('Count')
    plt.xticks(x, names, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save to file and convert to base64
    scope_chart_file = viz_dir / f"scope_comparison_{len(scenario_results)}_scenarios.png"
    plt.savefig(scope_chart_file)
    
    # Convert to base64 for embedding in reports
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    charts_data['scope_comparison_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
    charts_data['scope_comparison_chart_file'] = str(scope_chart_file)
    plt.close()
    
    return charts_data

def create_vulnerability_charts(results, viz_dir):
    """Create charts for vulnerability analysis."""
    charts_data = {}
    
    # Extract data
    high_risk_components = results.get('highest_risk_components', [])
    country = results.get('country_focus', 'Unknown')
    
    # 1. Component Risk Bubble Chart (if we have enough information)
    if high_risk_components and len(high_risk_components) >= 3:
        plt.figure(figsize=(10, 6))
        
        # Extract data for bubble chart
        names = [comp.get('component_name', f"Component {i}") for i, comp in enumerate(high_risk_components[:10])]
        product_counts = [len(comp.get('products', [])) for comp in high_risk_components[:10]]
        tariff_vulnerable = [1 if comp.get('tariff_vulnerable', False) else 0.5 for comp in high_risk_components[:10]]
        countries_count = [len(comp.get('countries', [])) for comp in high_risk_components[:10]]
        
        # Create bubble chart
        bubbles = plt.scatter(
            range(len(names)), 
            product_counts,
            s=[count * 100 for count in countries_count],  # Size based on country count
            c=['#e74c3c' if tv == 1 else '#3498db' for tv in tariff_vulnerable],  # Color based on tariff vulnerability
            alpha=0.7
        )
        
        # Add labels
        for i, name in enumerate(names):
            plt.annotate(name, (i, product_counts[i]), 
                        xytext=(0, 10), textcoords='offset points',
                        ha='center', va='bottom', fontsize=8)
        
        plt.title(f'Component Vulnerability Analysis - {country}')
        plt.xlabel('Components')
        plt.ylabel('Products Affected')
        plt.xticks(range(len(names)), ['' for _ in names])  # Hide x-axis labels
        plt.tight_layout()
        
        # Add legend for bubble size
        handles, labels = plt.gca().get_legend_handles_labels()
        size_legend = plt.scatter([], [], s=100, color='gray', alpha=0.7, label='1 Country')
        size_legend2 = plt.scatter([], [], s=200, color='gray', alpha=0.7, label='2 Countries')
        size_legend3 = plt.scatter([], [], s=300, color='gray', alpha=0.7, label='3 Countries')
        color_legend1 = plt.scatter([], [], color='#e74c3c', alpha=0.7, label='Tariff Vulnerable')
        color_legend2 = plt.scatter([], [], color='#3498db', alpha=0.7, label='Not Tariff Vulnerable')
        plt.legend(handles=[size_legend, size_legend2, size_legend3, color_legend1, color_legend2], 
                  loc='upper right')
        
        # Save to file and convert to base64
        component_vuln_chart_file = viz_dir / f"component_vulnerability_{country.lower()}.png"
        plt.savefig(component_vuln_chart_file)
        
        # Convert to base64 for embedding in reports
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        charts_data['component_vulnerability_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts_data['component_vulnerability_chart_file'] = str(component_vuln_chart_file)
        plt.close()
    
    # 2. Country Impact Heatmap (if we have country concentration data)
    if 'country_concentration' in results:
        countries_data = results.get('country_concentration', [])
        
        if countries_data and len(countries_data) >= 3:
            plt.figure(figsize=(12, 8))
            
            # Extract top countries (up to 15)
            top_countries = countries_data[:15]
            countries = [country.get('country', 'Unknown') for country in top_countries]
            components = [country.get('total_components', 0) for country in top_countries]
            critical = [country.get('critical_components', 0) for country in top_countries]
            
            # Create positions for the bars
            x = np.arange(len(countries))
            width = 0.35
            
            # Create stacked bars - critical and non-critical components
            non_critical = [components[i] - critical[i] for i in range(len(components))]
            
            p1 = plt.bar(x, critical, width, color='#e74c3c', label='Critical Components')
            p2 = plt.bar(x, non_critical, width, bottom=critical, color='#3498db', label='Non-Critical Components')
            
            plt.title(f'Component Distribution by Country')
            plt.xlabel('Countries')
            plt.ylabel('Component Count')
            plt.xticks(x, countries, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            # Save to file and convert to base64
            country_dist_chart_file = viz_dir / f"country_distribution_{country.lower()}.png"
            plt.savefig(country_dist_chart_file)
            
            # Convert to base64 for embedding in reports
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            charts_data['country_distribution_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            charts_data['country_distribution_chart_file'] = str(country_dist_chart_file)
            plt.close()
            
    # 3. Concentration Risk Pie Chart
    if 'country_concentration' in results:
        countries_data = results.get('country_concentration', [])
        
        if countries_data:
            # Count countries by risk level
            high_risk = sum(1 for c in countries_data if c.get('risk_level') == 'high')
            medium_risk = sum(1 for c in countries_data if c.get('risk_level') == 'medium')
            low_risk = sum(1 for c in countries_data if c.get('risk_level') == 'low')
            
            if high_risk + medium_risk + low_risk > 0:
                plt.figure(figsize=(8, 6))
                labels = ['High Risk', 'Medium Risk', 'Low Risk']
                sizes = [high_risk, medium_risk, low_risk]
                colors = ['#e74c3c', '#f39c12', '#2ecc71']
                explode = (0.1, 0.05, 0) 
                
                plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                        autopct='%1.1f%%', shadow=True, startangle=90)
                plt.axis('equal')
                plt.title('Country Risk Distribution')
                plt.tight_layout()
                
                # Save to file and convert to base64
                country_risk_chart_file = viz_dir / f"country_risk_{country.lower()}.png"
                plt.savefig(country_risk_chart_file)
                
                # Convert to base64 for embedding in reports
                buffer = BytesIO()
                plt.savefig(buffer, format='png', dpi=100)
                buffer.seek(0)
                charts_data['country_risk_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                charts_data['country_risk_chart_file'] = str(country_risk_chart_file)
                plt.close()
    
    # 4. Risk Distribution by Product (if we have affected products)
    affected_products = results.get('affected_products_count', 0)
    if affected_products > 0 and 'highest_risk_components' in results and len(results['highest_risk_components']) > 0:
        # Extract product data from components
        product_data = {}
        for comp in results.get('highest_risk_components', []):
            for product in comp.get('products', []):
                product_id = product.get('product_id', 'unknown')
                if product_id in product_data:
                    product_data[product_id]['component_count'] += 1
                    if comp.get('tariff_vulnerable', False):
                        product_data[product_id]['tariff_vuln_count'] += 1
                    if comp.get('critical', False):
                        product_data[product_id]['critical_count'] += 1
                else:
                    product_data[product_id] = {
                        'name': product.get('product_name', 'Unknown'),
                        'component_count': 1,
                        'tariff_vuln_count': 1 if comp.get('tariff_vulnerable', False) else 0,
                        'critical_count': 1 if comp.get('critical', False) else 0
                    }
        
        # Take top 10 products by total component count
        top_products = sorted(product_data.items(), key=lambda x: x[1]['component_count'], reverse=True)[:10]
        
        if top_products:
            plt.figure(figsize=(12, 6))
            
            # Extract data for stacked bar chart
            names = [p[1]['name'] for p in top_products]
            critical = [p[1]['critical_count'] for p in top_products]
            tariff_vuln = [p[1]['tariff_vuln_count'] - p[1]['critical_count'] for p in top_products]
            other = [p[1]['component_count'] - p[1]['tariff_vuln_count'] for p in top_products]
            
            # Create positions for the bars
            x = np.arange(len(names))
            width = 0.6
            
            # Create stacked bars
            p1 = plt.bar(x, critical, width, color='#e74c3c', label='Critical & Tariff Vulnerable')
            p2 = plt.bar(x, tariff_vuln, width, bottom=critical, color='#f39c12', label='Tariff Vulnerable Only')
            p3 = plt.bar(x, other, width, bottom=[critical[i] + tariff_vuln[i] for i in range(len(critical))], 
                      color='#3498db', label='Other Components')
            
            plt.title(f'Product Vulnerability - {country}')
            plt.xlabel('Products')
            plt.ylabel('Component Count')
            plt.xticks(x, names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            # Save to file and convert to base64
            product_vuln_chart_file = viz_dir / f"product_vulnerability_{country.lower()}.png"
            plt.savefig(product_vuln_chart_file)
            
            # Convert to base64 for embedding in reports
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            charts_data['product_vulnerability_chart'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            charts_data['product_vulnerability_chart_file'] = str(product_vuln_chart_file)
            plt.close()
    
    return charts_data
