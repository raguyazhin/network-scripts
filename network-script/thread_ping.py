import subprocess
import threading
import time

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

    ip_results = {}

    def ping(address):
        status = subprocess.call(['ping', '-c', '5', address],)
        if status == 0:
            ip_results[address] = "1"
        else:
            ip_results[address] = "0"

    cursor = cnx.cursor()
    query = "SELECT ip_address from " + ip_address_table +  " where is_active=1"
    cursor.execute(query)
    rows = cursor.fetchall()

    threads = []

    for row in rows:
        address = row[0]
        thread = threading.Thread(target=ping, args=(address,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for address, status in ip_results.items():
        if status == "0":
            update_query = "UPDATE " + ip_address_table +  " SET current_status = %s, packet_loss_percentage=100 WHERE ip_address = %s"
        elif status == "1":
            update_query = "UPDATE " + ip_address_table +  " SET current_status = %s WHERE ip_address = %s"

        cursor.execute(update_query, (status, address))
        print(f"IP address {address} is {status}")

    cnx.commit()
    cursor.close()
    cnx.close()

    time.sleep(10)
