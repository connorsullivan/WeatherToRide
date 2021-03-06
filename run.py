
# This file should only be used to launch the development server.

from WeatherToRide import app, db

if __name__ == '__main__':

	# Create the DB tables if they don't already exist
	db.create_all()

	# Configure the development environment
	app.config['ENV'] = 'development'
	app.config['TESTING'] = True
	app.debug = True

	# Run the development server
	app.run(host='0.0.0.0', port=5000)
