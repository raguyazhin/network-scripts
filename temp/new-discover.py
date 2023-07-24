from pysnmp.hlapi import *

def snmp_walk(ip, community, oids):
    result = {}  # Dictionary to store the results for a device
    for oid in oids:
         for error_indication, error_status, error_index, var_binds in \
                bulkCmd(SnmpEngine(),
                        CommunityData(community),
                        UdpTransportTarget((ip, 161)),
                        ContextData(),
                        0, 10,
                        ObjectType(ObjectIdentity(*oid)),
                        lexicographicMode=False):

            if error_indication:
                print(f"Error: {error_indication}")
            elif error_status:
                print(f"Error: {error_status.prettyPrint()}")
            else:
                for var_bind in var_binds:                    
                    index = var_bind[0][-1]
                    value = var_bind[1]
                    key = str(oid[1]) + str(index)
                    result[key] = key + '-value'  # Store the OID and its value in the dictionary
    #print(result)
    return result

# Example usage
discovered_devices = [
    {'ip': '172.20.9.250', 'community': 'snmain'},
    {'ip': '172.20.9.251', 'community': 'snmain'},
    # Add more devices as needed
]

oids = [
    ('IF-MIB', 'ifIndex'),
    ('IF-MIB', 'ifDescr'),
    ('IF-MIB', 'ifType'),
    ('IF-MIB', 'ifMtu'),
    ('IF-MIB', 'ifSpeed'),
    ('IF-MIB', 'ifPhysAddress'),
    ('IF-MIB', 'ifAdminStatus'),
    ('IF-MIB', 'ifOperStatus'),
    ('IF-MIB', 'ifHCInOctets'),
    ('IF-MIB', 'ifHCOutOctets'),
    ('IF-MIB', 'ifHighSpeed')
]

results = []  # List to store overall results

for device in discovered_devices:
    ip = device['ip']
    community = device['community']
    result = snmp_walk(ip, community, oids)  # Perform SNMP walk for the device
    results.append({'device': device, 'interfaces': result})  # Store the result for the device


    # Print the results
for data in results:
    device = data['device']
    interfaces = data['interfaces']
    
    #print(interfaces)
    print(f"Device: {device['ip']}")

    #print(interfaces.keys())

    #print(interfaces['ifAdminStatus24'])
    print(interfaces.items());
    for oid, value in interfaces.items():
        print(f"{oid}: {value}")
    print()

desired_key = 'ifHighSpeed19'
desired_value = [value for key, value in interfaces.items() if key == desired_key]
print(desired_value)  # Output: ['ifHighSpeed28-value']







