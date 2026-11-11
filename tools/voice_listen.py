#!/usr/bin/env python3
"""Day 28: live offline voice recognition (Vosk), limited to drone commands.
Audio comes from WSLg PulseAudio via `parec` (16 kHz, mono, 16-bit)."""
import json, os, subprocess
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)
MODEL = os.path.expanduser('~/vosk_models/vosk-model-small-en-us-0.15')
RATE = 16000
COMMANDS = ['take off', 'land', 'stop', 'hover',
            'go behind the wall', 'go past the rock', 'go home']

rec = KaldiRecognizer(Model(MODEL), RATE, json.dumps(COMMANDS + ['[unk]']))
mic = subprocess.Popen(['parec', '--format=s16le', f'--rate={RATE}', '--channels=1'],
                       stdout=subprocess.PIPE)
print('listening... say one of:', ', '.join(COMMANDS), '(Ctrl+C to quit)')
try:
    while True:
        data = mic.stdout.read(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result())['text'].strip()
            if text and text != '[unk]':
                print('COMMAND:', text)
except KeyboardInterrupt:
    pass
finally:
    mic.terminate()
