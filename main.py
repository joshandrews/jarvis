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

all_words = []
jarvis = ["jarvis", "jervis", "service", "jars", "chargers", "purvis", "burgers", "nervous", "tervis", "German", "earth", "rs", "things", "ervice", "drivers", "artist" "gorgeous", "first", "davis", "just", "don't", "harvest"]
stop = ["stop", "stopped", "suck", "sucks", "top", "test", "stock"]
run = True

def parsejson(obj):
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
	wordslist = words[0].encode('latin-1').split(' ')
	all_words.extend(wordslist)
	print all_words
    
def start():
	while(run):
		Recording = audiorecording.dorecord()
		thread.start_new_thread(getfromgoogle, (Recording, ))
		
def getfromgoogle(Recording):
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
	parsejson(data)



def analyze(i):
	while (len(all_words) > i or run):
		dobj = datetime.datetime.now()
		while (len(all_words) == i):
			time.sleep(.5)
		if (all_words[i] == "####"):
			os.system("Watch your language")
		if (all_words[i] == "what"):
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() == "what"):
					os.system('say in the butt')

			else:
				i-=1
				time.sleep(1)
				
		if (all_words[i] == "hello"):
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() in jarvis):
					os.system('say hello sir, how are you.')

			else:
				i-=1
				time.sleep(1)
		
		# Fix this, it is a complete gong show.. I mean really -- josh...
		if (all_words[i].lower() in jarvis):
			print all_words[i]
			if (len(all_words) > i+1):
				if (all_words[i+1].lower() in stop):
					os.system('say jarvis is shutting down')
					sys.exit()
				if (all_words[i+1] == 'dance'):
					os.system('say jarvis is dancing up a storm')
				if (all_words[i+1] == 'what'):
					if (len(all_words) > i+2):
						if (all_words[i+2] == 'time'):
							if (len(all_words) > i+3):
								if (all_words[i+3] == 'is'):
									if (len(all_words) > i+4):
										if (all_words[i+4] == 'it'):
											os.system('say it is'+str(dobj.hour)+" "+str(dobj.minute))
									else:
										i-=1
										time.sleep(1)
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
	analyze(0)