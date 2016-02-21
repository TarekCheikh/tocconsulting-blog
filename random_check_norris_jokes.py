#! /usr/bin/python

import requests

# Getting a random Check Norris joke

json_joke = requests.get(\
		"http://api.icndb.com/jokes/random?exclude=explicite").json()
# Print after replacing "&quot;" with ""
print (json_joke['value']['joke']).replace("&quot;", "\"")
