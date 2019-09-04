import subprocess
import math
from pydub import AudioSegment
from deep_emotion_recognition import DeepEmotionRecognizer
from glob import glob
from statistics import mode

def convert(f):
	spf = wave.open(f, 'rb')                  
    CHANNELS = spf.getnchannels()
    swidth = spf.getsampwidth()
    signal = spf.readframes(-1)
    spf.close()
    r = f.split('.')[:-1]+"_c.wav"
    wf = wave.open(r, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(swidth)
    wf.setframerate(16000)
    wf.writeframes(signal)
    wf.close()
    return(r)

def doDiarize(filename):
	subprocess.call(['cd', '/speaker-diarization'])
	subprocess.call(['./spk-diarization2.py', filename])
	output = str(subprocess.check_output(['cat', 'stdout']), 'utf-8')
	return output


def parse(output):
	string = output
	## audio=Audiosamples/1-r.wav lna=a_32 start-time=178.492 end-time=212.968 speaker=speaker_2
	speaker = list()
	for line in string.split('\n'):
		if (line):
			terms = line.split(' ')
			segment=dict()
			segment['start'] = round(float(terms[2].split('=')[-1])/3, 3)
			segment['end'] = 	round(float(terms[3].split('=')[-1])/3, 3)
			segment['i'] = int(terms[4].split('_')[-1])
		
			if speaker and speaker[-1]['i'] == segment['i'] :
				speaker[-1]['end'] = segment['end']
			else :
				speaker.append(segment)

	return speaker

def splitAudio(speaker, audiofile):

	conv = AudioSegment.from_wav(audiofile)
	chunk_silent = AudioSegment.silent(duration = 200)
	spk1 = []
	spk2 = []
	i=0
	for segment in speaker:
		chunk = conv[segment['start']*1000:segment['end']*1000]
		chunk = chunk_silent+chunk+chunk_silent
		filename = "/exported/"+segment['i'] + "_{}".format(i)+".wav"
		chunk.export(filename, bitrate ='16k', format ="wav")
		if(segment['i'] == 1):
			spk1.append(sentimentAnalysis(filename))
		else:
			spk2.append(sentimentAnalysis(filename))
		i += 1
	print("speaker1 ",mode(spk1))
	print("speaker2 ",mode(spk2))
		
def sentimentAnalysis(filename):
	# initialize instance
	# inherited from emotion_recognition.EmotionRecognizer
	# default parameters (LSTM: 128x2, Dense:128x2)
	deeprec = DeepEmotionRecognizer(emotions=['angry', 'sad', 'neutral', 'ps', 'happy'], n_rnn_layers=2, n_dense_layers=2, rnn_units=128, dense_units=128)
	# train the model
	deeprec.train()
	# get the accuracy
	# predict angry audio sample
	prediction = deeprec.predict(filename)
	print(f"Prediction: {prediction}")
	return prediction
	
def main():
	files = glob('/clips/*.wav')
	for f in files:
		splitAudio(parse(doDiarize(convert(f))), f)
		
	
	
		
		

