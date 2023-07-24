import sys
import yaml
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsEllipseItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen

class NetworkTopologyEditor(QMainWindow):
    def __init__(self, config_file):
        super().__init__()
        self.setWindowTitle('Network Topology Editor')

        # Load the configuration file
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

        # Create a QGraphicsScene and set its dimensions
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        # Create a QGraphicsView and set the scene
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # Initialize device positions from the configuration
        self.device_positions = {}
        for device in self.config['devices']:
            device_name = device['name']
            position = device.get('position', (0, 0))  # Use (0, 0) as default position
            self.device_positions[device_name] = position

        # Draw the network topology
        self.draw_network_topology()

    def draw_network_topology(self):
        # Clear the scene
        self.scene.clear()

        # Draw nodes (devices)
        for device_name, position in self.device_positions.items():
            device_item = QGraphicsEllipseItem(position[0], position[1], 40, 40)
            device_item.setFlag(QGraphicsEllipseItem.ItemIsMovable)  # Enable device movement
            device_item.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)  # Enable position updates
            device_item.setData(0, device_name)  # Store device name as item data
            self.scene.addItem(device_item)

        # Draw edges (connections between devices)
        for device in self.config['devices']:
            device_name = device['name']
            interfaces = device['interfaces']
            for interface in interfaces:
                connected_to = interface['connected_to']
                if connected_to in self.device_positions:
                    start_pos = self.device_positions[device_name]
                    end_pos = self.device_positions[connected_to]
                    line_item = self.scene.addLine(start_pos[0] + 20, start_pos[1] + 20, end_pos[0] + 20, end_pos[1] + 20)
                    line_item.setPen(QPen(Qt.black, 2))

    def save_device_positions(self):
        # Update the configuration with the edited device positions
        for device in self.config['devices']:
            device_name = device['name']
            if device_name in self.device_positions:
                device['position'] = self.device_positions[device_name]

        # Save the updated configuration to a YAML file
        output_file = 'updated_topology.yaml'
        with open(output_file, 'w') as file:
            yaml.dump(self.config, file)

        print(f"Device positions saved to {output_file}")

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionChange and self.sender().type() == QGraphicsEllipseItem.Type:  # Use QGraphicsEllipseItem.Type to check the item type
            device_name = self.sender().data(0)
            new_pos = value - self.sender().pos()
            self.device_positions[device_name] = (new_pos.x(), new_pos.y())
            self.draw_network_topology()

