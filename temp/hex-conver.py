from pysnmp.hlapi import *


# def hex_to_binary(hex_digit):
#     binary_digit = bin(int(hex_digit, 16))[2:].zfill(4)
#     return binary_digit

# binary_digit = ""

# # Example usage
# hex_digit = 'FE EF FF FF F3 FF 00 00 00 00 00 00 00 00 00 00'
# hex_digit = str(hex_digit).replace(' ','')
# for index in hex_digit:
#     print(index)
#     binary_digit = str(binary_digit) + str(hex_to_binary(index))
    
# print(f"{binary_digit}")    

#########################################################################
# def get_matching_positions(arrays):
#     # Get positions of matching elements
#     positions = []
#     for idx, items in enumerate(zip(*arrays)):
#         if all(x == items[0] for x in items):
#             positions.append(idx)
#     return positions

# # Example arrays
# array1 = ["0","0","1"]
# array2 = ["1","0","0"]
# array3 = ["0","0","1"]

# # Get matching positions
# matching_positions = get_matching_positions([array1, array2, array3])

# # Print the positions
# for position in matching_positions:
#     print(position)


###################################################################################

# Example usage
community = 'public'
ip_address = '172.20.8.101'
port = 161

trunk_port_oid = '1.3.6.1.2.1.17.7.1.4.3.1.2'

def snmp_walk_vlan(community, ip_address, port, oid):
    result_array = []
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
    for response in iterator:
        errorIndication, errorStatus, errorIndex, varBinds = response
        if errorIndication:
            print(f'Error: {errorIndication}')
            break
        elif errorStatus:
            print(f'Error: {errorStatus.prettyPrint()}')
            break
        else:
            for varBind in varBinds:
                value = varBind[1].prettyPrint()
                result_array.append(value)
    return result_array

trunk_ports = snmp_walk_vlan(community, ip_address, port, trunk_port_oid)

def get_matching_positions(arrays):
    # Get positions of matching elements
    positions = []
    for idx, items in enumerate(zip(*arrays)):
        if all(x == items[0] for x in items):
            positions.append(idx+1)
    return positions

def hex_to_binary(hex_string):
    binary_digit = ''
    for hex in hex_string:
        # print(hex)
        binary_digit = str(binary_digit) + str(bin(int(hex, 16))[2:].zfill(4))
    return binary_digit

tag_port_array = []
for index in trunk_ports:
    #print(index[2:])
    #tag_port_array.append(string_to_array(hex_to_binary(index[2:])))
    tag_port_array.append(hex_to_binary(index[2:]))

tag_port_value = []
tag_port_value = get_matching_positions(tag_port_array)

print(tag_port_array)