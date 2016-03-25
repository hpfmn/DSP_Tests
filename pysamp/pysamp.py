#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import jack
import soundfile
import time
import mido

MIDI_DEVICE='nanoKEY2 MIDI 1'

class sampler:
    def __init__(self, sample, keynote):
        self.note=0
        self.playpos=0
        self.playstep=0
        self.keynote=keynote
        self.sample=sample
    def getSamples(self, size):
        out_buffer=numpy.zeros((1,size),'f')
        if self.note==0:
            return out_buffer
        for i in range(size):
            if(int(self.playpos)>=len(self.sample)):
                self.playpos=0
            out_buffer[0,i]=self.sample[int(self.playpos)]
            self.playpos+=self.playstep
        return out_buffer
    def setNote(self, note):
        print("got note ", note)
        semitones=note-self.keynote
        self.note=note
        self.playstep=2**(semitones/12.0)
        self.playpos=0
    def stopNote(self,note):
        if note==self.note:
            self.note=0
            self.playpos=0
            self.playstep=0

jack.attach("pysampl")
jack.register_port("out_1", jack.IsOutput)
jack.register_port("in_1", jack.IsInput)
jack.activate()
jack.connect("pysampl:out_1", "system:playback_1")
jack.connect("pysampl:out_1", "system:playback_2")

N = jack.get_buffer_size()
Sr = float(jack.get_sample_rate())
input_buf = numpy.zeros((1,N), 'f')

output, samplerate = soundfile.read('Sample.wav')
output = 0.225*output/numpy.max(output)

mysampl = sampler(output, 60)

midiOut = mido.open_input(MIDI_DEVICE)

def handleMidi(msg):
   if msg.type=='note_on':
       if msg.velocity==0:
           mysampl.stopNote(msg.note)
       else:
           mysampl.setNote(msg.note)
   if msg.type=='note_off':
       mysampl.stopNote(msg.note)

midiOut.callback = handleMidi

try:
    while True:
        try:
            out_buffer = mysampl.getSamples(N)
            jack.process(out_buffer, input_buf)
        except jack.InputSyncError:
            print("InputSyncErro")
        except jack.OutputSyncError:
            print("OuputSyncErro")
except KeyboardInterrupt:
    print('exeting...')
finally:
    jack.deactivate() 
    jack.detach()
