CREATE DATABASE WeatherToRide;

CREATE USER 'weather'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON *.* TO 'weather'@'localhost' IDENTIFIED BY 'password' WITH GRANT OPTION;

FLUSH PRIVILEGES;