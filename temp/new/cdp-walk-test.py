from pysnmp.hlapi import *

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


def get_cdp_details(ip_address, community):
    oid_cdp_ipaddr = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
    #oid_cdp_ios = '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
    oid_cdp_devid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
    oid_cdp_devport = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
    oid_cdp_devplat = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'

    cdp_details = {}

    ip_addresses = snmp_walk(community, ip_address, 161, oid_cdp_ipaddr)
    #ios_versions = snmp_walk(community, ip_address, 161, oid_cdp_ios)
    device_ids = snmp_walk(community, ip_address, 161, oid_cdp_devid)
    device_ports = snmp_walk(community, ip_address, 161, oid_cdp_devport)
    device_platforms = snmp_walk(community, ip_address, 161, oid_cdp_devplat)


    cdp_name_list = ["IP address","Device ID", "Interface", "Platform"]
    print(cdp_name_list[0])

    cdp_dict_list = [ip_addresses, device_ids, device_ports, device_platforms]

    #cdp_dict_list.append(ip_addresses, device_ids, device_ports, device_platforms )


    max_positions = max(len(d) for d in cdp_dict_list)

    jsonString = ""

    for position in range(max_positions):

        jsonString += "{"

        count = 0
        for dictionary in cdp_dict_list:
            
            if position < len(dictionary):

                value = list(dictionary.values())[position]

                jsonString += '"' + cdp_name_list[count] + '":' + '"' + str(value) + '",'

                count += 1


        jsonString = jsonString[:-1]
        jsonString += "},"
        
    jsonString = jsonString[:-1]
    print(jsonString)

    # num_entries = len(ip_addresses)

    # print(ip_addresses)

    # if (
    #     num_entries == len(device_ids)
    #     == len(device_ports)
    #     == len(device_platforms)
    # ):
    #     for i in range(num_entries):
    #         cdp_entry = {
    #             'Entry address(es)': {
    #                 'IP address': str(ip_addresses[i])
    #             },
    #             #'Version': str(ios_versions[i]),
    #             'Device ID': str(device_ids[i]),
    #             'Interface': str(device_ports[i]),
    #             'Platform': str(device_platforms[i])
    #         }
    #         cdp_details[i] = cdp_entry

    # return cdp_details


# Example usage
community = 'snmain'
ip_address = '172.20.1.89'

cdp_details = get_cdp_details(ip_address, community)
print(cdp_details)
