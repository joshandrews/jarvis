import urllib
import urllib2
import pyaudio
import wave

Recording = 'recording.flac'
 
 
url = "https://www.google.com/speech-api/v1/recognize?client=chromium&lang=en-us"
flac=open(Recording,"rb").read()
header = {'Content-Type' : 'audio/x-flac; rate=44100'}
req = urllib2.Request(url, flac, header)
data = urllib2.urlopen(req)
print data.read()