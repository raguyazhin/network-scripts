from pysnmp.hlapi import *
from influxdb import InfluxDBClient
import concurrent.futures

# SNMP parameters
community = 'snmain'      # SNMP community string


oids = ['ifIndex','ifDescr','ifType','ifMtu','ifSpeed','ifPhysAddress','ifAdminStatus','ifOperStatus','ifHCInOctets','ifHCOutOctets','ifHighSpeed']

# InfluxDB parameters
influxdb_host = 'localhost'  # InfluxDB host
influxdb_port = 8086  # InfluxDB port (default is 8086)
influxdb_database = 'snmp_data'  # InfluxDB database name

def get_ifindex_list(ip_address):
    # SNMPv2c configuration
    snmp_engine = SnmpEngine()
    target = CommunityData(community)
    transport = UdpTransportTarget((ip_address, 161))
    context = ContextData()

    # Retrieve ifIndex values using snmpwalk
    iterator = nextCmd(
        snmp_engine, target, transport, context,
        lexicographicMode=False
    )

    ifindex_list = []

    for error_indication, error_status, error_index, var_binds in iterator:
        if error_indication:
            print(f"Error: {error_indication}")
            break
        elif error_status:
            print(f"Error: {error_status}")
            break
        else:
            for var_bind in var_binds:
                ifindex_list.append(var_bind[1])

    return ifindex_list

def get_snmp_data(ip_address, ifindex_list, oid_list):
    # SNMPv2c configuration
    snmp_engine = SnmpEngine()
    target = CommunityData(community)
    transport = UdpTransportTarget((ip_address, 161))
    context = ContextData()

    influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)

   

    for oid in oid_list:
        print(oid)
        for if_index in ifindex_list:
            # Retrieve ifDescr
            error_indication, error_status, error_index, var_binds = next(
                getCmd(snmp_engine, target, transport, context,
                    ObjectType(ObjectIdentity('IF-MIB', oid, if_index)))
            )
            if error_indication:
                print(f"Error retrieving ifDescr for ifIndex {if_index}: {error_indication}")
            else:
                for var_bind in var_binds:
                    if_descr = var_bind[1]

                    # Prepare data for InfluxDB
                    json_body = [
                        {
                            "measurement": oid_value,
                            "tags": {
                                "ip_address": ip_address
                            },
                            "fields": {
                                "value": if_descr
                            }
                        }
                    ]

                    #print(json_body)

                    # Write data to InfluxDB
                    #influxdb_client.write_points(json_body, database=influxdb_database)


        # Retrieve other SNMP data (ifSpeed, ifAdminStatus, ifHCInOctets, ifHCOutOctets) in a similar manner

# Example usage
ip_addresses = ['172.20.9.250', '172.20.1.89', '172.20.8.131']  # Replace with your device's IP addresses
print(ip_addresses)
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for ip_address in ip_addresses:
        ifindex_list = get_ifindex_list(ip_address)
        futures.append(executor.submit(get_snmp_data, ip_address, ifindex_list, oids))

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)

#print("SNMP data stored in InfluxDB.")
