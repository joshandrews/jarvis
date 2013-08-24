import urllib2
import json
import datetime
import math

def distanceLatLong(lat1,lon1,lat2,lon2):
    radius = 6371 # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dis = radius * c

    return dis

def getBusRoutes():
	routesURL = "http://api.wmata.com/Bus.svc/json/jRoutes?api_key=7hs7b6hdx8gtef6wzjm8fdwh"
	header = {'Content-Type' : 'application/JSON'}
	req = urllib2.Request(routesURL, None, header)
	data = urllib2.urlopen(req)
	allRoutes = []
	jsonresponse = json.load(data)	
	for route in jsonresponse['Routes']:
		allRoutes.append(route['RouteID'])
	return allRoutes
	
def getBusScheduleForStop(stopID):
	dobj = datetime.datetime.now()
	url = "http://api.wmata.com/Bus.svc/json/jStopSchedule?stopId="+str(stopID)+"&date="+dobj.strftime('%Y-%m-%d')+"&api_key=7hs7b6hdx8gtef6wzjm8fdwh"
	header = {'Content-Type' : 'application/JSON'}
	req = urllib2.Request(url, None, header)
	data = urllib2.urlopen(req)
	schedule = []
	jsonresponse = json.load(data)
	for sched in jsonresponse['ScheduleArrivals']:
		if datetime.datetime.strptime(sched['ScheduleTime'], "%Y-%m-%dT%H:%M:%S") > dobj:
			schedule.append(datetime.datetime.strptime(sched['ScheduleTime'], "%Y-%m-%dT%H:%M:%S"))
	return schedule
	
def findClosestBusStopForRoute(routeID):
	url = "http://api.wmata.com/Bus.svc/json/jStops?lat=38.906937&lon=-77.070754&radius=500&api_key=7hs7b6hdx8gtef6wzjm8fdwh"
	header = {'Content-Type' : 'application/JSON'}
	req = urllib2.Request(url, None, header)
	data = urllib2.urlopen(req)
	theStop = 0
	distance = 999 #km
	jsonresponse = json.load(data)
	for stop in jsonresponse['Stops']:
		for route in stop['Routes']:
			if route == routeID:
				if distanceLatLong(38.906937,-77.070754,float(stop['Lat']),float(stop['Lon'])) < distance:
					distance = distanceLatLong(38.906937,-77.070754,float(stop['Lat']),float(stop['Lon']))
					theStop = stop['StopID']
	return theStop
	
busRoutes = getBusRoutes()
closeStopID = findClosestBusStopForRoute("D5")
print closeStopID
print getBusScheduleForStop(closeStopID)

