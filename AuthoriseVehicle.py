import PredictCharacters
import urllib.request as req
import requests
import json
from shared import *
import datetime

urlToOpen = baseUrl + '/vehicles?licenseplate=' + PredictCharacters.licensePlate + '&crossing_gte=1'

access = False

try:
	with req.urlopen(urlToOpen) as response:
		data = json.load(response)
except Exception as exc:
	print('An error occured!')
	print(exc.reason)

# there is some response
if len(data):
	obj = data[0]

	#cast to int
	obj['crossing'] = int(obj['crossing'])

	if (obj['crossing']) > 0:
		access = True

		#modify object
		obj['crossing'] -= 1
		obj['timeCrossed'] = datetime.datetime.utcnow().isoformat()


		#url to put
		urlToPut = baseUrl + 'vehicles/' + str(obj['id'])

		#put to server side database
		requests.put(urlToPut, data=obj)		

if access:
	print('Toll gate opened! Thanks for your visit!')
else:
	print('You are not authorized to pass!')

