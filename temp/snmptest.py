from pysnmp.hlapi import *
import concurrent.futures

def snmp_get(device):
    ip = device['ip']
    community = device['community']

    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('.1.3.6.1.2.1.2.1.0')))
    )

    if error_indication:
        print(f"Error: {error_indication}")
    elif error_status:
        print(f"Error: {error_status.prettyPrint()}")
    else:
        for var_bind in var_binds:
            num_indexes = var_bind[1]
            print(f"Device: {ip}, Number of Indexes: {num_indexes}")
            snmp_walk(device, num_indexes)


# Define the IP range and SNMP community
ip_range = ['172.20.8.131']  # Replace with your IP range
community = 'snmain'
oids = ['.1.3.6.1.2.1.2.2.1.1', '.1.3.6.1.2.1.2.2.1.2', '.1.3.6.1.2.1.2.2.1.7', '.1.3.6.1.2.1.2.2.1.8', '.1.3.6.1.2.1.31.1.1.1.1', '.1.3.6.1.2.1.31.1.1.1.18',
        '.1.3.6.1.2.1.2.2.1.3', '.1.3.6.1.2.1.2.2.1.5', '.1.3.6.1.2.1.2.2.1.6', '.1.3.6.1.2.1.4.20.1.2']  # Interface Admin Status

interfaces_table_oid = [
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

for oid in oids:
    print(oid)

# Create a list of device dictionaries
devices = [{'ip': ip, 'community': community} for ip in ip_range]


def snmp_walk(device, num_indexes):
    ip = device['ip']
    community = device['community']

    for oid in interfaces_table_oid:
    #for interface_index in range(1, num_indexes + 1):
        iterator = nextCmd(SnmpEngine(),
                            CommunityData(community),
                            UdpTransportTarget((ip, 161)),
                            ContextData(),
                                ObjectType(ObjectIdentity(*oid)))
                            # *[ObjectType(ObjectIdentity(oid)) for oid in oids],
                            # ObjectType(ObjectIdentity('.1.3.6.1.2.1.2.2.1.2')),
                            #  *[ObjectType(ObjectIdentity(oid)) for oid in oids])

                            # lexicographicMode=False,
                            # maxRows=num_indexes)

        for error_indication, error_status, error_index, var_binds in iterator:
            if error_indication:
                print(f"Error: {error_indication}")
            elif error_status:
                print(f"Error: {error_status.prettyPrint()}")
            else:
                #print(var_binds[0]);
                for var_bind in var_binds:
                    # print(var_bind)
                    # print(type(var_bind))
                    interface_index = var_bind[0][-1]  # Get the last element of the OID
                    interface_description = var_bind[1]
                    print(f"Device: {ip}, Interface {interface_index}: Description={interface_description}")

#
# 
for device in devices:
    snmp_get(device)


# data="SNMPv2-SMI::mib-2.2.2.1.2.10501 = Null0"

# print(data[0])