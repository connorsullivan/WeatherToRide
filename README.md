# WeatherToRide

* Making travel plans can be challenging, especially when you don't know how the weather will behave.

* For those riding motorcycles or other exposed vehicles, bad weather can make potential outings a no-go.

* WeatherToRide is designed with riders in mind and helps to solve this problem by providing on-demand weather forecasting for the days and times you'll be out in the elements.

* After registering an account, simply tell us your travel schedule and we'll let you know if you're good to ride or should maybe take the car instead.

## Built With

* [Python](https://www.python.org/) - The programming language
* [Flask](http://flask.pocoo.org/) - The web framework
* [MySQL](https://www.mysql.com/) - The database

### Getting Started

This repository is a ready-to-go (almost) Vagrant project! This means that getting up and running is very simple. Just make sure that you have [Vagrant](https://www.vagrantup.com/) installed on your machine.

Before trying to run the project, you'll need to add an "instance" folder to the root directory. This folder should contains settings that are specific to your instance of the project (such as encryption and third-party API keys).

```
cd WeatherToRide
mkdir instance
```

Inside of this instance folder, add a 'config.py' file.

```
cd WeatherToRide/instance
touch config.py
```

This instance/config.py file will be loaded after the root config.py file. It will override any settings defined in the latter.

Inside of the instance/config.py file, add the following:

```
# This is used to encrypt session data (e.g. cookies)
SECRET_KEY = 'put some secure key here'
```

Vagrant will automatically create the WeatherToRide database and an administrative MySQL user, called "weather". The default password for the "weather" user is "password". Flask-SQLAlchemy uses this information in the root config.py file. If you wish to make changes to the database settings, make sure to edit the database connection string, shown below:

```
# Database connection string
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://weather:password@localhost:3306/WeatherToRide'
```

For added security, this connection string can be moved to /instance/config.py. This will keep it from being added to your Git repository if you decide to fork this project and change the default values.

Lastly, you'll need to create the tables inside of the existing database. The easiest way to accomplish this is by running the development server (see below) and then stopping it with <kbd>Ctrl</kbd> + <kbd>C</kbd>.

### Running The Development Server

The 'run.py' file launches the development server on http://localhost:5000/.

To run this file, type the following from within the Vagrant shell:

```
python3 /var/www/WeatherToRide/run.py
```

### Running The Production Server

The production server should be available automatically after initializing the Vagrant project.

In order to access it, navigate in a web browser to http://localhost:8080/.

If you make any changes to server files and need to reload the production server, simply use:

```
sudo service apache2 restart
```

## Authors

* **Gregory C. Sullivan**
