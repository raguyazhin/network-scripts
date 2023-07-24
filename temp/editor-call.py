import sys
from PyQt5.QtWidgets import QApplication
from network_topology_editor import NetworkTopologyEditor

if __name__ == '__main__':
    # Path to the configuration file
    config_file = 'topology.yaml'

    # Create the application
    app = QApplication(sys.argv)

    # Create the network topology editor
    editor = NetworkTopologyEditor(config_file)

    # Show the main window
    editor.show()

    # Run the application event loop
    sys.exit(app.exec_())

