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

It is good practice to run projects like this inside of isolated environments (such as a Python virtual environment or a virtual machine). I recommend using [Vagrant](https://www.vagrantup.com/), but Python's [venv](https://docs.python.org/3/library/venv.html) is also ok.

WeatherToRide is built using [Python 3](https://www.python.org/).

[Flask](http://flask.pocoo.org/) and its related dependencies can be added using pip (from the root directory of the project).

```
pip install -r requirements.txt
```

You'll also need a [MySQL server](https://www.mysql.com/) to store the data.

Finally, you'll need to add an 'instance' folder to the root directory.

```
cd [root directory]
mkdir instance
```

Inside of this instance folder, you'll need to add a 'config.py' file.

```
cd [root directory]/instance
touch config.py
```

Inside of this config file, add at least the following values:

```
# This is used to encrypt session data (e.g. cookies)
SECRET_KEY = 'put your secret key here'

# This tells SQLALCHEMY how to connect to your database
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://[user]:[password]@[host]:[port]/[db]"
```

If you wish to take advantage of the SendGrid and Twilio functionality, you will need to add the API keys in this config file as well. Please consult the websites for these services to learn more.

### Running The Development Server

The development server is intended to be used for development only (go figure). If you are planning on deploying this (or any) application in a production environment, use a more robust web server, such as Apache (or something similar).

To launch the development server, run the 'run.py' file in the root directory from a terminal.

```
python run.py
```

If you're using Linux and/or have Python 2 installed on the same machine, you should use this command instead:

```
python3 run.py
```

The default settings will run the server on http://localhost:5000/, although this behavior can be changed by editing the 'run.py' file.

## Authors

* **Gregory C. Sullivan**
* **Branwin R. Dubose**
