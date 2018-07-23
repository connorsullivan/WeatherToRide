# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/bionic64"

  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.synced_folder ".", "/var/www/WeatherToRide"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "WeatherToRide"
  end

  config.vm.provision :shell, path: "provision.sh"

end