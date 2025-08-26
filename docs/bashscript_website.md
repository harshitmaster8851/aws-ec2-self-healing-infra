#!/bin/bash
sudo dnf update -y
sudo dnf install -y httpd unzip wget
sudo systemctl enable httpd
sudo systemctl start httpd
cd /tmp
wget https://www.tooplate.com/zip-templates/2140_stellaris_research.zip -O website.zip
unzip -o website.zip
sudo rm -rf /var/www/html/*
sudo cp -r 2140_stellaris_research/* /var/www/html/
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html
sudo systemctl restart httpd
