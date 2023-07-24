import subprocess

def snmp_walk(hostname, community, oid):
    """
    Perform an SNMP walk for the specified OID on the target hostname using the provided community string.

    Args:
        hostname (str): The IP address or hostname of the SNMP agent.
        community (str): The SNMP community string for authentication.
        oid (str): The starting OID for the SNMP walk.

    Returns:
        str: The output of the SNMP walk command.
    """
    command = f"snmpwalk -v 2c -c {community} {hostname} {oid}"
    output = subprocess.check_output(command, shell=True, encoding='utf-8')
    return output

# Example usage
hostname = '172.20.9.250'
community = 'snmain'
oid = '1.3.6.1.2.1.17.4.3.1.1'

output = snmp_walk(hostname, community, oid)
print(output[0])
