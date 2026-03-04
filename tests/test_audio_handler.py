#!/usr/bin/env python3
"""
Unit tests for AudioHandler
Tests can run without actual audio hardware
"""

import unittest
from unittest.mock import Mock, patch
from audio_handler import AudioHandler


class TestAudioHandler(unittest.TestCase):
    """Test AudioHandler class without hardware"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("audio_handler.pyaudio.PyAudio"):
            self.handler = AudioHandler()
            self.handler.input_stream = None
            self.handler.output_stream = None

    def tearDown(self):
        """Clean up after tests"""
        if self.handler:
            self.handler.cleanup()

    def test_initialization(self):
        """Test that AudioHandler initializes correctly"""
        self.assertIsNotNone(self.handler)
        self.assertIsNone(getattr(self.handler, 'input_stream', None))
        self.assertIsNone(getattr(self.handler, 'output_stream', None))
        self.assertFalse(self.handler.is_running)
        self.assertIsNone(self.handler.thread)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_list_devices(self, mock_pyaudio_class):
        """Test listing audio devices"""
        # Mock PyAudio instance
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 3

        # Mock device info
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Built-in Microphone", "maxInputChannels": 2, "defaultSampleRate": 44100.0},
            {"name": "Built-in Speaker", "maxInputChannels": 0, "defaultSampleRate": 44100.0},  # Output only
            {"name": "Elgato HD60+", "maxInputChannels": 2, "defaultSampleRate": 48000.0},
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        devices = handler.list_devices()

        # Should only return devices with input channels
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["name"], "Built-in Microphone")
        self.assertEqual(devices[1]["name"], "Elgato HD60+")

    @patch("audio_handler.pyaudio.PyAudio")
    def test_find_capture_card_audio_found(self, mock_pyaudio_class):
        """Test finding capture card audio device"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2

        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Built-in Microphone", "maxInputChannels": 2, "defaultSampleRate": 44100.0},
            {"name": "Elgato HD60+ Game Capture", "maxInputChannels": 2, "defaultSampleRate": 48000.0},
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        device_index = handler.find_capture_card_audio()

        # Should find the Elgato device at index 1
        self.assertEqual(device_index, 1)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_find_capture_card_audio_not_found(self, mock_pyaudio_class):
        """Test when capture card audio is not found"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1

        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Built-in Microphone", "maxInputChannels": 2, "defaultSampleRate": 44100.0}
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        device_index = handler.find_capture_card_audio()

        # Should return None when not found
        self.assertIsNone(device_index)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_success(self, mock_pyaudio_class):
        """Test successful audio passthrough start"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return mock_input_stream
            if kwargs.get("output"):
                return mock_output_stream
        mock_audio.open.side_effect = open_side_effect
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True},
        ]
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)
        self.assertTrue(result)
        self.assertTrue(handler.is_running)
        self.assertIs(handler.input_stream, mock_input_stream)
        self.assertIs(handler.output_stream, mock_output_stream)
        handler.stop_passthrough()

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_already_running(self, mock_pyaudio_class):
        """Test starting passthrough when already running"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        handler.is_running = True

        result = handler.start_passthrough(input_device_index=0)

        # Should return False when already running
        self.assertFalse(result)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_auto_detect(self, mock_pyaudio_class):
        """Test auto-detection of capture card when no device specified"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        # Provide both input and output devices with correct properties
        def get_device_info_by_index(idx):
            if idx == 0:
                return {"name": "Elgato Capture", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0}
            if idx == 1:
                return {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True}
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = get_device_info_by_index
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return mock_input_stream
            if kwargs.get("output"):
                return mock_output_stream
        mock_audio.open.side_effect = open_side_effect
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        result = handler.start_passthrough()
        self.assertTrue(result)
        self.assertTrue(handler.is_running)
        handler.stop_passthrough()

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_auto_detect_not_found(self, mock_pyaudio_class):
        """Test auto-detection when capture card not found"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1
        mock_audio.get_device_info_by_index.return_value = {
            "name": "Built-in Mic",
            "maxInputChannels": 2,
            "defaultSampleRate": 44100.0,
        }

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        result = handler.start_passthrough()

        # Should fail when device not found
        self.assertFalse(result)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_exception(self, mock_pyaudio_class):
        """Test handling of exception during passthrough start"""
        mock_audio = Mock()
        mock_audio.open.side_effect = Exception("Audio device error")

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)

        # Should return False on exception
        self.assertFalse(result)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_stop_passthrough(self, mock_pyaudio_class):
        """Test stopping audio passthrough"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        handler.input_stream = mock_input_stream
        handler.output_stream = mock_output_stream
        handler.is_running = True
        handler.stop_passthrough()
        mock_input_stream.stop_stream.assert_called_once()
        mock_input_stream.close.assert_called_once()
        mock_output_stream.stop_stream.assert_called_once()
        mock_output_stream.close.assert_called_once()
        self.assertIsNone(handler.input_stream)
        self.assertIsNone(handler.output_stream)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_stop_passthrough_no_stream(self, mock_pyaudio_class):
        """Test stopping when no stream exists"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        handler.input_stream = None
        handler.output_stream = None
        handler.is_running = False
        # Should not raise exception
        handler.stop_passthrough()
        self.assertIsNone(handler.input_stream)
        self.assertIsNone(handler.output_stream)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.subprocess.run")
    @patch("audio_handler.pyaudio.PyAudio")
    def test_get_pulse_sources_success(self, mock_pyaudio_class, mock_run):
        """Test getting PulseAudio sources"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio

        # Mock pactl output
        mock_result = Mock()
        mock_result.stdout = """0\talsa_input.pci-0000_00_1f.3.analog-stereo
1\talsa_input.usb-Elgato_Elgato_HD60_S.analog-stereo
"""
        mock_run.return_value = mock_result

        handler = AudioHandler()
        sources = handler.get_pulse_sources()

        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["index"], "0")
        self.assertIn("alsa_input", sources[0]["name"])
        self.assertEqual(sources[1]["index"], "1")
        self.assertIn("Elgato", sources[1]["name"])

    @patch("audio_handler.subprocess.run")
    @patch("audio_handler.pyaudio.PyAudio")
    def test_get_pulse_sources_exception(self, mock_pyaudio_class, mock_run):
        """Test handling exception when getting PulseAudio sources"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio
        mock_run.side_effect = Exception("pactl not found")

        handler = AudioHandler()
        sources = handler.get_pulse_sources()

        # Should return empty list on exception
        self.assertEqual(sources, [])

    @patch("audio_handler.pyaudio.PyAudio")
    def test_cleanup(self, mock_pyaudio_class):
        """Test cleanup method"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        handler.input_stream = mock_input_stream
        handler.output_stream = mock_output_stream
        handler.is_running = True
        handler.cleanup()
        mock_input_stream.stop_stream.assert_called_once()
        mock_input_stream.close.assert_called_once()
        mock_output_stream.stop_stream.assert_called_once()
        mock_output_stream.close.assert_called_once()
        mock_audio.terminate.assert_called_once()
        self.assertIsNone(handler.input_stream)
        self.assertIsNone(handler.output_stream)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_opens_input_and_output_streams(self, mock_pyaudio_class):
        """Test that both input and output streams are opened with correct parameters"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        # Simulate two devices: input and output
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True},
        ]
        # Simulate open returns
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return mock_input_stream
            if kwargs.get("output"):
                return mock_output_stream
        mock_audio.open.side_effect = open_side_effect
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)
        self.assertTrue(result)
        self.assertTrue(handler.is_running)
        self.assertIs(handler.input_stream, mock_input_stream)
        self.assertIs(handler.output_stream, mock_output_stream)
        handler.stop_passthrough()

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_no_output_device(self, mock_pyaudio_class):
        """Test passthrough fails if no output device is found"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1
        mock_audio.get_device_info_by_index.return_value = {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0}
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)
        self.assertFalse(result)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_start_passthrough_output_open_failure(self, mock_pyaudio_class):
        """Test passthrough fails if output stream cannot be opened"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True},
        ]
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return Mock()
            if kwargs.get("output"):
                raise Exception("Output open failed")
        mock_audio.open.side_effect = open_side_effect
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)
        self.assertFalse(result)
        self.assertFalse(handler.is_running)

    @patch("audio_handler.pyaudio.PyAudio")
    def test_passthrough_thread_error_sets_not_running(self, mock_pyaudio_class):
        """Test that an exception in the passthrough thread sets is_running to False"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        mock_input_stream.read.side_effect = Exception("Read error")
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True},
        ]
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return mock_input_stream
            if kwargs.get("output"):
                return mock_output_stream
        mock_audio.open.side_effect = open_side_effect
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        handler.start_passthrough(input_device_index=0)
        import time
        time.sleep(0.1)  # Let thread run
        self.assertFalse(handler.is_running)
        handler.stop_passthrough()

    @patch("audio_handler.pyaudio.PyAudio")
    def test_cleanup_closes_both_streams_and_thread(self, mock_pyaudio_class):
        """Test cleanup closes both input and output streams and resets thread"""
        mock_audio = Mock()
        mock_input_stream = Mock()
        mock_output_stream = Mock()
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {"name": "Elgato HD60X", "maxInputChannels": 2, "maxOutputChannels": 0, "defaultSampleRate": 48000.0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 48000.0, "defaultOutputDevice": True},
        ]
        def open_side_effect(*args, **kwargs):
            if kwargs.get("input"):
                return mock_input_stream
            if kwargs.get("output"):
                return mock_output_stream
        mock_audio.open.side_effect = open_side_effect
        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()
        handler.start_passthrough(input_device_index=0)
        handler.cleanup()
        mock_input_stream.stop_stream.assert_called()
        mock_input_stream.close.assert_called()
        mock_output_stream.stop_stream.assert_called()
        mock_output_stream.close.assert_called()
        mock_audio.terminate.assert_called()
        self.assertIsNone(getattr(handler, 'input_stream', None))
        self.assertIsNone(getattr(handler, 'output_stream', None))
        self.assertIsNone(handler.thread)


if __name__ == "__main__":
    unittest.main()
