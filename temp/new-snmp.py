from pysnmp.hlapi import *
import concurrent.futures

def get_ifindex_list(ip_address, community):
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

def get_snmp_data(ip_address, community, ifindex_list):
    # SNMPv2c configuration
    snmp_engine = SnmpEngine()
    target = CommunityData(community)
    transport = UdpTransportTarget((ip_address, 161))
    context = ContextData()

    for if_index in ifindex_list:
        # Retrieve ifDescr
        error_indication, error_status, error_index, var_binds = next(
            getCmd(snmp_engine, target, transport, context,
                   ObjectType(ObjectIdentity('IF-MIB', 'ifDescr', if_index)))
        )
        if error_indication:
            print(f"Error retrieving ifDescr for ifIndex {if_index}: {error_indication}")
        else:
            for var_bind in var_binds:
                print(f"ifDescr: {var_bind[1]}")

        # Retrieve ifSpeed
        error_indication, error_status, error_index, var_binds = next(
            getCmd(snmp_engine, target, transport, context,
                   ObjectType(ObjectIdentity('IF-MIB', 'ifSpeed', if_index)))
        )
        if error_indication:
            print(f"Error retrieving ifSpeed for ifIndex {if_index}: {error_indication}")
        else:
            for var_bind in var_binds:
                print(f"ifSpeed: {var_bind[1]}")

        # Retrieve ifAdminStatus
        error_indication, error_status, error_index, var_binds = next(
            getCmd(snmp_engine, target, transport, context,
                   ObjectType(ObjectIdentity('IF-MIB', 'ifAdminStatus', if_index)))
        )
        if error_indication:
            print(f"Error retrieving ifAdminStatus for ifIndex {if_index}: {error_indication}")
        else:
            for var_bind in var_binds:
                print(f"ifAdminStatus: {var_bind[1]}")

        # Retrieve ifHCInOctets
        error_indication, error_status, error_index, var_binds = next(
            getCmd(snmp_engine, target, transport, context,
                   ObjectType(ObjectIdentity('IF-MIB', 'ifHCInOctets', if_index)))
        )
        if error_indication:
            print(f"Error retrieving ifHCInOctets for ifIndex {if_index}: {error_indication}")
        else:
            for var_bind in var_binds:
                print(f"ifHCInOctets: {var_bind[1]}")

        # Retrieve ifHCOutOctets
        error_indication, error_status, error_index, var_binds = next(
            getCmd(snmp_engine, target, transport, context,
                   ObjectType(ObjectIdentity('IF-MIB', 'ifHCOutOctets', if_index)))
        )
        if error_indication:
            print(f"Error retrieving ifHCOutOctets for ifIndex {if_index}: {error_indication}")
        else:
            for var_bind in var_binds:
                print(f"ifHCOutOctets: {var_bind[1]}")

# Example usage
ip_addresses = ['172.20.9.250', '172.20.1.89', '172.20.8.131', '172.20.9.13', '172.20.8.150']  # Replace with your device's IP addresses
community = 'snmain'      # Replace with your SNMP community string

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for ip_address in ip_addresses:
        ifindex_list = get_ifindex_list(ip_address, community)
        futures.append(executor.submit(get_snmp_data, ip_address, community, ifindex_list))

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)
