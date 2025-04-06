# Nova Prophet - Supply Chain Analysis System

Nova Prophet is a graph-based deep reasoning system that predicts various outcomes in supply chains based on graph interactions. The system consists of three main components:

1. **SIGNUS** - The agentic system which feeds Nova Prophet with all the information
2. **Nova Prophet** - The core prediction system
3. **Veritas** - The deep reasoning system which seeks the "truth" from the underlying data

## Project Structure

```
supply-chain-analysis/
├── data/                # Data directory
├── src/                 # Source code
│   ├── simple_graph_builder.py
│   ├── veritas.py
│   ├── prophet/
│   └── signus/
├── scripts/             # Utility scripts
│   ├── build_graph.py
│   └── prophet_cli.py
├── output/              # Output directory for reports
└── logs/                # Log files
```

## Getting Started

### Prerequisites

- Python 3.8+
- NetworkX
- pandas
- matplotlib

Install the required packages:

```bash
pip install networkx pandas matplotlib
```

### Building the Supply Chain Graph

1. Place your data files in the `data/` directory
2. Run the build_graph script:

```bash
python scripts/build_graph.py
```

This will create a `supply_chain.pickle` file in the `output/` directory.

### Running Analysis

Use the prophet_cli.py script to run various analyses:

```bash
# Analyze a company
python scripts/prophet_cli.py --graph output/supply_chain.pickle analyze company EC001

# Predict the impact of tariff changes
python scripts/prophet_cli.py --graph output/supply_chain.pickle predict tariff  --country China --increase 25 

#Running a Comprehensive Tariff Vulnerability Analysis
python scripts/prophet_cli.py  --graph output/supply_chain.pickle analyze tariff-vulnerability 
```

## Components

### SimpleGraphBuilder

Constructs a graph representation of the supply chain from JSON data files.

### Veritas

The truth analysis engine that analyzes supply chain graphs to extract meaningful insights and identify:
- Critical components
- Single points of failure
- Geographical concentration
- Tariff vulnerabilities

### Nova Prophet

The prediction system that simulates various scenarios and predicts their impact on the supply chain, including:
- Tariff changes
- Supplier disruptions
- Geopolitical events
- Component shortages

## Data Sources

The system uses several JSON data files to build the supply chain graph:

- `electronics-tech-companies.json`: Information about electronics companies
- `product_components_*.json`: Information about product components for different product categories

## Output

Analysis results are saved to the `output/` directory in either JSON 
