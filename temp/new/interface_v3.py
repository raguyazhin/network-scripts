from pysnmp.hlapi import *
import binascii

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def snmp_get(community, ip_address, port, oid):

    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip_address, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        print(f'SNMP query failed: {error_indication}')
        return None

    if error_status:
        print(f'SNMP query failed: {error_status.prettyPrint()}')
        return None

    for var_bind in var_binds:
        return var_bind[1]
    
def snmp_walk_index(community, ip_address, port, ifindex_oid):

    index_dict = {}
    index_dict[ip_address] = []

    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(ifindex_oid)),
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
            for response in varBinds:
                index_dict[ip_address].append(response[1])

    return index_dict

    
def snmp_walk(community, ip_address, port, oid):

    result_dic = {}

    # Perform SNMP walk
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
                key = (ip_address, str(varBind[0]))
                result_dic[key] = varBind[1]

                
    return result_dic

def snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid):
    result_dic = {}

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    usm_user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    iterator = nextCmd(
        SnmpEngine(),
        usm_user,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    for response in iterator:
        error_indication, error_status, error_index, var_binds = response

        if error_indication:
            print(f"SNMP query failed: {error_indication}")
            break
        elif error_status:
            print(f"SNMP query failed: {error_status.prettyPrint()}")
            break
        else:
            for var_bind in var_binds:
                #print(var_bind[1])
                key = (ip_address, str(var_bind[0]))
                result_dic[key] = var_bind[1]

    return result_dic

def snmp_walk_v3_get(ip_address, username, auth_protocol, auth_password, oid):
    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    usm_user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               usm_user,
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        print(f"SNMP query failed: {error_indication}")
        return None

    if error_status:
        print(f"SNMP query failed: {error_status.prettyPrint()}")
        return None

    for var_bind in var_binds:
        return var_bind[1]


def snmp_walk_v3_index(ip_address, username, auth_protocol, auth_password, ifindex_oid):
    index_dict = {}
    index_dict[ip_address] = []

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    usm_user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    iterator = nextCmd(
        SnmpEngine(),
        usm_user,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(ifindex_oid)),
        lexicographicMode=False
    )

    for response in iterator:
        error_indication, error_status, error_index, var_binds = response

        if error_indication:
            print(f"SNMP query failed: {error_indication}")
            break
        elif error_status:
            print(f"SNMP query failed: {error_status.prettyPrint()}")
            break
        else:
            for response in var_binds:
                index_dict[ip_address].append(response[1])

    return index_dict

community = 'snmain'
#ip_address = '172.20.1.89'
port = 161

ip_address = '172.20.1.110'
username = 'network'
auth_protocol = 'MD5'
auth_password = r'$nN3tw0rK'

ifindex_oid = '1.3.6.1.2.1.2.2.1.1'
host_name_oid = '1.3.6.1.2.1.1.5.0'

if_oid = {
    'ifIndex' : '1.3.6.1.2.1.2.2.1.1',
    #'oid_cdp_devport' : '1.3.6.1.4.1.9.9.23.1.2.1.1.7',
    'ifDescr' : '1.3.6.1.2.1.2.2.1.2',
    'ifType'  : '1.3.6.1.2.1.2.2.1.3',
    # 'ifMtu' : '1.3.6.1.2.1.2.2.1.4',
    'ifSpeed' : '1.3.6.1.2.1.2.2.1.5',
    'ifPhysAddress' : '1.3.6.1.2.1.2.2.1.6',
    'ifAdminStatus' : '1.3.6.1.2.1.2.2.1.7',
    'ifOperStatus' : '1.3.6.1.2.1.2.2.1.8',
    'ifAlias' : '1.3.6.1.2.1.31.1.1.1.18'
    # 'ifHCInOctets' : '1.3.6.1.2.1.31.1.1.1.6',
    # 'ifHCOutOctets' : '1.3.6.1.2.1.31.1.1.1.10',
    # 'ifHighSpeed' : '1.3.6.1.2.1.31.1.1.1.15'
    }

#host_name = snmp_get(community, ip_address, port, host_name_oid)

host_name = snmp_walk_v3_get(ip_address, username, auth_protocol, auth_password, host_name_oid)

#print(host_name)
interface_data = {}

# for oid_name,oid in if_oid.items():

#     oid_value = snmp_walk(community, ip_address, port, oid)

#     key = (ip_address, oid_name)
#     interface_data[key] = oid_value

# ifIndexResult = snmp_walk_index(community, ip_address, port, ifindex_oid)

for oid_name,oid in if_oid.items():
    
    oid_value = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid)

    key = (ip_address, oid_name)
    interface_data[key] = oid_value

ifIndexResult = snmp_walk_v3_index(ip_address, username, auth_protocol, auth_password, ifindex_oid)



# print(interface_data[(ip_address,'ifIndex')][(ip_address,'1.3.6.1.2.1.2.2.1.1.1')])
# for oid_name,oid in if_oid.items(): 
#     for key,value in interface_data[(ip_address,oid_name)].items():
#         print(key)


jsonString = ''

jsonString = jsonString + '{"' + str(host_name) + '":' 

jsonString = jsonString + '['

if ifIndexResult:

    for ip,ifIndexValues in ifIndexResult.items():      

        for ifIndexVal in ifIndexValues:

            jsonString = jsonString + '{'

            for oid_name,oid in if_oid.items(): 

                #print(ip,oid_name,oid,ifIndexVal)

                ifIndexData = interface_data[(ip_address,oid_name)][(ip_address,str(oid) + '.' + str(ifIndexVal))]

                if(oid_name == "ifPhysAddress"):
                    ifIndexData = convert_mac(ifIndexData)

                jsonString = jsonString + '"' + oid_name + '":"' + str(ifIndexData) + '",'

                

            jsonString = jsonString[:-1]
            jsonString = jsonString + '},'  

jsonString = jsonString[:-1]
jsonString = jsonString + ']'
jsonString = jsonString + '}'



print(jsonString)
