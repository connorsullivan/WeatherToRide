
-- Create an administrative user to be used in DB connections
CREATE USER 'weather'@'localhost' IDENTIFIED BY 'password';

-- Grant all privileges to this new user
GRANT ALL PRIVILEGES ON *.* TO 'weather'@'localhost';
