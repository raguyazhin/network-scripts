from pysnmp.hlapi import *
import concurrent.futures

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
                    result[(oid, index)] = value  # Store the OID and its value in the dictionary

    return result

# Example usage
discovered_devices = [
    {'ip': '172.20.9.250', 'community': 'snmain'},
    {'ip': '172.20.9.251', 'community': 'snmain'},
    {'ip': '172.20.1.89', 'community': 'snmain'},
    {'ip': '172.20.8.131', 'community': 'snmain'},
    {'ip': '172.20.9.13', 'community': 'snmain'},
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

def process_device(device):
    ip = device['ip']
    community = device['community']
    result = snmp_walk(ip, community, oids)  # Perform SNMP walk for the device
    return {'device': device, 'interfaces': result}  # Return the result for the device

# Use ThreadPoolExecutor for parallel processing
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit SNMP walk tasks for each device
    future_to_device = {executor.submit(process_device, device): device for device in discovered_devices}
    
    # Retrieve the results as they complete
    for future in concurrent.futures.as_completed(future_to_device):
        device = future_to_device[future]
        try:
            result = future.result()
            results.append(result)  # Store the result for the device
        except Exception as e:
            print(f"Error processing device {device['ip']}: {str(e)}")

# Print the results
for data in results:
    device = data['device']
    interfaces = data['interfaces']
    
    print(f"Device: {device['ip']}")
    for oid, value in interfaces.items():
        print(f"{oid}: {value}")
    print()
