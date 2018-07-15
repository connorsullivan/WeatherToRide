# WeatherToRide

* Making travel plans can be challenging, especially when you don't know how the weather will behave.

* For those riding motorcycles or other exposed vehicles, bad weather can make potential outings a no-go.

* WeatherToRide is designed with riders in mind and helps to solve this problem by providing on-demand weather forecasting for the days and times you'll be out in the elements.

* After registering an account, simply tell us your travel schedule and we'll let you know if you're good to ride or should maybe take the car instead.

## Built With

* [Python](https://www.python.org/) - The programming language
* [Flask](http://flask.pocoo.org/) - The web framework
* [MySQL](https://www.mysql.com/) - The database

## Getting Started

To get started with your own copy of this application, simply fork or clone this repository.

### Prerequisites & Installations

WeatherToRide is built using [Python 3](https://www.python.org/).

[Flask](http://flask.pocoo.org/) and its related dependencies can be added using pip.

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

Once you have the necessary software installed (see above), getting the development server running is very simple.

Open a terminal, navigate to the project root directory, and type the following command:

```
python run.py
```

If you're using Linux or have different versions of Python installed on the same machine, you might need to use a slightly different command:

```
python3 run.py
```

The development server should launch and be available at http://localhost:5000/.

## Authors

* **Gregory C. Sullivan**
* **Branwin R. Dubose**
