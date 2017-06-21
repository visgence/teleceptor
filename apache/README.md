# How to setup Teleceptor on Apache as a reverse proxy with mod_proxy

as root:
* yum install httpd
* systemctl start httpd
* systemctl enable httpd
* copy teleceptor.conf to /etc/httpd/conf.d/
* systemctl restart httpd

#### if running SELinux run:
  /usr/sbin/setsebool -P httpd_can_network_connect 1

### running teleceptor in system d:
* copy teleceptor.service to /etc/systemd/system
* systemctl daemon-reload
* systemctl start teleceptor
* systemctl status teleceptor

### make sure it starts on reboot:
* systemctl enable teleceptor
* systemctl enable postgresql-9.6
