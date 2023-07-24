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

community = 'snmain'
ip_address = '172.20.1.89'
port = 161

ifindex_oid = '1.3.6.1.2.1.2.2.1.1'
host_name_oid = '1.3.6.1.2.1.1.5.0'

if_oid = {
    'ifIndex' : '1.3.6.1.2.1.2.2.1.1', 
    'ifDescr' : '1.3.6.1.2.1.2.2.1.2',
    'ifType'  : '1.3.6.1.2.1.2.2.1.3',
    'ifMtu' : '1.3.6.1.2.1.2.2.1.4',
    'ifSpeed' : '1.3.6.1.2.1.2.2.1.5',
    'ifPhysAddress' : '1.3.6.1.2.1.2.2.1.6',
    'ifAdminStatus' : '1.3.6.1.2.1.2.2.1.7',
    'ifOperStatus' : '1.3.6.1.2.1.2.2.1.8',
    'ifAlias' : '1.3.6.1.2.1.31.1.1.1.18'
    # 'ifHCInOctets' : '1.3.6.1.2.1.31.1.1.1.6',
    # 'ifHCOutOctets' : '1.3.6.1.2.1.31.1.1.1.10',
    # 'ifHighSpeed' : '1.3.6.1.2.1.31.1.1.1.15'
    }

host_name = snmp_get(community, ip_address, port, host_name_oid)
#print(host_name)
interface_data = {}

for oid_name,oid in if_oid.items():

    oid_value = snmp_walk(community, ip_address, port, oid)

    key = (ip_address, oid_name)
    interface_data[key] = oid_value

    
# print(interface_data[(ip_address,'ifIndex')][(ip_address,'1.3.6.1.2.1.2.2.1.1.1')])
# for oid_name,oid in if_oid.items(): 
#     for key,value in interface_data[(ip_address,oid_name)].items():
#         print(key)

ifIndexResult = snmp_walk_index(community, ip_address, port, ifindex_oid)

jsonString = ''

jsonString = jsonString + '{"' + str(host_name) + '":' 

jsonString = jsonString + '['

if ifIndexResult:

    for ip,ifIndexValues in ifIndexResult.items():      

        for ifIndexVal in ifIndexValues:

            jsonString = jsonString + '{'

            for oid_name,oid in if_oid.items(): 

                ifIndexData = interface_data[(ip_address,oid_name)][(ip_address,str(oid) + '.' + str(ifIndexVal))]

                if(oid_name == "ifPhysAddress"):
                    ifIndexData = convert_mac(ifIndexData)

                jsonString = jsonString + '"' + oid_name + '":"' + str(ifIndexData) + '",'

                #print(ip,oid_name,oid,ifIndexVal,ifIndexData)

            jsonString = jsonString[:-1]
            jsonString = jsonString + '},'  

jsonString = jsonString[:-1]
jsonString = jsonString + ']'
jsonString = jsonString + '}'


print(jsonString)
