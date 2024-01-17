#!/bin/bash

# Copy the service file to the systemd directory
cp /root/site-net-monitor/site-traffic-monitor.service /etc/systemd/system/

# Reload the systemd daemon to pick up the new service file
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable site-traffic-monitor.service

# Start the service
systemctl start site-traffic-monitor.service

