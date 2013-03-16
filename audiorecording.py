import pyaudio
import wave
import os
import sys
import time
import subprocess, shlex
from array import array

def moving_average(data, sample_size):
    if (len(data) > 200):
    	data = data[100: ]
    sum = 0
    sampled = 0
    for x in range (0, sample_size):
    	index = len(data)-1-x
    	if (index >= 0):
    		sum += data[index]
    		sampled += 1
    	
    #print "sample size: " + str(sample_size)
    #print "sampled: " + str(sampled)
    return sum/sampled
    


def shellCall(shellCmd, stdin='', stderr=False):
    """Call a single system command with arguments, return its stdout.
    Returns stdout,stderr if stderr is True.
    Handles simple pipes, passing stdin to shellCmd (pipes are untested on windows)
    can accept string or list as the first argument
    """
    #This is all taken from psychopy
    if type(shellCmd) == str:
        shellCmdList = shlex.split(shellCmd) # safely split into cmd+list-of-args, no pipes here
    elif type(shellCmd) == list: # handles whitespace in filenames
        shellCmdList = shellCmd
    else:
        return None, 'shellCmd requires a list or string'
    proc = subprocess.Popen(shellCmdList, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutData, stderrData = proc.communicate(stdin)
    del proc
    if stderr:
        return stdoutData.strip(), stderrData.strip()
    else:
        return stdoutData.strip()

def record():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 5
	FLAC_CONV = 'flac -f '
	
	threshold = 10 
	maxValue = 0
	
	p = pyaudio.PyAudio()
	WAV_RECORDING = 'wavrecording%.6f' % time.time()+'.wav'
	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)
	
	#print("* recording")
	
	frames = []
	datalist = []
	movavglist = []
	send = 0
	while True:
		data = stream.read(CHUNK)
		asInts = array('h', data)
		average = sum(asInts)/float(len(asInts))
		datalist.append(average)
		movavg = moving_average(datalist, 20)
		if (movavg > .5 or movavg < -.5):
			movavglist.append(1.0)
		else:
			movavglist.append(0.0)
		reco = moving_average(movavglist, 10)
		if (reco > 0.1):
			send += 1;
			#print "speaking"
			frames.append(data)	
		elif send > 12:
			break;
		
			
	
	#print("* done recording")
	
	stream.stop_stream()
	stream.close()
	p.terminate()
	
	wf = wave.open(WAV_RECORDING, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	return WAV_RECORDING

def wavtoflac(WAV_RECORDING):
	FLAC_CONV = 'flac -f '
	# Shitty transcoder stuff to convert wav to flac
	FLAC_PATH, _ = shellCall(['/usr/bin/which', 'flac'], stderr=True)
	tmp_wav = WAV_RECORDING
	if not os.path.isfile(FLAC_PATH):
		sys.exit("failed to find flac, download it for your computer!!!!!")
	filetype = "x-flac"
	tmp = 'flacrecording%.6f' % time.time()+'.flac'
	flac_cmd = [FLAC_PATH, "-8", "-f", "--totally-silent", "-o", tmp, WAV_RECORDING]
	_, se = shellCall(flac_cmd, stderr=True)
	if se: logging.warn(se)
	while not os.path.isfile(tmp): # just try again
		# ~2% incidence when recording for 1s, 650+ trials
		# never got two in a row; time.sleep() does not help
		logging.warn('Failed to convert to tmp.flac; trying again')
		_, se = shellCall(flac_cmd, stderr=True)
		if se: logging.warn(se)
	WAV_RECORDING = tmp # note to self: ugly & confusing to switch up like this
	os.remove(tmp_wav)
	return tmp

def dorecord():
	WAV_RECORDING = record()
	return wavtoflac(WAV_RECORDING)