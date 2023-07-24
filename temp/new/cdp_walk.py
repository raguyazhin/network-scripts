from pysnmp.hlapi import *
import binascii

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def snmp_get(community, ipAddress, port, oid):
    
    error_indication, error_status, error_index, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ipAddress, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        print(f'SNMP query failed: {error_indication}')
        return None

    if error_status:
        print(f'SNMP query failed: {error_status.prettyPrint()}')
        return None

    for varBind in varBinds:
        return varBind[1]
    
def snmp_walk(community, ipAddress, port, oid):

    result_dic = {}

    # Perform SNMP walk
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ipAddress, port)),
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
                result_dic[str(varBind[0])] = varBind[1]

                
    return result_dic

community = 'snmain'
ipAddress = '172.20.1.89'
port = 161

ifIndexOid = '1.3.6.1.2.1.2.2.1.1'

hostNameOid = '1.3.6.1.2.1.1.5.0'

cdpOid = {
    'cdpCacheDeviceId' : '1.3.6.1.4.1.9.9.23.1.2.1.1.3',
    'cdpCacheDevicePort' : '1.3.6.1.4.1.9.9.23.1.2.1.1.4',
    'cdpCachePlatform' : '1.3.6.1.4.1.9.9.23.1.2.1.1.6',
    'cdpCacheCapabilities' : '1.3.6.1.4.1.9.9.23.1.2.1.1.7',
    'cdpCacheVersion' : '1.3.6.1.4.1.9.9.23.1.2.1.1.8',
}

cdpData = {}

for oidName,oid in cdpOid.items():
    
    oid_value = snmp_walk(community, ipAddress, port, oid)

    key = (ipAddress, oidName)
    cdpData[key] = oid_value

ifIndexResult = snmp_walk(community, ipAddress, port, ifIndexOid)
hostName = snmp_get(community, ipAddress, port, hostNameOid)

cdp_dict_list = []

for oidName,oid in cdpOid.items():

    cdp_dict_list.append(cdpData[(ipAddress, oidName)])


max_positions = max(len(d) for d in cdp_dict_list)

positions_str = ""

for position in range(max_positions):
    positions_str += "{"
    for dictionary in cdp_dict_list:
        if position < len(dictionary):
            value = list(dictionary.values())[position]
            positions_str += "|" + str(value)

    positions_str += "},"

print("Positions String:", positions_str)