import subprocess
from influxdb import InfluxDBClient

# InfluxDB connection details
influxdb_host = 'localhost'
influxdb_port = 8086
influxdb_database = 'mib_data'
influxdb_username = 'your_username'
influxdb_password = 'your_password'

# SNMPv3 parameters
snmp_user = 'your_username'
snmp_auth_key = 'your_auth_key'
snmp_priv_key = 'your_priv_key'
snmp_auth_protocol = 'sha'  # Options: sha, md5
snmp_priv_protocol = 'des'  # Options: des, aes

# Switches to monitor
switches = [
    {'name': 'Switch1', 'ip': '192.168.0.1'},
    {'name': 'Switch2', 'ip': '192.168.0.2'}
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
    
    # Execute snmpget command to retrieve MIB data
    cmd = f"snmpget -v3 -u {snmp_user} -l authPriv -a {snmp_auth_protocol} -A {snmp_auth_key} -x {snmp_priv_protocol} -X {snmp_priv_key} {switch_ip}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Process snmpget output to extract MIB data
        output = result.stdout.strip()
        parts = output.split(' = ')
        if len(parts) == 2:
            oid = parts[0].strip()
            value = parts[1].strip()
            mib_data = {oid: value}
            
            # Save MIB data to InfluxDB
            save_to_influxdb(switch_name, mib_data)
            print(f"Data saved to InfluxDB for {switch_name}")
        else:
            print(f"Error parsing MIB data from {switch_name}")
    else:
        print(f"Error retrieving MIB data from {switch_name}: {result.stderr}")
