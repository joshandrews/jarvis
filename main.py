import urllib
import urllib2
import pyaudio
import wave
import audiorecording
import json
import os
import thread
import time
import datetime
from xml.etree import ElementTree
import re
import jarvis_path
import gui

all_words = []
jarvis = ["jarvis", "jervis", "jersey", "germans", "dervis", "thomas", "travis", "garvis" "starbucks", "service", "jars", "charlotte", "chargers", "harris", "purvis", "burgers", "nervous", "tervis", "german", "earth","office", "rs", "things", "ervice", "drivers", "artist" "gorgeous", "first", "davis", "just", "don't", "harvest", "jerk"]
stop = ["stop", "stopped", "suck", "sucks", "top", "test", "stock"]
dance = ["dance", "damn", "dan"]
facebook = ["facebook.com", "facebook"]
pause = ["pause", "pos", "are", "pod", "hot"]
current = ["current", "temperature"]
temperature = ["temperature", "outside"]
high = ["hi", "high"]
clothing = ["everything. Just wear everything.", "jeans, with a tuuk, and gloves, and a fleece, and a sweater, and a winter coat, and whatever else you need.  It is super cold out, man", "jeans with a t-shirt and your fleece and a winter coat.  Perhaps the one from John Lewis.  It is rather cold out.", "jeans with a t-shirt and your smartwool or fleece.  It is kind of cold.", "jeans with a t-shirt and your smartwool.  It is balmy out.", "shorts and a t-shirt and your smartwool. It is warm out!", "shorts and a t-shirt.  It is hot out!"]
temps = [-40, -15, -5, 5, 10, 20, 35]
print len(clothing)
print len(temps)
run = True
wesbrook = ["westbrook", "wesbrook", "west"]
microphone = audiorecording.microphone()

def parsegooglejson(obj):
	jsonresponse = json.load(obj)
	status = jsonresponse['status']
	conf = 0
	report = []
	for utter_list in jsonresponse["hypotheses"]:
		for k in utter_list:
			report.append("%-10s : %s" % (k, utter_list[k]))
			if k == 'confidence':
				conf = float(utter_list[k])
	for key in jsonresponse:
		if key != "hypotheses":
			report.append("%-10s : %s" % (key, jsonresponse[key]))
	detailed = '\n'.join(report)
	words = tuple([line.split(':')[1].lstrip() for line in report if line.startswith('utterance')])
	confidence = tuple([line.split(':')[1].lstrip() for line in report if line.startswith('confidence')])
	print confidence
	wordslist = words[0].encode('latin-1').split(' ')
	all_words.extend(wordslist)
	print all_words
    
def start():
	while(run):
		WAV_RECORDING = microphone.record()
		thread.start_new_thread(getfromgoogle, (WAV_RECORDING, ))
		
def getfromgoogle(WAV_RECORDING):
	Recording =  microphone.wavtoflac(WAV_RECORDING)
	url = "https://www.google.com/speech-api/v1/recognize?client=chromium&lang=en-us"
	flac=open(Recording,"rb").read()
	header = {'Content-Type' : 'audio/x-flac; rate=44100'}
	try:
		req = urllib2.Request(url, flac, header)
		data = urllib2.urlopen(req)
	except:
		os.remove(Recording)
		return
	os.remove(Recording)
	parsegooglejson(data)

def parsetranslinkjson(obj):
	jsonresponse = json.load(obj)
	schedules = jsonresponse[0]['Schedules']
	leavetimes = []
	for sched in schedules:
		leavetimes.append(sched['ExpectedLeaveTime'].split(" ")[0].encode("latin-1"))
	return leavetimes
		

def getNextBusTimes(stop, routeno):
	url = "http://api.translink.ca/RTTIAPI/V1/stops/"+str(stop)+"/estimates?count=3&TimeFrame=1440&RouteNo="+str(routeno)+"&apiKey=PQuuoaRmkC1jlhtD2JA5"
	header = {'Content-Type' : 'application/JSON'}
	req = urllib2.Request(url, None, header)
	data = urllib2.urlopen(req)
	return parsetranslinkjson(data)

def parsedefinitionxml(data):
	tree = ElementTree.parse(data)
	root = tree.getroot()
	definitionlist = []
	if root is not None:
		for entry in root.findall('entry'):
			definition = entry.find('def')
			if definition is not None:
				for dt in definition.findall('dt'):
					if dt.text:
						if len(dt.text) > 15:
							txt = re.sub("[():{}]", " ", dt.text)
							definitionlist.append(txt)
	
	return definitionlist
	
def getDefinition(word):
	url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/"+word+"?key=65e3c274-1da8-45a0-b932-46da5f774769"
	header = {'Content-Type' : 'application/XML'}
	req = urllib2.Request(url, None, header)
	data = urllib2.urlopen(req)
	return parsedefinitionxml(data)

def parseweatherjson(data):
	jsonresponse = json.load(data)
	weather = jsonresponse['list'][0]['main']
	return weather
	
def getWeather(city, country=None):
	url = "http://api.openweathermap.org/data/2.1/find/name?q="+city+",%20"+country+"&units=metric"
	header = {'Content-Type' : 'application/json'}
	req = urllib2.Request(url, None, header)
	data = urllib2.urlopen(req)
	return parseweatherjson(data)
	
	
def analyze(i):
	jarvisWaiting = "yes?"
	while (len(all_words) > i or run):
		dobj = datetime.datetime.now()
		while (len(all_words) == i):
			time.sleep(.5)
		if (all_words[i] == "####"):
			os.system("say Watch your language")
		if (all_words[i] == "99"):
			leavetimes = getNextBusTimes(59266, 99)
			thread.start_new_thread(os.system, ("say The 99 leaves at "+str(leavetimes[0])+", "+str(leavetimes[1])+", and "+str(leavetimes[2]),))
			thread.start_new_thread(gui.sendToBrowser, ("["+str(leavetimes[0])+"], ["+str(leavetimes[1])+"], ["+str(leavetimes[2])+"]",))
		
		if (all_words[i] == "84"):
			leavetimes = getNextBusTimes(51917, 84)
			os.system("say The 84 leaves at "+str(leavetimes[0])+", "+str(leavetimes[1])+", and "+str(leavetimes[2]))
		
		if (all_words[i] == "44"):
			leavetimes = getNextBusTimes(51917, 44)
			os.system("say The 44 leaves at "+str(leavetimes[0])+", "+str(leavetimes[1])+", and "+str(leavetimes[2]))
				
		if (all_words[i] == "weather"):
			getWeather("UBC", "Canada");
		
		if (all_words[i] == "haha"):
			os.system("say ha ha ha ha")
		
		if (all_words[i].lower() in wesbrook):
			buses = [33, 41, 49, 25, 480]
			alltimes = []
			alltimes.append(getNextBusTimes(59272, 33))
			alltimes.append(getNextBusTimes(59273, 41))
			alltimes.append(getNextBusTimes(59275, 49))
			alltimes.append(getNextBusTimes(59271, 25))
			alltimes.append(getNextBusTimes(59270, 480))
			
			bustimes = []
			for times in alltimes:
				bustimes.append(time.strptime(times[0], "%I:%M%p"))
				
			besttime = time.localtime()
			for thetime in bustimes:
				if thetime > besttime:
					besttime = thetime
			
			print buses[bustimes.index(besttime)]
			
				
		if (all_words[i].lower() in current):
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() in temperature):
					weather = getWeather("UBC", "Canada")
					if weather is not None:
						temp = weather['temp']
						if temp is not None:
							os.system("say it is currently "+str(temp)+" degrees Celsius")
			else:
				i-=1
				time.sleep(.3)
		
		if (all_words[i] == "hello"):
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() in jarvis):
					os.system('say hello sir, how are you.')

			else:
				i-=1
				time.sleep(.3)
		
		if (all_words[i].lower() in high):
			if (len(all_words) > i+1):
				if (all_words[i+1] == 'for'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'today'):
							weather = getWeather("Vancouver", "Canada")
							if weather is not None:
								temp = weather['temp_max']
								if temp is not None:
									thread.start_new_thread(os.system, ("say the high is "+str(temp)+" degrees Celsius",))
									thread.start_new_thread(gui.sendToBrowser, ("the high is "+str(temp)+" degrees Celsius",))
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
		
		if (all_words[i] == 'low'):
			if (len(all_words) > i+1):
				if (all_words[i+1] == 'for'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'today'):
							weather = getWeather("UBC", "Canada")
							if weather is not None:
								temp = weather['temp_min']
								if temp is not None:
									thread.start_new_thread(os.system, ("say the low is "+str(temp)+" degrees Celsius",))
									thread.start_new_thread(gui.sendToBrowser, ("the low is "+str(temp)+" degrees Celsius",))
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
		
		if (all_words[i].lower() == 'should'):
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() == 'i'):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() == 'wear'):
							weather = getWeather("UBC", "Canada")
							print weather
							temp = None
							if weather is not None:
								temp = weather['temp']
							
							diff = 100
							win = None
							if temp is not None:
								for elem in temps:
									tdiff = abs(elem - temp)
									if tdiff < diff:
										diff = tdiff
										win = elem
								saystr = clothing[temps.index(win)]
								os.system("say you should wear "+saystr)
								print temp
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
		
		if (all_words[i] == 'mean'):
			if (len(all_words) > i+1):
				if (all_words[i+1] == 'to'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'me'):
							os.system("say i am sorry.")
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
				
		if (all_words[i] == 'what'):
			if (len(all_words) > i+1):
				if (all_words[i+1] == 'time'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'is'):
							if (len(all_words) > i+3):
								if (all_words[i+3] == 'it'):
									hour = dobj.hour
									if dobj.hour > 12:
										hour = dobj.hour-12
									if dobj.minute < 10:
										os.system('say it is'+str(hour)+" O "+str(dobj.minute))
									else:
										os.system('say it is'+str(hour)+" "+str(dobj.minute))
							else:
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
		if (all_words[i] == 'what'):
			if (len(all_words) > i+1):
				if (all_words[i+1] == 'is'):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() in jarvis):
							os.system("say I am your personal assistant.")
					else:
						i-=1
						time.sleep(1)
			else:
				i-=1
				time.sleep(1)
		
		if (all_words[i].lower() == "define"):
			if (len(all_words) > i+1):
				deflist = getDefinition(all_words[i+1].lower())
				if len(deflist) > 0:
					os.system("say "+getDefinition(all_words[i+1].lower())[0])
				else:
					os.system("say I cant define that")
			else:
				i-=1
				time.sleep(1)
			
		# Fix this, it is a complete gong show.. I mean really -- josh...
		if (all_words[i].lower() in jarvis):
			print all_words[i]
			if jarvisWaiting == "yes?":
				thread.start_new_thread(gui.sendToBrowser, (jarvisWaiting,))
				jarvisWaiting = ""
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() in stop):
					os.system('say jarvis is shutting down')
					sys.exit()
				if (all_words[i+1].lower() in facebook):
					os.system("/usr/bin/open -a '/Applications/Google Chrome.app' 'http://"+facebook[0]+"'")
				if (all_words[i+1] in dance):
					os.system('say jarvis is dancing up a storm')
				if (all_words[i+1] == "status"):
					os.system("say I am up and running")
					
				if (all_words[i+1].lower() == "open"):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() in facebook):
							os.system("/usr/bin/open -a '/Applications/Google Chrome.app' 'http://"+facebook[0]+"'")
					else:
						i-=1
						time.sleep(1)
				if (all_words[i+1] == "play"):
					if (len(all_words) > i+2):
						if (all_words[i+2]):
							os.system("itunes playlist '"+all_words[i+2]+"'")
					else:
						i-=1
						time.sleep(1)
				if (all_words[i+1].lower() in pause):
					os.system("itunes pause")
					
				if (all_words[i+1] == 'show'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'me'):
							if (len(all_words) > i+3):
								if (all_words[i+3] == 'my'):
									if (len(all_words) > i+4):
										if (all_words[i+4] == 'calendar'):
											os.system("/usr/bin/open -a '/Applications/Calendar.app'")
									else:
										i-=1
										time.sleep(1)
								if (all_words[i+3].lower() == 'evernote'):
									os.system("/usr/bin/open -a '/Applications/Evernote.app'")
							else:
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
				
				if (all_words[i+1] == 'tell'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'me'):
							if (len(all_words) > i+3):
								if (all_words[i+3] == 'a'):
									if (len(all_words) > i+4):
										if (all_words[i+4] == 'joke'):
											thread.start_new_thread(os.system, ("say Why did jarvis cross the road.  Just kidding, I'm a Robot",))
											thread.start_new_thread(gui.sendToBrowser, ("Why did jarvis cross the road.  Just kidding, I'm a Robot",))
									else:
										i-=1
										time.sleep(1)
							else:
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
				if (all_words[i+1].lower() == 'i'):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() == 'love'):
							if (len(all_words) > i+3):
								if (all_words[i+3].lower() == 'you'):
									os.system("say I love you too!")
							else:		
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
				if (all_words[i+1].lower() == 'set'):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() == 'the'):
							if (len(all_words) > i+3):
								if (all_words[i+3].lower() == 'mood'):
									os.system("itunes playlist jazz")
							else:		
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
				if (all_words[i+1].lower() == 'what'):
					if (len(all_words) > i+2):
						if (all_words[i+2].lower() == 'is'):
							if (len(all_words) > i+3):
								if (all_words[i+3].lower() == 'love'):
									thread.start_new_thread(os.system, ("say baby dont hurt me, dont hurt me, no more",))
									thread.start_new_thread(gui.sendToBrowser, ("baby dont hurt me, dont hurt me, no more",))
							else:		
								i-=1
								time.sleep(1)
					else:
						i-=1
						time.sleep(1)
				
			else:
				i-=1
				time.sleep(1)
		i+=1
		while (len(all_words) == i):
			time.sleep(.2)

if __name__ == '__main__':
	thread.start_new_thread(start, ())
	thread.start_new_thread(gui.startAllServers, ())
	analyze(0)
