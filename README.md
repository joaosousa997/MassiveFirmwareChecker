﻿# MassiveFirmwareChecker

Short in time i made this script to help out collect a huge ammount of firmwares from a list of IPs.
I had to change stuff for the sake of privacy but the script works pretty much the same:

It uses Netmiko for the network operations and ThreadPoolExecutor for the handling of multiple routers, 

1 - Open the TXT name ip_list.txt and fill with all the IPs you want to use

2 - run the ios_checker.py (Was originally made only for cisco routers)

3 - Answear the questions

4 - Wait for it to finish and keep an eye on the logs.
