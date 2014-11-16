import wave
import binascii
import math
import struct
import os


############### RAW DATA ###########################################################"
def getDataFromWav(fileName) :
        fileIn = open(fileName, 'rb')
        data=fileIn.read(os.path.getsize(fileName))
        fileIn.close()
        return data

def getWavHeader(bufHeader) :
  stHeaderFields = {'ChunkSize' : 0, 'Format' : '',
        'Subchunk1Size' : 0, 'AudioFormat' : 0,
        'NumChannels' : 0, 'SampleRate' : 0,
        'ByteRate' : 0, 'BlockAlign' : 0,
        'BitsPerSample' : 0, 'Filename': ''}
  # Parse fields
  stHeaderFields['ChunkSize'] = struct.unpack('<L', bufHeader[4:8])[0]
  stHeaderFields['Format'] = bufHeader[8:12]
  stHeaderFields['Subchunk1Size'] = struct.unpack('<L', bufHeader[16:20])[0]
  stHeaderFields['AudioFormat'] = struct.unpack('<H', bufHeader[20:22])[0]
  stHeaderFields['NumChannels'] = struct.unpack('<H', bufHeader[22:24])[0]
  stHeaderFields['SampleRate'] = struct.unpack('<L', bufHeader[24:28])[0]
  stHeaderFields['ByteRate'] = struct.unpack('<L', bufHeader[28:32])[0]
  stHeaderFields['BlockAlign'] = struct.unpack('<H', bufHeader[32:34])[0]
  stHeaderFields['BitsPerSample'] = struct.unpack('<H', bufHeader[34:36])[0]
  return stHeaderFields

def getSignalfromData(data) :
  Header = getWavHeader(data)
  n=Header['BitsPerSample']/4
  L=data[44:]
  nFrames=len(L)/n
  L2=[]
  for K in range(nFrames) :
          valeur=int(binascii.hexlify(L[4*K:4*K+4]),16)
          L2.append(valeur)
  
  return L2
#####################################################################################

##############Wav File###############################################################
def normWavSignal(wavSignal) :
        norm = 0
        wavSignal.setpos(0)
        for i in range(wavSignal.getnframes()) :
                norm += int(binascii.hexlify(wavSignal.readframes(1)),16)**2
        return math.sqrt(norm)

def getSignalfromWav(fileName) :
        WAV = wave.open(fileName,'r')
        Freq = WAV.getframerate()
        N=WAV.getnframes()
        
        WAV.setpos(0)
        L=[]
        for i in range(N) :
                valeur=int(binascii.hexlify(WAV.readframes(1)),16)
                L.append(valeur)
        return L     


####################################################################################

############## Signal Operation ####################################################
def norm(L) :
        norm=0
        for i in range(len(L)) :
                norm += L[i]**2
        return math.sqrt(norm)
 


def innerProduct(signal1,signal2) :
        M = min(len(signal1),len(signal2))
        innerProduct = 0
        for i in range(M) :
                innerProduct+=signal1[i]*signal2[i]
        return innerProduct

def covariance(signal1,signal2) :
        return float(innerProduct(signal1,signal2))/(norm(signal1)*norm(signal2))
#######################################################################################
#L1=getSignalfromData(getDataFromWav("Sons/REF1.wav"))
#L2=getSignalfromWav("Sons/REF2.wav")
#print covariance(L1,L2) 


