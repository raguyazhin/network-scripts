from pysnmp.hlapi import *

# SNMPv2 credentials
community_string = 'snmain'  # Replace with your SNMPv2 community string
switch_ip = '172.20.8.131'  # Replace 'switch_ip' with the actual IP address of the switch

# OID string for VLAN membership information
oid = '1.3.6.1.2.1.17.7.1.4.3.1.2'

# Create SNMP object
snmp_object = ObjectIdentity(oid)

# Create SNMP walk generator
snmp_walk = nextCmd(SnmpEngine(),
                    CommunityData(community_string),
                    UdpTransportTarget((switch_ip, 161)),
                    ContextData(),
                    ObjectType(snmp_object),
                    lexicographicMode=False)

# Process SNMP walk results
for error_indication, error_status, error_index, var_binds in snmp_walk:
    if error_indication:
        print(f"SNMP error: {error_indication}")
        break
    elif error_status:
        print(f"SNMP error: {error_status.prettyPrint()}")
        break
    else:
        for var_bind in var_binds:
            vlan_hex = var_bind[1].prettyPrint()
            vlan_id = int(var_bind[0][-1])  # Extract the port index from the OID
            print(f"Port {vlan_id} VLAN membership: {vlan_hex}")

            # Convert VLAN membership from hexadecimal to binary format
            # port_membership_binary = bin(int(port_membership_hex, 16))[2:].zfill(len(port_membership_hex) * 4)

            # # Identify positions of '1' values
            # vlan_positions = [i + 1 for i, bit in enumerate(port_membership_binary[::-1]) if bit == '1']

            # print(f"Port {port_index} VLAN membership (Binary): {port_membership_binary}")
            # print(f"Port {port_index} VLAN positions: {vlan_positions}")
def hex_to_binary(vlan_hex):
    binary_digit = bin(int(hex_digit, 16))[2:].zfill(4)
    return binary_digit

binary_digit = ""

# Example usage
vlan_hex = 'FE EF FF FF F3 FF 00 00 00 00 00 00 00 00 00 00'
vlan_hex = str(hex_digit).replace(' ','')
for index in vlan_hex:
    print(index)
    binary_digit = str(binary_digit) + str(hex_to_binary(index))
    
print(f"{binary_digit}")    
