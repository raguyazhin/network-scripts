import yaml
import svgwrite
import networkx as nx


def create_network_topology(config_file, output_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Create an empty graph
    G = nx.Graph()

    # Create an empty SVG drawing
    dwg = svgwrite.Drawing(output_file, profile='tiny')

    # Define node and edge styles
    node_style = {'fill': 'lightblue', 'stroke': 'black', 'stroke-width': '2'}
    edge_style = {'stroke': 'black', 'stroke-width': '2'}

    # Add nodes (devices) to the SVG drawing
    for device in config['devices']:
        device_name = device['name']
        dwg.add(dwg.circle(center=(0, 0), r=20, **node_style))  # Draw a circle as a node
        dwg.add(dwg.text(device_name, insert=(-15, 5), font_size='12px', fill='black'))  # Add label for the node

    # Add edges (connections between devices) to the SVG drawing
    for device in config['devices']:
        device_name = device['name']
        interfaces = device['interfaces']
        for interface in interfaces:
            connected_to = interface['connected_to']
            dwg.add(dwg.line(start=(0, 0), end=(0, 0), **edge_style))  # Draw a line as an edge

    # Calculate positions and update node and edge coordinates
    node_positions = nx.spring_layout(G, seed=42)  # Set a seed for consistent layout
    for node, (x, y) in node_positions.items():
        dwg.node(node).translate(x=x*300, y=y*300)  # Scale and translate node position
        for edge in dwg.edges(node):
            edge.translate(x1=x*300, y1=y*300, x2=x*300, y2=y*300)  # Update edge coordinates

    # Save the SVG file
    dwg.save()

# Example usage
config_file = 'topology1.yaml'
output_file = 'topology.svg'
create_network_topology(config_file, output_file)

