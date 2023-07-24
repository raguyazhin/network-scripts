import yaml

def create_network_topology(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    for device in config['devices']:
        device_name = device['name']
        device_type = device['type']
        interfaces = device['interfaces']

        print(f"Device: {device_name} (Type: {device_type})")
        print("Interfaces:")
        for interface in interfaces:
            interface_name = interface['name']
            connected_to = interface['connected_to']
            print(f"- {interface_name} (Connected to: {connected_to})")
        print()

# Example usage
config_file = 'topology.yaml'
create_network_topology(config_file)

