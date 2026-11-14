#!/usr/bin/env python3
"""Day 28: live offline voice commands with Vosk.
Free-text recognition + whole-word keyword matching (more tolerant than a fixed grammar).
Audio: WSLg PulseAudio via `parec` (16 kHz mono 16-bit), with software gain.
Usage: voice_listen.py [gain]   (default gain 3.0)"""
import audioop, json, os, re, subprocess, sys
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)
MODEL = os.path.expanduser('~/vosk_models/vosk-model-small-en-us-0.15')
RATE = 16000
GAIN = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0

# Checked in this order: safety commands first. Includes common mishearings
# of the small Vosk model (found in Day 28 testing).
KEYWORDS = [
    ('stop',               ['stop', 'abort', 'halt']),
    ('land',               ['land', 'landing', 'learned', 'lang']),
    ('take off',           ['take off', 'takeoff', 'take of']),
    ('hover',              ['hover', 'hold', 'stay', 'howard', 'however']),
    ('go behind the wall', ['wall', 'behind']),
    ('go past the rock',   ['rock', 'past']),
    ('go home',            ['home']),
]

def to_command(text):
    for cmd, words in KEYWORDS:
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', text):
                return cmd
    return None

if __name__ == '__main__':
    rec = KaldiRecognizer(Model(MODEL), RATE)
    mic = subprocess.Popen(['parec', '--format=s16le', f'--rate={RATE}', '--channels=1'],
                           stdout=subprocess.PIPE)
    print(f'listening (gain {GAIN})... say: take off, hover/hold, go behind the wall, '
          'go past the rock, go home, land, stop   (Ctrl+C to quit)')
    try:
        while True:
            data = mic.stdout.read(4000)
            if not data:
                break
            data = audioop.mul(data, 2, GAIN)          # boost quiet microphones
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())['text'].strip()
                if not text:
                    continue
                cmd = to_command(text)
                print(f'heard: "{text}"  ->  ' + (f'COMMAND: {cmd}' if cmd else 'no command'))
    except KeyboardInterrupt:
        pass
    finally:
        mic.terminate()
