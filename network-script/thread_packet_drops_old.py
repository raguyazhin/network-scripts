import subprocess
import threading
import re
import time

from subprocess import PIPE

import mysql.connector

#while True:

cnx = mysql.connector.connect(
    host='172.20.10.56',
    user='root',
    password='Server@2016',
    database='netmon'
)

ip_address_table = "ip_master";

ping_results = {}

ping_count = 50

def get_packet_drops(ip_address):

    ping_command = ['ping', '-c', str(ping_count), ip_address]
    ping_output = subprocess.run(ping_command, stdout=PIPE, stderr=PIPE)

    packet_loss_match = re.search(r'(\d+)% packet loss', ping_output.stdout.decode())
    min_ping_match = re.search(r'min/avg/max/(?:stddev|mdev) = ([\d.]+)/([\d.]+)/([\d.]+)/', ping_output.stdout.decode())

    if packet_loss_match and min_ping_match:
        packet_loss = int(packet_loss_match.group(1))
        min_ping = round(float(min_ping_match.group(1)), 2)
        avg_ping = round(float(min_ping_match.group(2)), 2)
        max_ping = round(float(min_ping_match.group(3)), 2)

        ping_results[ip_address] = {
            'packet_loss': packet_loss,
            'min_ping': min_ping,
            'avg_ping': avg_ping,
            'max_ping': max_ping
        }

    else:

        ping_results[ip_address] = {
            'packet_loss': "100",
            'min_ping': "NA",
            'avg_ping': "NA",
            'max_ping': "NA"
        }

cursor = cnx.cursor()
query = "SELECT ip_address from " + ip_address_table +  " where is_active=1 and ip_address='103.60.139.2'"
cursor.execute(query)
rows = cursor.fetchall()

threads = []

for row in rows:
    address = row[0]
    thread = threading.Thread(target=get_packet_drops, args=(address,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

for ip_address, result in ping_results.items():
    packet_loss = result['packet_loss']
    min_ping = result['min_ping']
    avg_ping = result['avg_ping']
    max_ping = result['max_ping']

    update_query = "UPDATE " + ip_address_table +  " SET packet_loss_percentage = %s, ping_min = %s, ping_avg = %s, ping_max = %s WHERE ip_address = %s"
    cursor.execute(update_query, (packet_loss, min_ping, avg_ping, max_ping, ip_address))

    print(f'IP Address: {ip_address}')
    print(f'Packet Loss: {packet_loss}%')
    print(f'Min Ping: {min_ping} ms')
    print(f'Avg Ping: {avg_ping} ms')
    print(f'Max Ping: {max_ping} ms')
    print()

cnx.commit()
cursor.close()
cnx.close()

    #time.sleep(60)

    # # Print the IP status results
    # for address, status in ip_results.items():
        
    #     print(f"IP address {address} is {status}")

    # if packet_drops is not None:
    #     print(f'Packet drops for {ip_address}: {packet_drops}%')
    # else:
    #     print(f'Failed to retrieve packet drops for {ip_address}')
