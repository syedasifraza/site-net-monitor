# WLCG Site Network Monitoring (Container based deployement for USCMS)

# Configuration Steps:

## Step #1:
  Download repository

    $$ cd /root/mount_location/    (You can use your own folder for repository location)
    
    $$ git clone https://github.com/syedasifraza/site-net-monitor.git
    
    $$ cd site-net-monitor

## Step #2:
  Copy your certificate files into "certs" folder and set permissions

    $$ cp <YOUR_HOST_KEY_FILE_LOCATION> /root/mount_location/site-net-monitor/certs/host_key.pem
    
    $$ cp <YOUR_HOST_CERT_FILE_LOCATION> /root/mount_location/site-net-monitor/certs/host_cert.pem
  
    $$ chmod 600 /root/mount_location/site-net-monitor/certs/host_key.pem
  
    $$ chmod 644 /root/mount_location/site-net-monitor/certs/host_cert.pem

**Host_cert:** It is the host pem certificate to use to start https (use a certificate that can be generally recognised, or you can run this on a standard grid machine)

**Host_key:** It is the host pem key to use to start https


## Step #3:
  
  First, we need to identify the correct SNMP indices for the border interfaces we want to monitor. Let suppose, I want to monitor two interfaces of my FNAL's boarder router (IP address: 202.134.11.1), let’s say the border interfaces are Ethernet1/23 and Ethernet1/24.  We can use the following command to identify the correct index to configure in "site-config.json" file:

    $$ snmpwalk -v2c -c test_community 202.134.11.1 IF-MIB::ifDescr

    ...
  
    IF-MIB::ifDescr.436233216 = STRING: Ethernet1/23
    IF-MIB::ifDescr.436233728 = STRING: Ethernet1/24
                    ^^^^^^^^^           ^^^^^^^^^^^^       
                    Index               Interface description


  Edit the site-config.json file and update the required information as per the site (SNMP community, border router/switch interfaces, and https)

    For example: Monitoring FNAL's single router's two interfaces and enabled https to use the certificates:
    
    $$ vim site-config.json 
    
    {
        "site": "FNAL-Net-Monitoring",
        "poll_interval": 60,
        "comm": {
            "202.134.11.1": "test_community"
        },
        "indices": {
             "202.134.11.1": {
                 "Ethernet1/23": "436233216",
                 "Ethernet1/24": "436233728",
             }
        },
        "https": {
            "use": true,
            "https_key": "/root/mount_location/site-net-monitor/certs/host_key.pem",
            "https_cert": "/root/mount_location/site-net-monitor/certs/host_cert.pem",
            "https_port": 443
        }
    }


   Note: Add the identification of interfaces and index number which is important here and also selected the correct path of certs if you use different mount location.
  
## Step #4:
  Change the NetInfo.html (an example) file available inside NetInfo folder and add your site's network configuraiton details and toplogy information. 

    $$ vim /root/mount_location/site-net-monitor/NetInfo/NetInfo.html
  
    OR you can also create your own NetInfo.html and copy into NetInfo folder.
  
    $$ cp <LOCALTION_OF_YOUR_FILE> /root/mount_location/site-net-monitor/NetInfo/NetInfo.html 


## Step #5:
  Now run the docker image using following command:

    $$ docker run --mount type=bind,source=/root/mount_location/site-net-monitor,target=/root/site-net-monitor -itd -p 443:443,8181:80 asifraza/wlcg-net-monitor:latest

  Note:
    You can change the source location if you downloaded repository at different mount location, but target location should be same as in example.
    You can also change the https port if you used different in site-config.json file. Also you need to open the PORT in your firewall. 
  

## Step #6:
  Run the start script inside docker container:

    $$ docker ps -a
    $$ docker exec -it <DOCKER_CONTAINER_ID> bash

  Once you are inside docker container then execute the following commands:

    $$ ./root/site-net-monitor/start.sh

  Verify service is running!

    $$ systemctl status site-traffic-monitor.service

## Step #7:

  Verify the information is accessible in web broswer:

    https://<YOUR_DomainName_OR_IP_ADDRESS>:<PORT#>/NetSite.json
    
    https://<YOUR_DomainName_OR_IP_ADDRESS>:<PORT#>/NetInfo
  


Now you can add these URLs in CRIC databse!


  
