import subprocess
import threading
import re
import time

from subprocess import PIPE

import mysql.connector

while True:

    cnx = mysql.connector.connect(
        host='172.20.10.56',
        user='root',
        password='Server@2016',
        database='netmon'
    )

    ip_address_table = "ip_master";

    ip_results = {}

    def get_packet_drops(ip_address):

        result = subprocess.run(['ping', '-c', '50', ip_address], stdout=PIPE, stderr=PIPE)

        packet_drop_match = re.search(r'(\d+)% packet loss', result.stdout.decode())
        if packet_drop_match:
            ip_results[ip_address] = int(packet_drop_match.group(1))
        else:
            ip_results[ip_address] = "NA"

    cursor = cnx.cursor()
    query = "SELECT ip_address from " + ip_address_table +  " where is_active=1"
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

    for address, packet_loss in ip_results.items():
        update_query = "UPDATE " + ip_address_table +  " SET packet_loss_percentage = %s WHERE ip_address = %s"
        cursor.execute(update_query, (packet_loss, address))
        print(f"IP address {address} is {packet_loss}")

    cnx.commit()
    cursor.close()
    cnx.close()

    time.sleep(60)

    # # Print the IP status results
    # for address, status in ip_results.items():
        
    #     print(f"IP address {address} is {status}")

    # if packet_drops is not None:
    #     print(f'Packet drops for {ip_address}: {packet_drops}%')
    # else:
    #     print(f'Failed to retrieve packet drops for {ip_address}')
