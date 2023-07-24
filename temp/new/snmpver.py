from pysnmp.hlapi import *

def snmp_walk(community, ip_address, port, oid, username, auth_password, priv_password):

    results = []

    target_v2 = SNMPEngine()
    community = CommunityData(community, mpModel=1)  # Use the appropriate community string
    transport_v2 = UdpTransportTarget((ip_address, port))  # Replace with the IP address of your SNMP-enabled device

    # SNMPv3 parameters
    target_v3 = SNMPEngine()
    user = UsmUserData(username, auth_password, priv_password,
                    authProtocol=usmHMACSHAAuthProtocol,
                    privProtocol=usmAesCfb128Protocol)  # Replace with your SNMPv3 user details
    transport_v3 = UdpTransportTarget((ip_address, port))  # Replace with the IP address of your SNMP-enabled device

    v_oid = ObjectType(ObjectIdentity(oid))

    iterator_v2 = nextCmd(target_v2, community, transport_v2, ContextData(), v_oid, lexicographicMode=False)

    for errorIndication_v2, errorStatus_v2, errorIndex_v2, varBinds_v2 in iterator_v2:

        if errorIndication_v2:

            print(f"SNMPv2 Error: {errorIndication_v2}")
            print("Switching to SNMPv3...")
            
            # SNMPv3 walk
            iterator_v3 = nextCmd(target_v3, user, transport_v3, ContextData(), v_oid)

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
                        results.append(varBind[1])
        
        elif errorStatus_v2:
            print(f"SNMPv2 Error: {errorStatus_v2.prettyPrint()} at {errorIndex_v2 and varBinds_v2[int(errorIndex_v2) - 1][0] or '?'}")
            return []
        
        else:
            for varBind in varBinds_v2:
                results.append(varBind[1])

    return results
