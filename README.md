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
  Edit the site-config.json file and add your SNMP community information & your border router/switch interfaces information

  $$ vim site-config.json
  

  
  
