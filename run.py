'''

This file should only be used to launch the development server.

For production, use Apache or something similar.

'''

from WeatherToRide import app

# Launch the development server
if __name__ == "__main__":
    app.config['ENV'] = 'development'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
