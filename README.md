# Configure the Site's Network Monitoring
## Step #1:
  Download repository

  $$ cd /tmp
  
  $$ git clone https://github.com/syedasifraza/site-net-monitor.git
  
  $$ cd site-net-monitor

## Step #2:
  Copy your certificate files into "certs" folder and set permissions

  $$ cp <YOUR_HOST_KEY_FILE_LOCATION> certs/host_key.pem
  
  $$ cp <YOUR_HOST_CERT_FILE_LOCATION> certs/host_cert.pem

  $$ chmod 600 certs/host_key.pem

  $$ chmod 644 certs/host_cert.pem

## Step #3:
  Edit the site-config.json file and update the required information as per your site (SNMP community, border router/switch interfaces, and https)

  $$ vim site-config.json 
  
    For example: Monitoring FNAL's single router's two interfaces and enabled https to use the certificates:
    
    {
        "site": "FNAL-RCsite",
        "poll_interval": 60,
        "comm": {
            "202.134.11.1": "test_rw_community"
        },
        "indices": {
             "202.134.11.1": {
                 "Ethernet1/23": "436218880",
                 "Ethernet1/16": "436218760",
             }
        },
        "https": {
            "use": true,
            "https_key": "/tmp/site-net-monitor/certs/host_key.pem",
            "https_cert": "/tmp/site-net-monitor/certs/host_cert.pem",
            "https_port": 8443
        }
    }


   Note: you can change the site-config.json file as per your site's information
  
