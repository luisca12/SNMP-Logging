from netmiko import ConnectHandler
from log import authLog

import traceback
import re
import os

interface = ''

shHostname = "show run | i hostname"

shVlanIDs = [
    "do show vlan id 1101",
    "do show vlan id 1103",
    "do show vlan id 1105",
    "do show vlan id 1107",
    "do show vlan id 1193",
    "do show vlan id 1194"
]

snmpLoggingConf = [
    f'int {interface}',
    'snmp trap link-status',
    'logging event link-status'
]

allInterfacesList = []

# Regex Patterns
intPatt = r'[a-zA-Z]+\d+\/(?:\d+\/)*\d+'

def snmpLoggingConfig(validIPs, username, netDevice):
    # This function is to take a show run

    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                try:
                    sshAccess.enable()
                    shHostnameOut = sshAccess.send_command(shHostname)
                    authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                    shHostnameOut = shHostnameOut.replace('hostname', '')
                    shHostnameOut = shHostnameOut.strip()
                    shHostnameOut = shHostnameOut + "#"

                    shVlanIDsStr = " ".join(shVlanIDs)
                    shVlanIDsStr.split('\n')

                    print(f"INFO: Taking the following commands for device: {validDeviceIP}\n{shVlanIDsStr}")
                    shVlanIDsOut = sshAccess.send_config_set(shVlanIDs)
                    authLog.info(f"Automation successfully ran the commands for device {validDeviceIP}:\n{shVlanIDsStr}\n{shVlanIDsOut}")

                    shVlanIDsOut1 = re.findall(intPatt, shVlanIDsOut)
                    authLog.info(f"The following interfaces were found under the command for device {validDeviceIP}:\n{shVlanIDsStr}\n{shVlanIDsOut1}")

                    if shVlanIDsOut1:
                        
                        for interface in shVlanIDsOut1:
                            interface = interface.strip()
                            snmpLoggingConf[0] = f'int {interface}'

                            snmpLoggingConfStr = " ".join(snmpLoggingConf)
                            snmpLoggingConfStr.split('\n')

                            print(f"INFO: Modifying the interface {interface} on device {validDeviceIP} with the following config:\n{snmpLoggingConfStr}")
                            authLog.info(f"Modifying the interface {interface} on device {validDeviceIP} with the following config:\n{snmpLoggingConfStr}")

                            snmpLoggingConfOut = sshAccess.send_command(snmpLoggingConf)

                            authLog.info(f"Interface {interface} on device {validDeviceIP} was successfully configured:\n{snmpLoggingConfOut}")
                            print(f"INFO: Sucessfully configured interface {interface} on device {validDeviceIP}")
                            
                            allInterfacesList.append(snmpLoggingConfOut)

                    else:
                        print(f"INFO: No interfaces found under: {shVlanIDs}")
                        authLog.info(f"No interfaces found under: {shVlanIDs}")
                    
                    allInterfacesStr = " ".join(allInterfacesList)
                    allInterfacesStr.split('\n')

                    writeMemOut = sshAccess.send_command('write')
                    print(f"INFO: Running configuration saved for device {validDeviceIP}")
                    authLog.info(f"Running configuration saved for device {validDeviceIP}\n{shHostnameOut}'write'\n{writeMemOut}")

                    with open(f"Outputs/{validDeviceIP}_SNMP&Logging.txt", "a") as file:
                        file.write(f"User {username} connected to device IP {validDeviceIP}\n\n")
                        file.write(f"Below is the config applied to the interfaces under VLANs: 1101, 1103, 1105, 1107, 1193, 1194\n{allInterfacesStr}")
                        authLog.info(f"File {validDeviceIP}_SNMP&Logging.txt was created successfully.")

                except Exception as error:
                    print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                    authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
                    authLog.error(traceback.format_exc(),"\n")
                    os.system("PAUSE")
       
        except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.error(traceback.format_exc(),"\n")
            with open(f"failedDevices.txt","a") as failedDevices:
                failedDevices.write(f"User {username} connected to {validDeviceIP} got an error.\n")
        
        finally:
            print(f"Outputs and files successfully created for device {validDeviceIP}.\n")
            print("For any erros or logs please check Logs -> authLog.txt\n")