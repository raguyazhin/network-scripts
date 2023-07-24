from pysnmp.hlapi import *
from influxdb import InfluxDBClient
import binascii
import concurrent.futures

# SNMP parameters
community = 'snmain'      # SNMP community string


oids = ['ifIndex','ifDescr','ifType','ifMtu','ifSpeed','ifPhysAddress','ifAdminStatus','ifOperStatus','ifHCInOctets','ifHCOutOctets','ifHighSpeed']
#oids = ['ifIndex','ifDescr','ifType',]

# InfluxDB parameters
influxdb_host = 'localhost'  # InfluxDB host
influxdb_port = 8086  # InfluxDB port (default is 8086)
influxdb_database = 'sw_ifmib_db'  # InfluxDB database name

def get_ifindex_list(ip_address):
    # SNMPv2c configuration
    snmp_engine = SnmpEngine()
    target = CommunityData(community)
    transport = UdpTransportTarget((ip_address, 161))
    context = ContextData()

    # Retrieve ifIndex values using snmpwalk
    iterator = nextCmd(
        snmp_engine, target, transport, context,
        ObjectType(ObjectIdentity('IF-MIB', 'ifIndex')),
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
        #print(oid)
        for if_index in ifindex_list: 
            #print(oid, if_index)
            error_indication, error_status, error_index, var_binds = next(
                    getCmd(snmp_engine, target, transport, context,
                        ObjectType(ObjectIdentity('IF-MIB', oid, if_index)))
                )
            
            if error_indication:
                print(f"Error retrieving ifDescr for ifIndex {if_index}: {error_indication}")
            # else:
            #     for var_bind in var_binds:
            #         #field_value = float(var_bind[1]) if isinstance(var_bind[1], str) else var_bind[1]
            #         #print(var_bind[1])
            #         # Prepare data for InfluxDB
            #         json_body = [
            #             {
            #                 "measurement": oid,
            #                 "tags": {
            #                     "ip_address": ip_address
            #                 },
            #                 "fields": {
            #                     "value": var_bind[1]
            #                 }
            #             }
            #         ]

            else:
                    for var_bind in var_binds:
                        field_value = var_bind[1]
                        field_name = ""  # Initialize field_name with a default value
                        json_body = ""

                        # Handle specific OIDs with different data types
                        if oid == "ifIndex":
                            field_name = "index"
                            field_value = int(var_bind[1])
                        elif oid == "ifDescr":
                            field_name = "ifdescr"
                            field_value = str(var_bind[1])
                        elif oid == "ifType":
                            field_name = "iftype"
                            field_value = int(var_bind[1])
                        elif oid == "ifMtu":
                            field_name = "ifmtu"
                            field_value = int(var_bind[1])
                        elif oid == "ifSpeed":
                            field_name = "ifspeed"
                            field_value = int(var_bind[1])            
                        elif oid == "ifPhysAddress":
                            field_name = oid.replace('-', '_')
                            if isinstance(var_bind[1], OctetString):
                                if oid == 'ifPhysAddress':
                                    field_value = binascii.hexlify(var_bind[1].asOctets()).decode('utf-8').upper()
                                else:
                                    field_value = binascii.hexlify(var_bind[1].asOctets()).decode('utf-8').upper()
                            elif isinstance(var_bind[1], PhysAddress):
                                field_value = binascii.hexlify(var_bind[1].asOctets()).decode('utf-8').upper()
                            elif isinstance(var_bind[1], Integer):
                                field_value = str(var_bind[1])
                            elif isinstance(var_bind[1], DisplayString):
                                field_value = str(var_bind[1])
                            else:
                                field_value = str(var_bind[1])
                                #field_value = str(var_bind[1])
                        elif oid == "ifAdminStatus":
                            field_name = "ifadmsts"
                            field_value = int(var_bind[1])
                        elif oid == "ifOperStatus":
                            field_name = "ifoptsts"
                            field_value = int(var_bind[1])
                        # elif oid == "ifHCInOctets":
                        #     field_name = "ifhcinoct"
                        #     field_value = int(var_bind[1])
                        # elif oid == "ifHCOutOctets":
                        #     field_name = "ifhcoutoct"
                        #     field_value = int(var_bind[1])
                        elif oid == "ifHCInOctets" or oid == "ifHCOutOctets":
                            field_name = "value"
                            if var_bind[1]:
                                field_value = int(var_bind[1])
                            else:
                                field_value = 0
                        elif oid == "ifHighSpeed":
                            field_name = "ifhgspeed"
                            field_value = int(var_bind[1])

                        # elif oid == "ifAdminStatus" or oid == "ifOperStatus" or oid == "ifType" or oid == "ifMtu":
                        #     field_name = "status"
                        #     field_value = int(var_bind[1])
                        # elif oid == "ifSpeed" or oid == "ifHighSpeed" or oid == "ifHCInOctets" or oid == "ifHCOutOctets":
                        #     field_name = "value"
                        #     field_value = int(var_bind[1])  # Assuming Gauge and Counter64 OIDs are represented as floats
                        # # Add additional elif conditions for other OIDs with different data types

                        if field_name:
                            # Prepare data for InfluxDB
                            json_body = [
                                {
                                    "measurement": oid,
                                    "tags": {
                                        "ip_address": ip_address
                                    },
                                    "fields": {
                                        field_name: field_value
                                    }
                                }
                            ]
                        print(json_body)
            
                        # Write data to InfluxDB
                        influxdb_client.write_points(json_body, database=influxdb_database)

# Example usage
ip_addresses = ['172.20.9.250', '172.20.1.89', '172.20.8.131']  # Replace with your device's IP addresses


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for ip_address in ip_addresses:
        ifindex_list = get_ifindex_list(ip_address)
        #print(ifindex_list)
        #get_snmp_data(ip_address, ifindex_list, oids)
        futures.append(executor.submit(get_snmp_data, ip_address, ifindex_list, oids))

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

# #print("SNMP data stored in InfluxDB.")
