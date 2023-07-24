import yaml
import svgwrite
import networkx as nx

def create_network_topology(config_file, output_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Create an empty graph
    G = nx.Graph()

    # Add nodes (devices) to the graph
    for device in config['devices']:
        device_name = device['name']
        G.add_node(device_name)

    # Add edges (connections between devices) to the graph
    for device in config['devices']:
        device_name = device['name']
        interfaces = device['interfaces']
        for interface in interfaces:
            connected_to = interface['connected_to']
            G.add_edge(device_name, connected_to)

    # Create an SVG drawing
    dwg = svgwrite.Drawing(output_file, profile='tiny')

    # Define node and edge styles
    node_style = {'fill': 'lightblue', 'stroke': 'black', 'stroke-width': '2'}
    edge_style = {'stroke': 'black', 'stroke-width': '2'}

    # Add nodes (devices) to the SVG drawing
    for device in G.nodes():
        dwg.add(dwg.circle(center=(0, 0), r=20, **node_style))
        dwg.add(dwg.text(device, insert=(-15, 5), font_size='12px', fill='black'))

    # Add edges (connections between devices) to the SVG drawing
    for edge in G.edges():
        dwg.add(dwg.line(start=(0, 0), end=(0, 0), **edge_style))

    # Calculate positions and update node and edge coordinates
    pos = nx.spring_layout(G, seed=42)  # Set a seed for consistent layout
    for node, (x, y) in pos.items():
        dwg.add(dwg.circle(center=(x * 300, y * 300), r=20, **node_style))
        for edge in G.edges(node):
            start_x, start_y = pos[node]
            end_x, end_y = pos[edge[1]]
            dwg.add(dwg.line(start=(start_x * 300, start_y * 300), end=(end_x * 300, end_y * 300), **edge_style))

    # Save the SVG file
    dwg.save()

# Example usage
config_file = 'topology.yaml'
output_file = 'topology.svg'
create_network_topology(config_file, output_file)

