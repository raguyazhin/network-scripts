import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        
    url_table = "url_master";

    url_results = {}

    def check_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return url, "1"
            else:
                return url, "0"
        except requests.exceptions.RequestException as e:
            return url, "0"

    cursor = cnx.cursor()

    query = "SELECT url_link from " + url_table +  " where is_active=1"
    cursor.execute(query)
    urls = [row[0] for row in cursor.fetchall()]

    num_workers = 10
    executor = ThreadPoolExecutor(max_workers=num_workers)

    future_to_url = {executor.submit(check_url, url): url for url in urls}

    # Process the completed tasks as they finish
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            url_results[url] = result  # Update the results dictionary
        except Exception as e:
            url_results[url] = f"Error occurred: {e}"  # Update the results dictionary

    # Update the MySQL table with the results
    update_query = "UPDATE " + url_table +  " SET current_status = %s WHERE url_link = %s"
    update_values = [(result[1], url) for url, result in url_results.items()]
    cursor.executemany(update_query, update_values)
    cnx.commit()

    cursor.close()
    cnx.close()

    time.sleep(10)
