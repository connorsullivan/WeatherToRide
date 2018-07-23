#!/usr/bin/env bash

PROJECT_NAME="WeatherToRide"

PROJECT_FOLDER="/var/www/${PROJECT_NAME}"

# Create the project folder (if it doesn't already exist)
mkdir ${PROJECT_FOLDER}

# Prevent user interaction (for automatic installs)
export DEBIAN_FRONTEND=noninteractive

# Prepare for package installations
apt-get update
apt-get -y upgrade

# Apache
apt-get -y install apache2

# MySQL
apt-get -y install mysql-server

# Set up the database
mysql < ${PROJECT_FOLDER}/db/createDatabase.sql
mysql < ${PROJECT_FOLDER}/db/createUser.sql

# Python
apt-get -y install python3

# Pip
apt-get -y install python3-pip
sudo -H pip3 install --upgrade pip

# Install Python package requirements with Pip
pip3 install -r ${PROJECT_FOLDER}/requirements.txt

# Install and enable mod_wsgi
apt-get -y install libapache2-mod-wsgi-py3 python3-dev
a2enmod wsgi

# Copy the VirtualHost file to the appropriate location
cp ${PROJECT_FOLDER}/${PROJECT_NAME}.conf /etc/apache2/sites-available/${PROJECT_NAME}.conf

# Disable the default VirtualHost file and enable the new one
a2dissite 000-default
a2ensite ${PROJECT_NAME}.conf

# Restart Apache
service apache2 restart