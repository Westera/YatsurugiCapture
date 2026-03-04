#!/usr/bin/env python3
"""
Audio capture and passthrough for Elgato HD60+
Handles ALSA audio input and routes it to default output
"""

import subprocess
import threading

import pyaudio


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
        """Start audio passthrough from input to output (default system output)"""
        if self.is_running:
            return False

        try:
            # Auto-detect if no device specified
            if input_device_index is None:
                input_device_index = self.find_capture_card_audio()
                if input_device_index is None:
                    print("Could not find capture card audio device")
                    return False

            # Find default output device
            output_device_index = None
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info["maxOutputChannels"] > 0 and info.get("defaultOutputDevice", False):
                    output_device_index = i
                    break
            # If not found, fallback to first output device
            if output_device_index is None:
                for i in range(self.audio.get_device_count()):
                    info = self.audio.get_device_info_by_index(i)
                    if info["maxOutputChannels"] > 0:
                        output_device_index = i
                        break
            if output_device_index is None:
                print("No output device found for audio passthrough")
                return False

            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=1024,
            )
            self.output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                output=True,
                output_device_index=output_device_index,
                frames_per_buffer=1024,
            )
            self.is_running = True
            self.thread = threading.Thread(target=self._passthrough_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Error starting audio passthrough: {e}")
            self.is_running = False
            return False

    def _passthrough_loop(self):
        try:
            while self.is_running:
                data = self.input_stream.read(1024, exception_on_overflow=False)
                self.output_stream.write(data)
        except Exception as e:
            print(f"Audio passthrough loop error: {e}")
        finally:
            self.is_running = False

    def stop_passthrough(self):
        """Stop audio passthrough"""
        self.is_running = False
        if hasattr(self, "input_stream") and self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        if hasattr(self, "output_stream") and self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        self.thread = None

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
