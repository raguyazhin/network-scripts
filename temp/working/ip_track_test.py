from pysnmp.hlapi import *
import binascii

## OID for SNMP walk
# vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
# mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'



def snmp_walk(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = []

    # Perform SNMP walk
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    # Process the SNMP walk iterator
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
                value = varBind[1]
                result_array.append(value)

    return result_array

def snmp_walk_index(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = {}

    # Perform SNMP walk
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    # Process the SNMP walk iterator
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
                value = varBind[1]
                result_array[varBind[0]] = varBind[1]

    return result_array

def snmp_get(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = []

    # Perform SNMP GET
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip_address, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    # Check for SNMP errors
    if errorIndication:
        print(f'Error: {errorIndication}')
    elif errorStatus:
        print(f'Error: {errorStatus.prettyPrint()}')
    else:
        for varBind in varBinds:
            value = varBind[1]
            #print(varBind[0], "Hi", varBind[1])
            result_array.append(value)

    return result_array


def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

# Example usage
community = 'snmain'
ip_address = '172.20.1.111'
port = 161

# OID for SNMP walk
vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'
bridge_port_oid = '1.3.6.1.2.1.17.4.3.1.2'
if_index_oid = '1.3.6.1.2.1.2.2.1.1'
port_name_oid = '1.3.6.1.2.1.31.1.1.1.1'
local_port_oid = '1.3.6.1.2.1.17.1.4.1.2'
trunck_port_oid = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'
vlan_name_oid = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
arp_ip_add = '1.3.6.1.2.1.4.22.1.3'
arp_mac_add = '1.3.6.1.2.1.3.1.1.2'

vlan_id = snmp_walk(community, ip_address, port, vlan_oid)

bridge_port_id = snmp_walk(community, ip_address, port, bridge_port_oid)

if_index_value = snmp_walk(community, ip_address, port, if_index_oid)

bridge_port_value = snmp_walk_index(community, ip_address, port, bridge_port_oid)

mac_address_value = snmp_walk_index(community, ip_address, port, mac_address_oid)

#local_port_value = snmp_walk(community, ip_address, port, local_port_oid + '.' + str(bridge_port))

unique_array = list(set(vlan_id))

bridge_port_array = list(set(bridge_port_id))

result_array = []

for bridge_port_val in bridge_port_array:
    local_port_array = snmp_get(community, ip_address, port, local_port_oid + '.' + str(bridge_port_val))
    for local_port_val in local_port_array:
        local_port_trunk = snmp_get(community, ip_address, port, trunck_port_oid + '.' + str(local_port_val))
        for local_port_trunk_val in local_port_trunk:
            if (local_port_trunk_val != 1):
                print(bridge_port_val,local_port_val,local_port_trunk_val)
                local_port_name = snmp_get(community, ip_address, port, port_name_oid + '.' + str(local_port_val))
                for local_port_name_val in local_port_name:
                    result_array.append([bridge_port_val,local_port_val,local_port_name_val,local_port_trunk_val])

for res_val,val1,val2,val3 in result_array:
    print(res_val)
    bridge_port_key = (list(bridge_port_value.keys())[list(bridge_port_value.values()).index(res_val)])
    mac_array_key = str(bridge_port_key).replace(bridge_port_oid,mac_address_oid)
    print(mac_array_key)
    for index in mac_address_value:
        if str(index) == str(mac_array_key):
            print(index,convert_mac(mac_address_value[index]),res_val,val1,val2,val3)
    #print(mac_address_value[mac_array_key])

# for index in bridge_port_value:
#     print(index,bridge_port_value[index])mac_address_value

# trunck_port_value = snmp_walk(community, ip_address, port, trunck_port_oid)

# 1.3.6.1.2.1.17.4.3.1.1.0.48.145.129.35.250 
# 1.3.6.1.2.1.17.4.3.1.1.0.48.145.129.35.250
# def non_trunck_port(pair):
#     key, value = pair
#     if value > 1:
#         return True
#     else:
#         return False


# def replace_dic_oid(dict_value,find_value,replace_value):
#     replace_dict = {}
#     for index in dict_value:        
#         replace_val = str(index).replace(find_value,replace_value)
#         replace_dict[replace_val] = dict_value[index]
#         #print(str(index).replace(find_value,replace_value),dict_value[index])

#     return replace_dict
    
# non_trunck_port_value = dict(filter(non_trunck_port,trunck_port_value.items()))
# for value in non_trunck_port_value:
#     print(value,non_trunck_port_value[value])

# # for index in non_trunck_port_value:
# #     print(index, non_trunck_port_value[index])

# mac_address_value = snmp_walk(community, ip_address, port, mac_address_oid)

# mac_address_oid_replace = replace_dic_oid(mac_address_value,mac_address_oid,"");



# bridge_port_oid_replace = replace_dic_oid(bridge_port_value,bridge_port_oid,"");

# # mac_address_dic = {}

# # for index in mac_address_oid_replace:
# #     print(index,convert_mac(mac_address_oid_replace[index]))

# # for index in bridge_port_oid_replace:
# #     print(index,bridge_port_oid_replace[index])

# # bridge_port_value = snmp_walk(community, ip_address, port, bridge_port_oid)

# # for index in bridge_port_value:
# #        print(index)

# # bridge_port_dic = {}

# # for index in bridge_port_value:
# #     bridge_port_dic[index] = bridge_port_value[index]


# mac_address_set = set(mac_address_oid_replace)
# # #print(mac_address_set)

# bridge_port_set = set(bridge_port_oid_replace)
# # #print(bridge_port_set)


# comm_keys = mac_address_set.intersection(bridge_port_set)

# for key in comm_keys:# &  set(bridge_port_oid_replace.items()):
#     if not (bridge_port_oid_replace[key] == 25 or bridge_port_oid_replace[key] == 24 or bridge_port_oid_replace[key] == 21 or bridge_port_oid_replace[key] == 2):
#     #     print()
#     # else:   
#         print(key,convert_mac(mac_address_oid_replace[key]),bridge_port_oid_replace[key])

