from pysnmp.hlapi import *
import binascii
import json

import mysql.connector
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

community = 'snmain'
port = 161

username = 'network'
auth_protocol = 'MD5'
auth_password = r'$nN3tw0rK'

ipAddress = '172.20.1.89'

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def snmp_get(community, ip_address, port, oid, username, auth_protocol, auth_password):
    
   
    target_v2 = SnmpEngine()
    community = CommunityData(community, mpModel=1) 
    transport_v2 = UdpTransportTarget((ip_address, port)) 

    target_v3 = SnmpEngine()

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    transport_v3 = UdpTransportTarget((ip_address, port))  

    v_oid = ObjectType(ObjectIdentity(oid))

    iterator_v2 = getCmd(target_v2, community, transport_v2, ContextData(), v_oid, lexicographicMode=False)

    for errorIndication_v2, errorStatus_v2, errorIndex_v2, varBinds_v2 in iterator_v2:

        if errorIndication_v2:

            print(f"SNMPv2 Error: {errorIndication_v2}")
            print("Switching to SNMPv3...")
            
            iterator_v3 = getCmd(target_v3, user, transport_v3, ContextData(), v_oid, lexicographicMode=False)

            for errorIndication_v3, errorStatus_v3, errorIndex_v3, varBinds_v3 in iterator_v3:

                if errorIndication_v3:
                    print(f"SNMPv3 Error: {errorIndication_v3}")
                    return []
                
                elif errorStatus_v3:
                    print(f"SNMPv3 Error: {errorStatus_v3.prettyPrint()} at {errorIndex_v3 and varBinds_v3[int(errorIndex_v3) - 1][0] or '?'}")
                    return []
                
                else:
                    for varBind in varBinds_v3:
                        return varBind[1]
        
        elif errorStatus_v2:
            print(f"SNMPv2 Error: {errorStatus_v2.prettyPrint()} at {errorIndex_v2 and varBinds_v2[int(errorIndex_v2) - 1][0] or '?'}")
            return []
        
        else:
            for varBind in varBinds_v2:
                return varBind[1]

def snmp_walk(community, ip_address, port, oid, username, auth_protocol, auth_password):
    
    result_dic = {}

    target_v2 = SnmpEngine()
    community = CommunityData(community, mpModel=1)  # Use the appropriate community string
    transport_v2 = UdpTransportTarget((ip_address, port))  # Replace with the IP address of your SNMP-enabled device

    # SNMPv3 parameters
    target_v3 = SnmpEngine()

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    transport_v3 = UdpTransportTarget((ip_address, port))  

    v_oid = ObjectType(ObjectIdentity(oid))

    iterator_v2 = nextCmd(target_v2, community, transport_v2, ContextData(), v_oid, lexicographicMode=False)

    for errorIndication_v2, errorStatus_v2, errorIndex_v2, varBinds_v2 in iterator_v2:

        if errorIndication_v2:

            #print(f"SNMPv2 Error: {errorIndication_v2}")
            #print("Switching to SNMPv3...")
            
            iterator_v3 = nextCmd(target_v3, user, transport_v3, ContextData(), v_oid, lexicographicMode=False)

            # Process the SNMPv3 walk response
            for errorIndication_v3, errorStatus_v3, errorIndex_v3, varBinds_v3 in iterator_v3:

                if errorIndication_v3:
                    print(f"SNMPv3 Error: {errorIndication_v3}")
                    return []
                
                elif errorStatus_v3:
                    print(f"SNMPv3 Error: {errorStatus_v3.prettyPrint()} at {errorIndex_v3 and varBinds_v3[int(errorIndex_v3) - 1][0] or '?'}")
                    return []
                
                else:
                    for varBind in varBinds_v3:
                        result_dic[str(varBind[0])] = varBind[1]
        
        elif errorStatus_v2:
            print(f"SNMPv2 Error: {errorStatus_v2.prettyPrint()} at {errorIndex_v2 and varBinds_v2[int(errorIndex_v2) - 1][0] or '?'}")
            return []
        
        else:
            for varBind in varBinds_v2:
                result_dic[str(varBind[0])] = varBind[1]

    return result_dic

def get_interface_if_data(ip_address):

    hostNameOid = '1.3.6.1.2.1.1.5.0'

    ifOid = {  
        'ifIndex' : '1.3.6.1.2.1.2.2.1.1', 
        'ifDescr' : '1.3.6.1.2.1.2.2.1.2',
        'ifType'  : '1.3.6.1.2.1.2.2.1.3',
        'ifMtu' : '1.3.6.1.2.1.2.2.1.4',
        'ifSpeed' : '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress' : '1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus' : '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus' : '1.3.6.1.2.1.2.2.1.8',
        'ifAlias' : '1.3.6.1.2.1.31.1.1.1.18'
    }

    ifindexData = {}

    for oidName,oid in ifOid.items():

        oid_value = snmp_walk(community, ip_address, port, oid, username, auth_protocol, auth_password)

        key = (ip_address, oidName)
        ifindexData[key] = oid_value

    ifIndexResult = snmp_walk(community, ip_address, port, ifOid['ifIndex'], username, auth_protocol, auth_password)
    hostName = snmp_get(community, ip_address, port, hostNameOid, username, auth_protocol, auth_password)

    jsonString = ''

    jsonString = jsonString + '{"' + str(hostName) + '":' 

    jsonString = jsonString + '['

    if ifIndexResult:

        for ifIndexKey,ifIndexValue in ifIndexResult.items():  
            
            jsonString = jsonString + '{'

            for oidName,oid in ifOid.items(): 

                findKey = str(oid) + '.' + str(ifIndexValue)

                if findKey in ifindexData[(ip_address,oidName)]:
                    ifIndexValData = ifindexData[(ip_address,oidName)][findKey]
                else:                 
                    ifIndexValData = ""

                if oidName == "ifPhysAddress" and ifIndexValData != "":
                    ifIndexValData = convert_mac(ifIndexValData)

                ifIndexValData = json.dumps(str(ifIndexValData))

                jsonString = jsonString + '"' + oidName + '":' + ifIndexValData + ','

            jsonString = jsonString[:-1]
            jsonString = jsonString + '},'  

    jsonString = jsonString[:-1]
    jsonString = jsonString + ']'
    jsonString = jsonString + '}'
   
    return jsonString  

cnx = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )

ip_address_table = "ip_master";

ip_results = {}

cursor = cnx.cursor()
query = "SELECT ip_address from " + ip_address_table +  " where ip_type_id=3 and ip_service_provider_id=6 and is_active=1"
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    print(row[0])

    print(get_interface_if_data(row[0]))