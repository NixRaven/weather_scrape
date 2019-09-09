#!/usr/bin/python3.6
# a script to scrape weather info about the weather in paris and portland and compare weather data over time

#imports
import requests
import json
from lxml import html
import re
import time

# a file update function
def update_json(path, info):
	#check if file has been updated today

	last_line = []

	try:
		with open(path, 'r') as f:
			for l in f:
				last_line = json.loads(l)
	except IOError:
		last_line = ['','','','','','']

	if (last_line[4] != info[4]) or (last_line[5] != info[5]):
		f = open(path, 'a')
		f.write(json.dumps(info) + '\n')
		f.close()


# a function to convert the data input into useful data types and formats to dump into the json
def weath_format(weath_st, wind_st):
	# define variables
	weath_cond = re.search(r'.*\w+(?=\.)', weath_st).group()
	# temporary variable used to allow us to get rid of the first instance of the number search so that we can search for the second number instance without catching the first instance again.
	temporary = re.search(r'\b\d+\b', weath_st)
	# remove the first number from the string
	weath_st = weath_st.replace(temporary.group(), '', 1)
	# finaly get our temperature integer and then find and convert the next
	temp1 = temporary.group()
	temp2 = re.search(r'\b\d+\b', weath_st).group()

	# temporary variable to clean the humidity number from the string allowing a search for the second number containging windspeed
	temporary = re.search(r'\b\d+\b', wind_st)
	# clean the humidity number from the string
	wind_st = wind_st.replace(temporary.group(), '', 1)
	# get the windspeed
	wind_spd = re.search(r'\b\d+\b', wind_st).group()

	return([weath_cond, temp1, temp2, wind_spd])
	

# a function for finding the weather info given a url input
def get_stats(url, time_offset):

 r = requests.get(url)

 # check for url request errors.  If anything went wrong, exit
 if (r.status_code != 200):
  exit()
  print("url could not be reached")

 tree = html.fromstring(r.text)

 # get the temperature and further information on the weather
 weather = tree.xpath('//h3[@class="mgt0"]/../p/text()')[0]
 wind = tree.xpath('//h3[@class="mgt0"]//../p/text()')[1]
 DATE = time.localtime(time.time() + (time_offset * 3600.0) - (24.0 * 3600.0))
 date = [DATE[0], DATE[7]]

 # call data conversion
 weather_dat = weath_format(weather, wind)

 #return variables
 return(weather_dat + date)

# a quick function to increment through dates for testing
def date_add(date_in):
	if (date_in[1] > 364):
		date_in[0] += 1
		date_in[1] = 1
	else:
		date_in[1] += 1

	return(date_in)

# a function to generate a large weather data file for testing purposes
def fill_file(PDX_PATH, PARIS_PATH, pdx_weather, paris_weather, length):
	x = 0
	while x < length:
		x += 1
		[pdx_weather[4], pdx_weather[5]] = date_add([pdx_weather[4], pdx_weather[5]])
		[paris_weather[4], paris_weather[5]] = date_add([paris_weather[4], paris_weather[5]])
		update_json(PDX_PATH, pdx_weather)
		update_json(PARIS_PATH, paris_weather)

def main():
	# set urls for sites and pathnames for files
	PARIS_URL = 'https://www.timeanddate.com/weather/france/paris'
	PDX_URL = 'https://www.timeanddate.com/weather/usa/portland-or'
	PDX_PATH = 'pdx_weather.json'
	PARIS_PATH = 'paris_weather.json'

	# set variables for paris and portland
	PDX_WEATHER = 'https://www.timeanddate.com/weather/france/paris'
	PDX_URL = 'https://www.timeanddate.com/weather/usa/portland-or'
	PDX_PATH = 'pdx_weather.json'
	PARIS_PATH = 'paris_weather.json'

	# set variables for paris and portland
	pdx_weather = get_stats(PDX_URL, 0)
	paris_weather = get_stats(PARIS_URL, 9)

	# add weather data to portland and paris jsons and print weather data to user
	update_json(PDX_PATH, pdx_weather)
	update_json(PARIS_PATH, paris_weather)
	print('Yesterdays weather for Portland: ', pdx_weather)
	print('Yesterdays weather for Paris: ', paris_weather)

	# uncomment this line to generate a large test data set
	#fill_file(PDX_PATH, PARIS_PATH, pdx_weather, paris_weather, 500)


main()

