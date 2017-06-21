How
as root
yum install httpd
systemctl start httpd
systemctl enable httpd

copy teleceptor.conf to /etc/httpd/conf.d/

systemctl restart httpd

if running SELinux run:
  /usr/sbin/setsebool -P httpd_can_network_connect 1


run in system d
