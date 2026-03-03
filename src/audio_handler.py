#!/usr/bin/env python3
"""
Audio capture and passthrough for Elgato HD60+
Handles ALSA audio input and routes it to default output
"""

import pyaudio
import subprocess


class AudioHandler:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        self.thread = None

    def list_devices(self):
        """List all available audio input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append(
                    {
                        "index": i,
                        "name": info["name"],
                        "channels": info["maxInputChannels"],
                        "sample_rate": int(info["defaultSampleRate"]),
                    }
                )
        return devices

    def find_capture_card_audio(self):
        """Try to find Elgato capture card audio device"""
        devices = self.list_devices()

        # Look for common Elgato device names
        keywords = ["elgato", "hd60", "capture", "game capture"]

        for device in devices:
            name_lower = device["name"].lower()
            for keyword in keywords:
                if keyword in name_lower:
                    return device["index"]

        # If not found, return None
        return None

    def start_passthrough(self, input_device_index=None, channels=2, rate=48000):
        """Start audio passthrough from input to output"""
        if self.is_running:
            return False

        try:
            # Auto-detect if no device specified
            if input_device_index is None:
                input_device_index = self.find_capture_card_audio()
                if input_device_index is None:
                    print("Could not find capture card audio device")
                    return False

            # Open input stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                output=True,
                input_device_index=input_device_index,
                frames_per_buffer=1024,
                stream_callback=self._audio_callback,
            )

            self.stream.start_stream()
            self.is_running = True

            return True

        except Exception as e:
            print(f"Error starting audio passthrough: {e}")
            return False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback to pass audio from input to output"""
        return (in_data, pyaudio.paContinue)

    def stop_passthrough(self):
        """Stop audio passthrough"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.is_running = False

    def get_pulse_sources(self):
        """Get PulseAudio sources (for systems using PulseAudio)"""
        try:
            result = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True)
            sources = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        sources.append({"index": parts[0], "name": parts[1]})
            return sources
        except:
            return []

    def cleanup(self):
        """Clean up audio resources"""
        self.stop_passthrough()
        self.audio.terminate()
