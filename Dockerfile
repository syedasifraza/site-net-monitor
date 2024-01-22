FROM almalinux:8

# Install EPEL repository (required for SupervisorD)
RUN dnf install -y epel-release && \
    dnf clean all

# Install SupervisorD
RUN dnf install -y  supervisor && \
    dnf clean all

RUN dnf install -y vim net-snmp git net-snmp-devel python3-devel gcc net-snmp-utils

RUN pip3 install easysnmp==0.2.5

# Copy your SupervisorD configuration files into the image
COPY supervisord.conf /etc/supervisord.conf

#COPY site-net-monitor/

WORKDIR /root/site-net-monitor/

# Expose any ports that your application may use
EXPOSE 443 80

# Start SupervisorD when the container starts
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
