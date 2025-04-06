"""
html_report.py - HTML report generation for tariff analysis

This module generates visually appealing HTML reports for tariff analysis,
both for individual scenarios and comparisons between multiple scenarios.
"""

from datetime import datetime
from pathlib import Path
import os
import json
import base64

# Common CSS styles used in all reports
COMMON_CSS = """
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
    --light-color: #ecf0f1;
    --dark-color: #2c3e50;
    --border-radius: 8px;
    --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Roboto', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    padding: 0;
    margin: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: var(--primary-color);
    color: white;
    padding: 20px 0;
    margin-bottom: 30px;
}

header .container {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.logo {
    display: flex;
    align-items: center;
}

.logo i {
    font-size: 2.5rem;
    margin-right: 10px;
}

h1, h2, h3, h4 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.header-meta {
    text-align: right;
}

.card {
    background-color: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: 20px;
    overflow: hidden;
}

.card-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    background-color: var(--light-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.card-body {
    padding: 20px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.success {
    color: var(--success-color);
}

.warning {
    color: var(--warning-color);
}

.danger {
    color: var(--danger-color);
}

.primary {
    color: var(--secondary-color);
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
}

table th, table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

table th {
    background-color: var(--light-color);
    font-weight: 500;
}

table tbody tr:hover {
    background-color: rgba(236, 240, 241, 0.3);
}

.chart-container {
    margin-top: 20px;
    text-align: center;
}

.chart-container img {
    max-width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

footer {
    margin-top: 40px;
    text-align: center;
    color: #777;
    padding: 20px;
    border-top: 1px solid #eee;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }
    
    header .container {
        flex-direction: column;
        text-align: center;
    }
    
    .header-meta {
        text-align: center;
        margin-top: 15px;
    }
    
    .logo {
        justify-content: center;
        margin-bottom: 10px;
    }
}
"""

def create_report_directory():
    """
    Create the reports directory if it doesn't exist
    
    Returns:
        Path object for the reports directory
    """
    report_dir = Path("./reports")
    report_dir.mkdir(exist_ok=True)
    return report_dir

def generate_timestamp():
    """
    Generate a formatted timestamp string
    
    Returns:
        String with formatted date and time
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def safe_get(data, *keys, default=0):
    """
    Safely get a value from a nested dictionary
    
    Args:
        data: The dictionary to extract values from
        keys: A sequence of keys to traverse
        default: The default value to return if the key path is invalid
        
    Returns:
        The value at the key path or the default value
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def get_color_class(value, threshold_low, threshold_high, inverse=False):
    """
    Determine the color class based on a value and thresholds
    
    Args:
        value: The value to evaluate
        threshold_low: Lower threshold value
        threshold_high: Higher threshold value
        inverse: Whether higher values are worse (True) or better (False)
        
    Returns:
        String with the CSS class name
    """
    if inverse:
        if value < threshold_low:
            return "success"
        elif value > threshold_high:
            return "danger"
        else:
            return "warning"
    else:
        if value > threshold_high:
            return "success"
        elif value < threshold_low:
            return "danger"
        else:
            return "warning"

def create_chart_div(charts_data, key):
    """
    Generate HTML for including a chart if it exists in the data
    
    Args:
        charts_data: Dictionary of chart data
        key: The key for the chart to include
        
    Returns:
        HTML string for the chart or empty string
    """
    if key in charts_data and charts_data[key]:
        alt_text = key.replace("_", " ").title()
        return f'<div class="chart-container"><img src="data:image/png;base64,{charts_data[key]}" alt="{alt_text} Chart"></div>'
    return ""

def generate_html_report(country, results, charts_data):
    """
    Generate an HTML report for tariff impact analysis.
    
    Args:
        country: Country being analyzed
        results: Dictionary containing analysis results
        charts_data: Dictionary containing chart data
        
    Returns:
        Path to the generated report
    """
    # Extract needed data
    affected_components_count = safe_get(results, 'affected_components_count', default=0)
    affected_components = safe_get(results, 'affected_components', default=[])
    affected_products_count = safe_get(results, 'affected_products_count', default=0)
    affected_products = safe_get(results, 'affected_products', default=[])
    price_impacts = safe_get(results, 'price_impacts', default={})
    resilience_impact = safe_get(results, 'resilience_impact', default={})
    recommendations = safe_get(results, 'recommendations', default=[])
    
    # Get increase percentage
    increase_percentage = safe_get(results, 'increase_percentage', default=0)
    
    # Create output directory if it doesn't exist
    report_dir = create_report_directory()
    
    # Generate filename
    country_slug = country.lower().replace(' ', '_') if country else "unknown"
    filename = f"tariff_analysis_{country_slug}_{increase_percentage:+}_{generate_timestamp()}.html"
    filepath = report_dir / filename
    
    # Build component rows HTML
    component_rows = ""
    for comp in affected_components[:10]:
        comp_name = safe_get(comp, 'component_name', default='Unknown')
        comp_type = safe_get(comp, 'component_type', default='Unknown')
        price_increase = safe_get(comp, 'estimated_price_increase', default=0)
        
        component_rows += f"""
        <tr>
            <td>{comp_name}</td>
            <td>{comp_type}</td>
            <td>{price_increase:.1f}%</td>
        </tr>
        """
    
    # Build product rows HTML
    product_rows = ""
    for prod in affected_products[:10]:
        prod_name = safe_get(prod, 'product_name', default='Unknown')
        manufacturer = safe_get(prod, 'manufacturer', default='Unknown')
        price_increase = safe_get(prod, 'estimated_price_increase_percentage', default=0)
        critical_components = safe_get(prod, 'critical_components_count', default=0)
        
        price_class = get_color_class(price_increase, 2, 5, inverse=True)
        
        product_rows += f"""
        <tr>
            <td>{prod_name}</td>
            <td>{manufacturer}</td>
            <td class="{price_class}">{price_increase:.1f}%</td>
            <td>{critical_components}</td>
        </tr>
        """
    
    # Build recommendation items HTML
    recommendation_items = ""
    for i, rec in enumerate(recommendations[:5]):
        desc = safe_get(rec, 'description', default='No description available')
        priority = safe_get(rec, 'priority', default='medium').lower()
        benefit = safe_get(rec, 'estimated_benefit', default='Unknown')
        
        recommendation_items += f"""
        <div class="recommendation-item">
            <div class="recommendation-header">
                <h4><i class="fas fa-check-circle"></i> Recommendation {i+1}</h4>
                <span class="priority priority-{priority}">{priority.upper()}</span>
            </div>
            <p>{desc}</p>
            <p class="benefit"><strong>Benefit:</strong> {benefit}</p>
        </div>
        """
    
    # Individual report specific CSS
    individual_report_css = """
    .stat-card {
        background-color: white;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: #777;
    }
    
    .stat-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .recommendations {
        margin-top: 30px;
    }
    
    .recommendation-item {
        margin-bottom: 15px;
        padding: 15px;
        border-radius: var(--border-radius);
        background-color: white;
        box-shadow: var(--box-shadow);
    }
    
    .recommendation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .priority {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .priority-high {
        background-color: var(--danger-color);
        color: white;
    }
    
    .priority-medium {
        background-color: var(--warning-color);
        color: white;
    }
    
    .priority-low {
        background-color: var(--success-color);
        color: white;
    }
    
    .benefit {
        font-style: italic;
        color: #777;
    }
    
    .resilience-marker {
        position: relative;
    }
    
    .resilience-value {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 2rem;
        font-weight: bold;
    }
    """
    
    # Get color classes
    tariff_change_class = get_color_class(increase_percentage, 0, 10, inverse=True)
    
    avg_price_increase = safe_get(price_impacts, 'average_product_price_increase', default=0)
    avg_price_class = get_color_class(avg_price_increase, 2, 5, inverse=True)
    
    resilience_before = safe_get(resilience_impact, 'before', default=0)
    resilience_before_class = get_color_class(resilience_before, 60, 80)
    
    resilience_after = safe_get(resilience_impact, 'after', default=0)
    resilience_after_class = get_color_class(resilience_after, 60, 80)
    
    resilience_change = safe_get(resilience_impact, 'change', default=0)
    resilience_change_class = get_color_class(resilience_change, -5, 0)
    
    # Format values
    avg_price_increase_fmt = f"{avg_price_increase:.2f}%"
    max_price_increase = safe_get(price_impacts, 'max_product_price_increase', default=0)
    max_price_increase_fmt = f"{max_price_increase:.2f}%"
    
    resilience_before_fmt = f"{resilience_before:.1f}"
    resilience_after_fmt = f"{resilience_after:.1f}"
    resilience_change_fmt = f"{resilience_change:+.1f}"
    
    # Include charts
    product_chart = create_chart_div(charts_data, 'product_chart')
    component_chart = create_chart_div(charts_data, 'component_chart')
    resilience_chart = create_chart_div(charts_data, 'resilience_chart')
    risk_chart = create_chart_div(charts_data, 'risk_chart')
    
    # Start building HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tariff Analysis Report: {country} {increase_percentage:+}%</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <style>
            {COMMON_CSS}
            {individual_report_css}
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="logo">
                    <i class="fas fa-chart-line"></i>
                    <h1>Nova Prophet</h1>
                </div>
                <div class="header-meta">
                    <h2>Tariff Analysis Report</h2>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y %H:%M')}</p>
                </div>
            </div>
        </header>
        
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-info-circle"></i> Analysis Overview</h2>
                </div>
                <div class="card-body">
                    <div class="grid">
                        <div class="stat-card">
                            <i class="fas fa-globe-americas stat-icon primary"></i>
                            <div class="stat-label">Country</div>
                            <div class="stat-value">{country}</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-percentage stat-icon {tariff_change_class}"></i>
                            <div class="stat-label">Tariff Change</div>
                            <div class="stat-value">{increase_percentage:+}%</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-microchip stat-icon primary"></i>
                            <div class="stat-label">Affected Components</div>
                            <div class="stat-value">{affected_components_count}</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-box-open stat-icon primary"></i>
                            <div class="stat-label">Affected Products</div>
                            <div class="stat-value">{affected_products_count}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid">
                <!-- Left column -->
                <div>
                    <div class="card">
                        <div class="card-header">
                            <h3><i class="fas fa-tags"></i> Price Impact</h3>
                        </div>
                        <div class="card-body">
                            <div class="grid">
                                <div class="stat-card">
                                    <i class="fas fa-chart-line stat-icon {avg_price_class}"></i>
                                    <div class="stat-label">Average Price Increase</div>
                                    <div class="stat-value">{avg_price_increase_fmt}</div>
                                </div>
                                <div class="stat-card">
                                    <i class="fas fa-arrow-up stat-icon danger"></i>
                                    <div class="stat-label">Maximum Price Increase</div>
                                    <div class="stat-value">{max_price_increase_fmt}</div>
                                </div>
                            </div>
                            
                            {product_chart}
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3><i class="fas fa-microchip"></i> Affected Components</h3>
                        </div>
                        <div class="card-body">
                            <div class="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Component</th>
                                            <th>Type</th>
                                            <th>Price Impact</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {component_rows}
                                    </tbody>
                                </table>
                            </div>
                            
                            {component_chart}
                        </div>
                    </div>
                </div>
                
                <!-- Right column -->
                <div>
                    <div class="card">
                        <div class="card-header">
                            <h3><i class="fas fa-shield-alt"></i> Resilience Impact</h3>
                        </div>
                        <div class="card-body">
                            <div class="grid">
                                <div class="stat-card">
                                    <i class="fas fa-chart-bar stat-icon {resilience_before_class}"></i>
                                    <div class="stat-label">Before Tariff</div>
                                    <div class="stat-value">{resilience_before_fmt}</div>
                                    <div>out of 100</div>
                                </div>
                                <div class="stat-card">
                                    <i class="fas fa-chart-bar stat-icon {resilience_after_class}"></i>
                                    <div class="stat-label">After Tariff</div>
                                    <div class="stat-value">{resilience_after_fmt}</div>
                                    <div>out of 100</div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <i class="fas fa-exchange-alt stat-icon {resilience_change_class}"></i>
                                <div class="stat-label">Resilience Change</div>
                                <div class="stat-value">{resilience_change_fmt}</div>
                            </div>
                            
                            {resilience_chart}
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3><i class="fas fa-box-open"></i> Affected Products</h3>
                        </div>
                        <div class="card-body">
                            <div class="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Product</th>
                                            <th>Manufacturer</th>
                                            <th>Price Impact</th>
                                            <th>Critical Components</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {product_rows}
                                    </tbody>
                                </table>
                            </div>
                            
                            {risk_chart}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3><i class="fas fa-lightbulb"></i> Strategic Recommendations</h3>
                </div>
                <div class="card-body">
                    <div class="recommendations">
                        {recommendation_items}
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <div class="container">
                <p>Generated by Nova Prophet Supply Chain Prediction System</p>
                <p>&copy; {datetime.now().year} Nova Prophet</p>
            </div>
        </footer>
    </body>
    </html>
    """
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Individual report generated: {filepath}")
    return filepath

def generate_html_comparison_report(scenario_results, charts_data):
    """
    Generate an HTML report comparing multiple tariff scenarios.
    
    Args:
        scenario_results: List of dictionaries containing scenario results
        charts_data: Dictionary containing chart data
        
    Returns:
        Path to the generated report
    """
    # Create output directory if it doesn't exist
    report_dir = create_report_directory()
    
    # Generate filename
    scenario_count = len(scenario_results) if scenario_results else 0
    filename = f"tariff_scenario_comparison_{scenario_count}_scenarios_{generate_timestamp()}.html"
    filepath = report_dir / filename
    
    # Calculate min/max values for normalization (ensure no division by zero)
    price_impacts = [safe_get(r, 'price_impacts', 'average_product_price_increase') for r in scenario_results]
    resilience_changes = [safe_get(r, 'resilience_impact', 'change') for r in scenario_results]
    
    min_price_impact = min(price_impacts) if price_impacts else 0
    max_price_impact = max(price_impacts) if price_impacts else 1
    min_resilience_change = min(resilience_changes) if resilience_changes else 0
    max_resilience_change = max(resilience_changes) if resilience_changes else 1
    
    # Avoid division by zero
    if max_price_impact == min_price_impact:
        max_price_impact = min_price_impact + 1
    if max_resilience_change == min_resilience_change:
        max_resilience_change = min_resilience_change + 1
    
    # Create ranking of scenarios
    # Rank by resilience impact (higher is better)
    resilience_ranking = sorted(scenario_results, 
                               key=lambda x: safe_get(x, 'resilience_impact', 'change', default=-999), 
                               reverse=True) if scenario_results else []
    
    # Rank by price impact (lower is better)
    price_ranking = sorted(scenario_results, 
                          key=lambda x: safe_get(x, 'price_impacts', 'average_product_price_increase', default=999)) if scenario_results else []
    
    # Calculate overall best scenario
    # Define scoring weights for resilience and price (configurable parameters)
    RESILIENCE_WEIGHT = 0.6
    PRICE_WEIGHT = 0.4
    
    for result in scenario_results:
        resilience_change = safe_get(result, 'resilience_impact', 'change', default=0)
        price_impact = safe_get(result, 'price_impacts', 'average_product_price_increase', default=0)
        
        # Normalize scores (resilience: higher is better, price: lower is better)
        resilience_score = (resilience_change - min_resilience_change) / (max_resilience_change - min_resilience_change)
        price_score = 1 - ((price_impact - min_price_impact) / (max_price_impact - min_price_impact))
        
        # Combined score (weighted average)
        result['combined_score'] = resilience_score * RESILIENCE_WEIGHT + price_score * PRICE_WEIGHT
    
    # Get overall best scenario
    overall_best = max(scenario_results, key=lambda x: safe_get(x, 'combined_score', default=0)) if scenario_results else None
    
    # Build scenario overview rows
    scenario_rows = ""
    for result in scenario_results:
        scenario_name = safe_get(result, 'scenario_name', default='Unknown')
        country = safe_get(result, 'country', default='Unknown')
        increase_percentage = safe_get(result, 'increase_percentage', default=0)
        affected_components = safe_get(result, 'affected_components_count', default=0)
        affected_products = safe_get(result, 'affected_products_count', default=0)
        
        price_impact = safe_get(result, 'price_impacts', 'average_product_price_increase', default=0)
        price_class = get_color_class(price_impact, 2, 5, inverse=True)
        
        resilience_change = safe_get(result, 'resilience_impact', 'change', default=0)
        resilience_class = get_color_class(resilience_change, -5, 0)
        
        scenario_rows += f"""
        <tr>
            <td>{scenario_name}</td>
            <td>{country} {increase_percentage:+}%</td>
            <td>{affected_components}</td>
            <td>{affected_products}</td>
            <td class="{price_class}">{price_impact:.2f}%</td>
            <td class="{resilience_class}">{resilience_change:+.2f}</td>
        </tr>
        """
    
    # Create HTML for best resilience scenario
    best_resilience_html = ""
    if resilience_ranking:
        best_scenario = resilience_ranking[0]
        scenario_name = safe_get(best_scenario, 'scenario_name', default='Unknown')
        country = safe_get(best_scenario, 'country', default='Unknown')
        increase_percentage = safe_get(best_scenario, 'increase_percentage', default=0)
        resilience_change = safe_get(best_scenario, 'resilience_impact', 'change', default=0)
        
        best_resilience_html = f"""
        <div class="scenario-card">
            <div class="scenario-header">
                <span>{scenario_name}</span>
                <span class="badge badge-best">BEST</span>
            </div>
            <div class="scenario-metrics">
                <div class="metric">
                    <div class="metric-value success">{country} {increase_percentage:+}%</div>
                    <div class="metric-label">Tariff Change</div>
                </div>
                <div class="metric">
                    <div class="metric-value success">{resilience_change:+.2f}</div>
                    <div class="metric-label">Resilience Change</div>
                </div>
            </div>
        </div>
        """
    else:
        best_resilience_html = "<p>No resilience data available</p>"
    
    # Create HTML for best price impact scenario
    best_price_html = ""
    if price_ranking:
        best_scenario = price_ranking[0]
        scenario_name = safe_get(best_scenario, 'scenario_name', default='Unknown')
        country = safe_get(best_scenario, 'country', default='Unknown')
        increase_percentage = safe_get(best_scenario, 'increase_percentage', default=0)
        price_impact = safe_get(best_scenario, 'price_impacts', 'average_product_price_increase', default=0)
        
        best_price_html = f"""
        <div class="scenario-card">
            <div class="scenario-header">
                <span>{scenario_name}</span>
                <span class="badge badge-best">BEST</span>
            </div>
            <div class="scenario-metrics">
                <div class="metric">
                    <div class="metric-value success">{country} {increase_percentage:+}%</div>
                    <div class="metric-label">Tariff Change</div>
                </div>
                <div class="metric">
                    <div class="metric-value success">{price_impact:.2f}%</div>
                    <div class="metric-label">Avg Price Increase</div>
                </div>
            </div>
        </div>
        """
    else:
        best_price_html = "<p>No price data available</p>"
    
    # Create HTML for best overall scenario
    best_overall_html = ""
    if overall_best:
        scenario_name = safe_get(overall_best, 'scenario_name', default='Unknown')
        country = safe_get(overall_best, 'country', default='Unknown')
        increase_percentage = safe_get(overall_best, 'increase_percentage', default=0)
        price_impact = safe_get(overall_best, 'price_impacts', 'average_product_price_increase', default=0)
        resilience_change = safe_get(overall_best, 'resilience_impact', 'change', default=0)
        affected_products = safe_get(overall_best, 'affected_products_count', default=0)
        
        best_overall_html = f"""
        <div class="scenario-card best-scenario">
            <div class="scenario-header">
                <span>{scenario_name}</span>
                <span class="badge badge-best">BEST OVERALL</span>
            </div>
            <div class="scenario-metrics">
                <div class="metric">
                    <div class="metric-value">{country} {increase_percentage:+}%</div>
                    <div class="metric-label">Tariff Change</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{price_impact:.2f}%</div>
                    <div class="metric-label">Avg Price Increase</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{resilience_change:+.2f}</div>
                    <div class="metric-label">Resilience Change</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{affected_products}</div>
                    <div class="metric-label">Affected Products</div>
                </div>
            </div>
        </div>
        """
    else:
        best_overall_html = "<p>No scenario data available for recommendation</p>"
        
    # Include comparison charts
    price_comparison_chart = create_chart_div(charts_data, 'price_comparison_chart')
    resilience_comparison_chart = create_chart_div(charts_data, 'resilience_comparison_chart')
    scope_comparison_chart = create_chart_div(charts_data, 'scope_comparison_chart')
    
    # Comparison report specific CSS
    comparison_report_css = """
    .scenario-card {
        background-color: white;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        margin-bottom: 15px;
        padding: 15px;
        transition: transform 0.3s ease;
    }
    
    .scenario-card:hover {
        transform: translateY(-5px);
    }
    
    .scenario-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 1.2rem;
        font-weight: 500;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    
    .scenario-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px;
    }
    
    .metric {
        text-align: center;
        padding: 10px;
        background-color: var(--light-color);
        border-radius: var(--border-radius);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #777;
    }
    
    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin-left: 10px;
    }
    
    .badge-best {
        background-color: var(--success-color);
        color: white;
    }
    
    .best-scenario {
        border: 2px solid var(--success-color);
    }
    
    .recommendation {
        margin-bottom: 15px;
        padding: 15px;
        border-radius: var(--border-radius);
        background-color: white;
        box-shadow: var(--box-shadow);
    }
    
    @media (max-width: 768px) {
        .scenario-metrics {
            grid-template-columns: 1fr 1fr;
        }
    }
    """
    
    # Start building HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tariff Scenario Comparison Report</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <style>
            {COMMON_CSS}
            {comparison_report_css}
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="logo">
                    <i class="fas fa-chart-line"></i>
                    <h1>Nova Prophet</h1>
                </div>
                <div class="header-meta">
                    <h2>Tariff Scenario Comparison</h2>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y %H:%M')}</p>
                </div>
            </div>
        </header>
        
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-exchange-alt"></i> Scenarios Overview</h2>
                </div>
                <div class="card-body">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Scenario</th>
                                    <th>Tariff Change</th>
                                    <th>Components</th>
                                    <th>Products</th>
                                    <th>Avg Price Impact</th>
                                    <th>Resilience Δ</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scenario_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Visualizations -->
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-chart-bar"></i> Visual Comparison</h2>
                </div>
                <div class="card-body">
                    <div class="grid">
                        {price_comparison_chart}
                        {resilience_comparison_chart}
                        {scope_comparison_chart}
                    </div>
                </div>
            </div>
            
            <!-- Best Scenarios -->
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-trophy"></i> Scenario Ranking</h2>
                </div>
                <div class="card-body">
                    <div class="grid">
                        <div>
                            <h3>Best for Supply Chain Resilience</h3>
                            {best_resilience_html}
                        </div>
                        
                        <div>
                            <h3>Best for Price Impact</h3>
                            {best_price_html}
                        </div>
                    </div>
                    
                    <h3>Overall Recommendation</h3>
                    {best_overall_html}
                </div>
            </div>
        </div>
        
        <footer>
            <div class="container">
                <p>Generated by Nova Prophet Supply Chain Prediction System</p>
                <p>&copy; {datetime.now().year} Nova Prophet</p>
            </div>
        </footer>
    </body>
    </html>
    """
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Comparison report generated: {filepath}")
    return filepath