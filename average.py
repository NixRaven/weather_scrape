#! /usr/bin/python3.6
#
# a program to interpret the data from the json files produced by scraper.py
# analyzes average conditions for the last 30 days, 90 days, and year

import json

# a function to read our json files into variables. These will be pretty long lists.  This function will also rewrite the file deleting the oldest files untill there are no more than 365 lines.
def read_data(path):
	cont = []	
	
	try:
		with open(path, 'r') as f:
			for l in f:
				cont.append(json.loads(l))
		f.close()
	except IOError:
		raise IOError('file not found')
	except:
		raise StandardError('unknown error')

	if (len(cont) > 365):
		cont = cont[-365:len(cont)]
		f = open(path, 'w')
		for l in cont:
			f.write(json.dumps(l) + '\n')
		f.close()

	return(cont)

# a function to collect agregate date about the data sets
def stats(data):
	# create variables
	w_stats = dict(
		tempHigh=0,
		tempLow=0,
		avHigh30=0,
		avLow30=0,
		avHigh90=0,
		avLow90=0,
		weather={},
		weather30={},
		weather90={},
		wind=0,
		wind30=0,
		wind90=0
	)
	# a variable to flag if there are any changes in date by more than one day between linew of the data
	good = True
	last_date = ['','']
	
	# flag of the data set is not complete
	full = not bool(len(data) < 365)

	# loop through the data from the most recent (last) entry to the oldest (first) entry.
	i = 0
	while (i > -len(data)):
		# increment index
		i -= 1

		# check date of current line against date of last line
		if last_date != ['','']:
			if (data[i][5] != last_date[1] - 1) and not ((data[i][5] == 365) and (data[i][4] == last_date[0] - 1) and (last_date[1] == 1)):
				good = False
		last_date = [data[i][4], data[i][5]]

		# check if weather condition has been encountered before. If it has, increment the value associated with it. Otherwise, create an element to represent its occurence
		if data[i][0] in w_stats['weather']:
			w_stats['weather'][data[i][0]] += 1
		else:
			w_stats['weather'][data[i][0]] = 1

		# increment stat totals
		w_stats['tempHigh'] += int(data[i][1])
		w_stats['tempLow'] += int(data[i][2])
		w_stats['wind'] += int(data[i][3])

		# check if this is the 30 or 90 day total. Iff so, set those variables.
		if (i >= -30):
			w_stats['avHigh30'] = w_stats['tempHigh'] / -i
			w_stats['avLow30'] = w_stats['tempLow'] / -i
			w_stats['wind30'] = w_stats['wind'] / -i
			w_stats['weather30'] = w_stats['weather'].copy()
		
		if (i >= -90):
			w_stats['avHigh90'] = w_stats['tempHigh'] / -i
			w_stats['avLow90'] = w_stats['tempLow'] / -i
			w_stats['wind90'] = w_stats['wind'] / -i
			w_stats['weather90'] = w_stats['weather'].copy()

	w_stats['tempHigh'] = w_stats['tempHigh'] / len(data)
	w_stats['tempLow'] = w_stats['tempLow'] / len(data)
	w_stats['wind'] = w_stats['wind'] / len(data)


	return([w_stats, good, full])

# a function print one set of averages
def print_avgs(avHigh, avLow, avWind, avWeather, prologue):
	print(f'\n{prologue}:\nTemperature: {avHigh} / {avLow} (degrees F)     Wind Speed: {avWind}mph')
		
	# loop through weather conditions
	for k, v in avWeather.items():
		print(f'The weather was {k} for {v} days out of the {prologue.lower()}')
	
	return(1)

# a function to make nice readable output
def readable_out(data, city, good=True, full=True):
	print(f'\nAVERAGE WEATHER FOR {city}:\n')

	print_avgs(data['avHigh30'], data['avLow30'], data['wind30'], data['weather30'], 'LAST 30 DAYS')
	print_avgs(data['avHigh90'], data['avLow90'], data['wind90'], data['weather90'], 'LAST 90 DAYS')
	print_avgs(data['tempHigh'], data['tempLow'], data['wind'], data['weather'], 'LAST 365 DAYS')

	if not full or not good:
		print('\nWarning: incomplete or corrupted data set.  Averages may not be reliable for any specific date range.\n')

# main function
def main():
	# create lists of all the data from our weather files
	try:
		paris_dat = read_data('paris_weather.json')
		pdx_dat = read_data('pdx_weather.json')
	except IOError:
		print('Error: data set does not exist or could not be found. Use scraper.py to populate data set.')
		return(0)
	except:
		print('An unknown error occured')
		return(0)

	paris_stats = stats(paris_dat)
	pdx_stats = stats(pdx_dat)

	readable_out(paris_stats[0], 'PARIS', paris_stats[1], paris_stats[2])
	readable_out(pdx_stats[0], 'PORTLAND', pdx_stats[1], pdx_stats[2])

main()

