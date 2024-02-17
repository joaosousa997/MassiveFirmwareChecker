from concurrent.futures import ThreadPoolExecutor
import netmiko
import sys
import pandas as pd
from netmiko import ConnectHandler, redispatch

file_location = r"ip_list.csv"


ip_list = []

user = input('> Input the username for the proxy server: ')
pw = input('> Input the password for the proxy server: ')
proxyServerIp = input('> Input the IP of the proxy server: ')
while True:
    routerBrand = input('Is the router Cisco (1) or Huawei (2)? Please write the correct number: ')
    if routerBrand in '1':
        routerBrand = 'cisco_ios'
        check_ios_command = "show ver"
        break
    elif routerBrand in '2':
        routerBrand = 'huawei'
        check_ios_command = "dis ver"
        break
    else:
        print("Invalid input. Please enter '1' for Cisco or '2' for Huawei.")
routerUser = input('> Input the username for the Router: ')
# Only works if VTY is currently defined to elevate user, 
# else you need to configure that first or will ask for enable password
routerPw = input('> Input the password for the Router: ')
ios_version = input('What firmware version should be on the router?')


for a in file_location:
    try:
        ip_list.append(a)
    except:
        print(f"Error adding {a} to the list.\n")    
    
def start_con():
    # Starting base connection to terminal aka DSE Server, in case of fail then shut down.
    try:
        conn_dic = {
            'ip': proxyServerIp,
            'username': user,
            'password': pw,
            'device_type': 'terminal_server',
            'session_log': 'LOG.txt',
            #'fast_cli': False,
        }
        conn = ConnectHandler(**conn_dic)
        return conn
    except:
        print("Error connecting to Proxy Server!")
        input("Press any key to exit.")
        sys.exit(0)


def ssh_toCpe(conn, ip):
    # Connection to Router, if doesn't find prompt then return False
    conn.send_command(f'ssh -o StrictHostKeyChecking=no {routerUser}@{ip}', expect_string='assword:')
    conn.write_channel(f"{routerPw}\n")
    redispatch(conn, device_type=routerBrand)
    check_cpe = conn.find_prompt()
    # Switch this for your hostname convention, mainly used to validate if it 100% is inside the router
    if 'CPE' in check_cpe:
        return True
    else:
        return False
    
def ping_cpe(conn, ip):
    # Checks ping to router, sends 2 packets, after checks if it was received
    ping = conn.send_command(f"ping -c 2 {ip}", expect_string="$")
    if "2 received" in ping:
        return True
    else:
        return False
    
def check_firmware(conn):
    current_ios = conn.send_command(f'{check_ios_command}\n')
    if ios_version not in current_ios:
        return False
    return True

def main(ip):

    conn = start_con()
    ping_check = ping_cpe(conn, ip)
    if ping_check is False:
        print(f"Ping router -> {ip} NOK!")
        return "Ping NOK"
    
    check_ssh = ssh_toCpe(conn, ip)
    if check_ssh is False:
        print(f"SSH NOK -> {ip}")
        return "SSH NOK"
    
    ios_valid = check_firmware(conn)
    
def worker(ip):
    return ip, main(ip)

# Create a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    # Use the executor to map the worker function to the IPs
    results = list(executor.map(worker, ip_list))

# Separate the results into two lists
ips_after, results = zip(*results)

# Create a DataFrame
df = pd.DataFrame({'IP': ip_list, 'Result': results})

# Write the DataFrame to an Excel file
df.to_excel('output.xlsx', index=False)