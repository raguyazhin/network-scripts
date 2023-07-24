import yaml
import networkx as nx
import matplotlib.pyplot as plt

def create_network_topology(config_file):
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

    # Draw the network topology
    pos = nx.spring_layout(G, seed=42)  # Set a seed for consistent layout
    nx.draw_networkx(G, pos, with_labels=True, node_size=800, node_color='lightblue', font_size=10, font_weight='bold', width=2)
    plt.title('Network Topology')
    plt.axis('off')
    plt.show()

# Example usage
config_file = 'topology.yaml'
create_network_topology(config_file)

