#!/usr/bin/env python3
"""Day 29: ROS 2 voice command node (offline, Vosk).
Publishes:
  /voice/command  std_msgs/String  clean command, e.g. "take off", "land", "stop"
  /voice/heard    std_msgs/String  raw recognised text (for logging)
Repeats of the same command within DEBOUNCE_S are ignored.
Usage: voice_commander.py [gain]   (default 3.0)"""
import audioop, json, os, subprocess, sys, threading, time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from vosk import Model, KaldiRecognizer, SetLogLevel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voice_listen import to_command, MODEL, RATE   # one keyword list (Day 28)

DEBOUNCE_S = 2.0


class VoiceCommander(Node):
    def __init__(self, gain):
        super().__init__('voice_commander')
        self.pub_cmd = self.create_publisher(String, '/voice/command', 10)
        self.pub_heard = self.create_publisher(String, '/voice/heard', 10)
        self.gain = gain
        self.last_cmd, self.last_t = None, 0.0
        SetLogLevel(-1)
        self.rec = KaldiRecognizer(Model(MODEL), RATE)
        self.mic = subprocess.Popen(
            ['parec', '--format=s16le', f'--rate={RATE}', '--channels=1'],
            stdout=subprocess.PIPE)
        self.running = True
        threading.Thread(target=self.listen, daemon=True).start()
        self.get_logger().info(f'listening (gain {gain}); publishing /voice/command')

    def listen(self):
        while self.running:
            data = self.mic.stdout.read(4000)
            if not data:
                break
            data = audioop.mul(data, 2, self.gain)
            if not self.rec.AcceptWaveform(data):
                continue
            text = json.loads(self.rec.Result())['text'].strip()
            if not text:
                continue
            self.pub_heard.publish(String(data=text))
            cmd = to_command(text)
            if cmd is None:
                self.get_logger().info(f'heard "{text}" -> no command')
                continue
            now = time.time()
            if cmd == self.last_cmd and now - self.last_t < DEBOUNCE_S:
                self.get_logger().info(f'heard "{text}" -> {cmd} (repeat, ignored)')
                continue
            self.last_cmd, self.last_t = cmd, now
            self.pub_cmd.publish(String(data=cmd))
            self.get_logger().info(f'heard "{text}" -> COMMAND: {cmd}')

    def destroy_node(self):
        self.running = False
        self.mic.terminate()
        super().destroy_node()


def main():
    gain = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    rclpy.init()
    node = VoiceCommander(gain)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
