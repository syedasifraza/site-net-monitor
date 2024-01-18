#!/bin/env python
#
# Example code to query for interface information from network devices,
# add relevant values together and output JSON file match WLCG Mon TF needs
#
#  See https://gitlab.cern.ch/wlcg-doma/site-network-information
#
# Requires easysnmp package (see https://easysnmp.readthedocs.io/en/latest/)
#
#   CentOS example install#   (assuming you have python3)
#   sudo yum install gcc python3-devel net-snmp-devel
#   sudo pip3 install easysnmp
#
from easysnmp import Session
from datetime import datetime, timezone
import time
import json
import os
import logging, sys
import argparse
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--site-config',
                        dest='config_file',
                        default='site-config.json',
                        help='Site snmp config file name. Default config_file.')
# PWD is not set if you start this as a systemd service
arg_parser.add_argument('--install_location',
                        dest='install_loc',
                        default='./',
                        help='Install Location. Default: ./')
arg_parser.add_argument('--debug_level',
                        dest='debug_level',
                        default='WARN',
                        help='Debug level INFO,DEBUG')

args, unknown = arg_parser.parse_known_args()


# Note: interfaces have the ifDescr value holding the right index. This is 
# needed for the INDICES python dictionary below.
#
#    To see what your device provides try:
#       snmpwalk -v2c -c <COMMUNITY> <HOST> IF-MIB::ifDescr
#
#    For the example below, my Cisco provides:
#
#      IF-MIB::ifDescr.436233216 = STRING: Ethernet1/51
#      IF-MIB::ifDescr.436233728 = STRING: Ethernet1/52
#                      ^^^^^^^^^           ^^^^^^^^^^^^
#                      Index               Interface description

# Set up logging and specify level as logging.<LEVEL> with <LEVEL>=DEBUG,INFO,WARN,ERROR...
logging.basicConfig(format='%(asctime)s - %(message)s',stream=sys.stderr, level=args.debug_level)

                        
# ---------------------------------------------------------------------------
# ================= CUSTOMIZE THIS SECTION ==================================
# ---------------------------------------------------------------------------

# Install location (directory that hosts WLCG-site-snmp.py script)
INSTALL_LOC=args.install_loc
MESSAGE="Install Location INSTALL_LOC: "+INSTALL_LOC
logging.info(MESSAGE)

# Define the set of switches and ports that represent the site "border"
#   You will need to find the correct SNMP indices to use.  See info above
site_config=json.load(open(f"{INSTALL_LOC}/{args.config_file}"))

# ------------ Define the needed 64-bit OIDs for In/Out Octets --------------
ifHCInOctets = ".1.3.6.1.2.1.31.1.1.1.6"
ifHCOutOctets = ".1.3.6.1.2.1.31.1.1.1.10"

# ----------- For reference, here are the 32-bit OIDs for In/Out Octets -----
# ----------- If the 64-bit OIDs above don't exist you can try these --------
IfInOctets = ".1.3.6.1.2.1.2.2.1.10"
IfOutOctets = ".1.3.6.1.2.1.2.2.1.16"

InStartTime = {}
InEndTime = {}
ifInCntrStart = {}
ifInCntrEnd = {}

OutStartTime = {}
OutEndTime = {}
ifOutCntrStart = {}
ifOutCntrEnd = {}

CurrentOutput={}

# Sleep interval between loop executions (in seconds) default 60
INTERVAL = site_config['poll_interval']

# Announce service start up
MESSAGE=" WLCG site traffic monitor started at " + datetime.now(timezone.utc).isoformat()
print(MESSAGE)
MESSAGE="  -------  traffic monitor directory " + INSTALL_LOC
print(MESSAGE)

def snmpGetData(INDICES,COMM):

    MESSAGE="INDICES:"+json.dumps(INDICES, indent=4)
    logging.debug(MESSAGE)
    MESSAGE="COMM:"+json.dumps(COMM, indent=4)
    logging.debug(MESSAGE)

    # ------------ Loop over interfaces, gathering data -------------------------
    MonInterfaces = []
    InBytesPerSec = 0
    OutBytesPerSec = 0
    LastTime_us = datetime.utcnow().isoformat()
    global CurrentOutput

    if CurrentOutput and (INTERVAL > (datetime.strptime(LastTime_us,'%Y-%m-%dT%H:%M:%S.%f')-datetime.strptime(CurrentOutput['UpdatedLast'],'%Y-%m-%dT%H:%M:%S.%f')).total_seconds()):
        CurrentOutput['UpdateInterval'] = (datetime.strptime(LastTime_us,'%Y-%m-%dT%H:%M:%S.%f')-datetime.strptime(CurrentOutput['UpdatedLast'],'%Y-%m-%dT%H:%M:%S.%f')).total_seconds()
        logging.debug("CurrentOutput exists and elapsed < INTERVAL --> reuse CurrentOutput")
    else:
        logging.debug("CurrentOutput doesn't exist or elapsed > INTERVAL --> calculate a new value for CurrentOutput")

        # Loop over all devices and interfaces, adding up Octets
        for host, interface in INDICES.items():
            MESSAGE=" host: " + host + " comm: " + COMM[host]
            logging.debug(MESSAGE)
            session = Session(hostname=host, community=COMM[host], version=2)
            # ----------- Gather In/Out Octets and Associated time ----------------------
            for desc in interface:
                MESSAGE=" Interface: " + desc + " index: ", interface[desc]
                logging.debug(MESSAGE)
                KEY = host + "_" + desc
                MonInterfaces.append(KEY)
    # Get end info for IN
                ifInCntrEnd[KEY] = int(session.get((ifHCInOctets, interface[desc])).value)
                InEndTime[KEY] = datetime.now().isoformat()
                MESSAGE=" Key:" + KEY + "In End Counter:" + str(ifInCntrEnd[KEY]) + " End Time:" + InEndTime[KEY]
                logging.debug(MESSAGE)
                if InStartTime.get(KEY) is not None:
                    # ------------------------ Calculate rate and swap variables
                    time_diff = datetime.strptime(InEndTime[KEY],'%Y-%m-%dT%H:%M:%S.%f')-datetime.strptime(InStartTime[KEY],'%Y-%m-%dT%H:%M:%S.%f')
                    Rate = (ifInCntrEnd[KEY] - ifInCntrStart[KEY]) / time_diff.total_seconds()
                    InBytesPerSec = InBytesPerSec + Rate
    # Get new start info for In
                InStartTime[KEY] = InEndTime[KEY]
                ifInCntrStart[KEY] = ifInCntrEnd[KEY]
    # Get end info for Out 
                ifOutCntrEnd[KEY] = int(session.get((ifHCOutOctets, interface[desc])).value)
                OutEndTime[KEY] = datetime.now().isoformat()
                # ------------------------ Calculate rate and swap variables
                if OutStartTime.get(KEY) is not None:
                    time_diff = datetime.strptime(OutEndTime[KEY],'%Y-%m-%dT%H:%M:%S.%f')-datetime.strptime(OutStartTime[KEY],'%Y-%m-%dT%H:%M:%S.%f')
                    Rate = (ifOutCntrEnd[KEY] - ifOutCntrStart[KEY]) / time_diff.total_seconds()
                    OutBytesPerSec = OutBytesPerSec + Rate
    # Get new start info for Out
                OutStartTime[KEY] = OutEndTime[KEY]
                ifOutCntrStart[KEY] = ifOutCntrEnd[KEY]

        if InBytesPerSec != 0 or OutBytesPerSec != 0:
            # Need time in ISO 8601 format for UTC
            output = {
                "Description": f"Network statistics for {site_config['site']}",
                "UpdatedLast": LastTime_us,
                "InBytesPerSec": InBytesPerSec,
                "OutBytesPerSec": OutBytesPerSec,
                "UpdateInterval": str(time_diff.total_seconds()) + " seconds",
                "MonitoredInterfaces": MonInterfaces,
            }
            logging.debug(json.dumps(output))
            CurrentOutput=output
    return CurrentOutput
#----------------------------------
# HTTP server section             
#----------------------------------
class WebRequestHandler(BaseHTTPRequestHandler):
    # ...
        
    def do_GET(self):
        if self.path == '/NetSite.json':
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            snmpOutput = snmpGetData(INDICES=site_config['indices'], COMM=site_config['comm'])
            self.wfile.write(json.dumps(snmpOutput, indent=4).encode('utf-8'))
            self.wfile.write('\n'.encode('utf-8'))
        elif self.path == '/NetInfo':
            # Serve another file
            with open('/root/site-net-monitor/NetInfo/NetInfo.html', 'rb') as file:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('Select the correct path such as NetSite or NetInfo'.encode('utf-8'))


#----------------------------------
# Main server section             
#----------------------------------

if __name__ == "__main__":

     server = HTTPServer(("0.0.0.0",80), WebRequestHandler)

     if site_config['https']['use'] == True:
         server = HTTPServer(("0.0.0.0", site_config['https']['https_port']), WebRequestHandler)
         MESSAGE=f"Using https on port {site_config['https']['https_port']} with x509 key: {site_config['https']['https_key']} and cert: {site_config['https']['https_cert']}"
         logging.debug(MESSAGE)
         server.socket = ssl.wrap_socket (server.socket, 
             keyfile=site_config['https']['https_key'], 
             certfile=site_config['https']['https_cert'],
             server_side=True,
             ssl_version=ssl.PROTOCOL_TLS_SERVER)

     server.serve_forever()

