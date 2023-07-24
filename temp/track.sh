#!/bin/bash

# SNMP Community String
community="snmain"

# IP Address of the Switch
switch_ip="172.20.9.250"

# OID for Bridge Port IfIndex
bridge_port_ifindex_oid="1.3.6.1.2.1.17.1.4.1.2"

# OID for Bridge Port MAC Address
bridge_port_mac_oid="1.3.6.1.2.1.17.1.4.1.1"

# OID for VLAN Egress Ports
vlan_egress_ports_oid="1.3.6.1.2.1.17.7.1.4.3.1.2"

# OID for MAC Addresses
mac_address_oid="1.3.6.1.2.1.17.4.3.1.1"

# OID for MAC Address Bridge Port
mac_address_bridge_port_oid="1.3.6.1.2.1.17.4.3.1.2"

# OID for ARP IP Address
arp_ip_address_oid="1.3.6.1.2.1.4.22.1.2"

# Perform SNMP Walk for Bridge Port IfIndex
bridge_port_ifindex=$(snmpwalk -v2c -c "$community" "$switch_ip" "$bridge_port_ifindex_oid" | awk -F' ' '{print $NF}')

# Perform SNMP Walk for Bridge Port MAC Addresses
bridge_port_mac=$(snmpwalk -v2c -c "$community" "$switch_ip" "$bridge_port_mac_oid" | awk -F' ' '{print $NF}')

# Perform SNMP Walk for VLAN Egress Ports
vlan_egress_ports=$(snmpwalk -v2c -c "$community" "$switch_ip" "$vlan_egress_ports_oid" | awk -F' ' '{print $NF}')

# Perform SNMP Walk for MAC Addresses
mac_addresses=$(snmpwalk -v2c -c "$community" "$switch_ip" "$mac_address_oid" | awk -F' ' '{print $NF}')
echo $mac_addresses
# Perform SNMP Walk for MAC Address Bridge Port
mac_address_bridge_port=$(snmpwalk -v2c -c "$community" "$switch_ip" "$mac_address_bridge_port_oid" | awk -F' ' '{print $NF}')

# Perform SNMP Walk for ARP IP Addresses
arp_ip_addresses=$(snmpwalk -v2c -c "$community" "$switch_ip" "$arp_ip_address_oid" | awk -F' ' '{print $NF}')

# Initialize arrays
bridge_port_ifindex_array=()
bridge_port_mac_array=()
vlan_egress_ports_array=()
mac_addresses_array=()
mac_address_bridge_port_array=()
arp_ip_addresses_array=()

# Loop to populate the arrays
while IFS= read -r line; do
    bridge_port_ifindex_array+=("$line")
done <<< "$bridge_port_ifindex"

while IFS= read -r line; do
    bridge_port_mac_array+=("$line")
done <<< "$bridge_port_mac"

while IFS= read -r line; do
    vlan_egress_ports_array+=("$line")
done <<< "$vlan_egress_ports"

while IFS= read -r line; do
    mac_addresses_array+=("$line")
done <<< "$mac_addresses"

while IFS= read -r line; do
    mac_address_bridge_port_array+=("$line")
done <<< "$mac_address_bridge_port"

while IFS= read -r line; do
    arp_ip_addresses_array+=("$line")
done <<< "$arp_ip_addresses"

# Check the length of the arrays (assuming all arrays have the same length)
length=${#bridge_port_ifindex_array[@]}

# Process each entry
for ((i=0; i<length; i++)); do
    index="${bridge_port_ifindex_array[$i]}"
    mac="${bridge_port_mac_array[$i]}"
    vlan_egress_port="${vlan_egress_ports_array[$i]}"
    mac_address="${mac_addresses_array[$i]}"
    mac_address_bridge_port="${mac_address_bridge_port_array[$i]}"

    # Find associated IP address
    ip_address=""
    for entry in "${arp_ip_addresses_array[@]}"; do
        entry_mac_address="${entry% *}"
        entry_ip_address="${entry#* }"
        if [[ "$entry_mac_address" == "$mac_address" ]]; then
            ip_address="$entry_ip_address"
            break
        fi
    done

    echo "Index: $index, MAC: $mac, VLAN Egress Port: $vlan_egress_port, MAC Address: $mac_address, Bridge Port: $mac_address_bridge_port, IP Address: $ip_address"
done
