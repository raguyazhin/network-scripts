import subprocess
import threading
import re
import time

from subprocess import PIPE
from datetime import date, datetime

import mysql.connector
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

while True:

    cnx = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )

    ip_address_table = "ip_master";

    ping_results = {}

    ping_count = 50

    def get_packet_drops(ip_address):

        ping_command = ['ping', '-c', str(ping_count), ip_address]
        ping_output = subprocess.run(ping_command, stdout=PIPE, stderr=PIPE)

        packets_transmitted_match = re.search(r'(\d+) packets transmitted', ping_output.stdout.decode())
        packets_received_match = re.search(r'(\d+) received', ping_output.stdout.decode())
        packet_loss_match = re.search(r'(\d+)% packet loss', ping_output.stdout.decode())

        min_ping_match = re.search(r'min/avg/max/(?:stddev|mdev) = ([\d.]+)/([\d.]+)/([\d.]+)/', ping_output.stdout.decode())

        if packet_loss_match and min_ping_match:
            packets_transmitted = int(packets_transmitted_match.group(1))
            packets_received = int(packets_received_match.group(1))
            packet_loss = int(packet_loss_match.group(1))
            min_ping = round(float(min_ping_match.group(1)), 2)
            avg_ping = round(float(min_ping_match.group(2)), 2)
            max_ping = round(float(min_ping_match.group(3)), 2)

            ping_results[ip_address] = {
                'packets_transmitted': packets_transmitted,
                'packets_received': packets_received,
                'packet_loss': packet_loss,
                'min_ping': min_ping,
                'avg_ping': avg_ping,
                'max_ping': max_ping
            }

        else:

            ping_results[ip_address] = {
                'packet_loss': "100",
                'packets_transmitted': "NA",
                'packets_received': "NA",
                'min_ping': "NA",
                'avg_ping': "NA",
                'max_ping': "NA"
            }

    cursor = cnx.cursor()
    query = "SELECT ip_address from " + ip_address_table +  " where is_active='1' and current_status='1'"
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
        packets_transmitted = result['packets_transmitted']
        packets_received = result['packets_received']
        packet_loss = result['packet_loss']
        min_ping = result['min_ping']
        avg_ping = result['avg_ping']
        max_ping = result['max_ping']

        update_query = "UPDATE " + ip_address_table +  " SET packet_loss_percentage = %s, ping_min = %s, ping_avg = %s, ping_max = %s WHERE ip_address = %s"
        cursor.execute(update_query, (packet_loss, min_ping, avg_ping, max_ping, ip_address))

        current_date = date.today()
        current_datetime = datetime.now()

        if int(packet_loss) > 0:
            insert_query = "insert into ip_packet_loss_log(date_on, ip_address, packets_transmitted, packets_received, packet_loss_percentage, packet_loss_date_time) value (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (current_date, ip_address, packets_transmitted, packets_received, packet_loss, current_datetime))

        print(f'IP Address: {ip_address}')
        print(f'Packets_transmitted: {packets_transmitted}')
        print(f'Packets Received: {packets_received}')
        print(f'Packet Loss: {packet_loss}%')
        print(f'Min Ping: {min_ping} ms')
        print(f'Avg Ping: {avg_ping} ms')
        print(f'Max Ping: {max_ping} ms')
        print()

    cnx.commit()
    cursor.close()
    cnx.close()

    time.sleep(60)
