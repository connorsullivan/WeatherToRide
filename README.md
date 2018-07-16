# WeatherToRide

* Making travel plans can be challenging, especially when you don't know how the weather will behave.

* For those riding motorcycles or other exposed vehicles, bad weather can make potential outings a no-go.

* WeatherToRide is designed with riders in mind and helps to solve this problem by providing on-demand weather forecasting for the days and times you'll be out in the elements.

* After registering an account, simply tell us your travel schedule and we'll let you know if you're good to ride or should maybe take the car instead.

## Built With

* [Python](https://www.python.org/) - The programming language
* [Flask](http://flask.pocoo.org/) - The web framework
* [MySQL](https://www.mysql.com/) - The database

### Prerequisites & Installations

This repository is a ready-to-go (almost) Vagrant project! This means that getting up and running is very simple. Just make sure that you have [Vagrant](https://www.vagrantup.com/) installed on your machine.

Before trying to run the Vagrant project, you'll need to add an "instance" folder to the root directory. This folder contains settings that I cannot provide for you (such as encryption and third-party API keys).

```
cd WeatherToRide
mkdir instance
```

Inside of this instance folder, you'll need to add a 'config.py' file.

```
cd WeatherToRide/instance
touch config.py
```

Inside of this config file, add the following:

```
# This is used to encrypt session data (e.g. cookies)
SECRET_KEY = 'put some secure key here'
```

If you wish to take advantage of the SendGrid and Twilio functionality, you will need to add your API keys for these services in this config file as well.

By default, this project will automatically create the WeatherToRide database (not the tables) and an administrative user, called "weather". The default password for the "weather" user is "password". Flask-SQLAlchemy uses this information to connect to the MySQL database. The default connection string is located in WeatherToRide/config.py. If you wish to change any of these values, make sure to edit this setting, shown below:

```
# Database connection string
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://weather:password@localhost:3306/WeatherToRide'
```

For added security, this connection string can be moved to WeatherToRide/instance/config.py. This will keep it from being added to your Git repository if you decide to fork this project.

Lastly, you'll need to create the database tables. The easiest way to accomplish this is by running the development server (see below) and then stopping it with <kbd>Ctrl</kbd> + <kbd>C</kbd>.

### Running The Development Server

To launch the development server, connect to the Vagrant machine and execute 'run.py' in the project root.

```
vagrant ssh

python3 /var/www/WeatherToRide/run.py
```

The development server is available at http://localhost:5000/, although this can be changed by editing the 'run.py' file.

### Running The Production Server

The production server should be available automatically after initializing the Vagrant project at http://localhost:8080/. If you make any changes and need to reload Apache, simply type the following:

```
sudo service apache2 restart
```

## Authors

* **Gregory C. Sullivan**
