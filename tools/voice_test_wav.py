#!/usr/bin/env python3
"""Day 28: recognise speech in a 16 kHz mono WAV file with Vosk (offline)."""
import json, sys, wave, os
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)
MODEL = os.path.expanduser('~/vosk_models/vosk-model-small-en-us-0.15')
wf = wave.open(sys.argv[1], 'rb')
rec = KaldiRecognizer(Model(MODEL), wf.getframerate())
while True:
    data = wf.readframes(4000)
    if not data:
        break
    if rec.AcceptWaveform(data):
        print('heard:', json.loads(rec.Result())['text'])
print('heard:', json.loads(rec.FinalResult())['text'])
