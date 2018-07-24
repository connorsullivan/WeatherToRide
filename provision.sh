#!/usr/bin/env bash

PROJECT_NAME="WeatherToRide"

PROJECT_FOLDER="/var/www/${PROJECT_NAME}"

# Create the project folder (if it doesn't already exist)
mkdir ${PROJECT_FOLDER}

# Prevent user interaction (for automatic installs)
export DEBIAN_FRONTEND=noninteractive

# Prepare for package installations
sudo apt-get update
sudo apt-get -y upgrade

# Apache
sudo apt-get -y install apache2

# MySQL
sudo apt-get -y install mysql-server

# Set up the database
sudo mysql < ${PROJECT_FOLDER}/db/createDatabase.sql
sudo mysql < ${PROJECT_FOLDER}/db/createUser.sql

# Python
sudo apt-get -y install python3 python3-dev python3-pip

# Upgrade pip
sudo -H pip3 install --upgrade pip

# Install Python packages w/ pip
sudo pip3 install -r ${PROJECT_FOLDER}/requirements.txt

# Install and enable mod_wsgi
sudo apt-get -y install libapache2-mod-wsgi-py3
sudo a2enmod wsgi

# Copy the new VirtualHost file to the appropriate location
sudo cp ${PROJECT_FOLDER}/${PROJECT_NAME}.conf /etc/apache2/sites-available/${PROJECT_NAME}.conf

# Disable the default VirtualHost file and enable the new one
sudo a2dissite 000-default
sudo a2ensite ${PROJECT_NAME}.conf

# Restart Apache
sudo service apache2 restart