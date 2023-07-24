from influxdb import InfluxDBClient
from pysnmp.hlapi import *

# SNMP and InfluxDB settings (update as needed)
community = 'snmain'  # SNMP community string
influxdb_host = 'localhost'
influxdb_port = 8086
influxdb_database = 'snmp_data'

oids = {
    'ifIndex': '1.3.6.1.2.1.2.2.1.1',
    'ifDescr': '1.3.6.1.2.1.2.2.1.2',
    'ifOperStatus': '1.3.6.1.2.1.2.2.1.8'
}

switches = [
    {'ip': '172.20.9.250', 'name': 'Switch1'},
    {'ip': '172.20.1.89', 'name': 'Switch2'},
    # Add more switches here
]

# InfluxDB client
influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)

# SNMP data retrieval function
def get_snmp_data(switch):
    results = []
    for oid_name, oid_value in oids.items():
        error_indication, error_status, error_index, var_binds = next(
            getCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((switch['ip'], 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid_value)),
            )
        )
        if error_indication:
            print(f"Error: {error_indication}")
            return
        elif error_status:
            print(
                f"Error: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
            )
            return

        result = {
            'measurement': oid_name,
            'tags': {
                'switch': switch['name'],
            },
            'fields': {
                'value': str(var_binds[0][1]),
            },
        }
        results.append(result)

    return results

# Main function
def main():
    all_results = []
    for switch in switches:
        results = get_snmp_data(switch)
        all_results.extend(results)

    # Save the results to InfluxDB
    influxdb_client.switch_database(influxdb_database)
    print(all_results)
    influxdb_client.write_points(all_results)

    print("Data saved to InfluxDB successfully.")

#Execute the main function
if __name__ == '__main__':
    main()
#main()