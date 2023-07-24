import subprocess
from influxdb import InfluxDBClient

# InfluxDB connection details
influxdb_host = 'localhost'
influxdb_port = 8086
influxdb_database = 'snmp_data'
influxdb_username = 'superadmin'
influxdb_password = 'Server@2023'

# Switches to monitor
switches = [
    {'name': 'Switch1', 'ip': '172.20.9.250'},
    {'name': 'Switch2', 'ip': '172.20.8.131'}
]

# InfluxDB client setup
influx_client = InfluxDBClient(host=influxdb_host,
                               port=influxdb_port,
                               username=influxdb_username,
                               password=influxdb_password,
                               database=influxdb_database)

# Function to save data to InfluxDB
def save_to_influxdb(switch_name, mib_data):
    json_body = [
        {
            "measurement": "mib_data",
            "tags": {
                "switch": switch_name
            },
            "fields": mib_data
        }
    ]
    influx_client.write_points(json_body)

# Collect MIB data from switches
for switch in switches:
    switch_name = switch['name']
    switch_ip = switch['ip']
    
    # Execute snmpwalk command to retrieve MIB data
    cmd = f"snmpwalk -v2c -c snmain {switch_ip}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Process snmpwalk output to extract MIB data
        output_lines = result.stdout.strip().split('\n')
        mib_data = {}
        for line in output_lines:
            # Parse each line of output to get OID and value
            parts = line.split('=')
            if len(parts) == 2:
                oid = parts[0].strip()
                value = parts[1].strip()
                mib_data[oid] = value
        
        # Save MIB data to InfluxDB
        save_to_influxdb(switch_name, mib_data)
        print(f"Data saved to InfluxDB for {switch_name}")
    else:
        print(f"Error retrieving MIB data from {switch_name}: {result.stderr}")
