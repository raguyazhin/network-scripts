from pynfdump import NFdump

# NetFlow collector configuration
collector_ip = '172.20.10.124'
collector_port = 6667

# Path to the NetFlow data files
data_files_path = '/data/nfsen/profiles-data/live/Kolkata/2023/06/24/nfcapd.202306240410'

# Create an instance of NFdump
nfdump = NFdump()

# Set the NetFlow filter
filter_expression = f'ip {collector_ip} and port {collector_port}'
nfdump.set_filter(filter_expression)

# Process the NetFlow data files
nfdump.process_files(data_files_path)

# Iterate over the flow records
for flow in nfdump:
    print(flow)

# Close the NFdump instance
nfdump.close()
