#!/usr/bin/env python3
"""
Unit tests for AudioHandler
Tests can run without actual audio hardware
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from audio_handler import AudioHandler


class TestAudioHandler(unittest.TestCase):
    """Test AudioHandler class without hardware"""

    def setUp(self):
        """Set up test fixtures"""
        with patch('audio_handler.pyaudio.PyAudio'):
            self.handler = AudioHandler()

    def tearDown(self):
        """Clean up after tests"""
        if self.handler:
            self.handler.cleanup()

    def test_initialization(self):
        """Test that AudioHandler initializes correctly"""
        self.assertIsNotNone(self.handler)
        self.assertIsNone(self.handler.stream)
        self.assertFalse(self.handler.is_running)
        self.assertIsNone(self.handler.thread)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_list_devices(self, mock_pyaudio_class):
        """Test listing audio devices"""
        # Mock PyAudio instance
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 3

        # Mock device info
        mock_audio.get_device_info_by_index.side_effect = [
            {
                'name': 'Built-in Microphone',
                'maxInputChannels': 2,
                'defaultSampleRate': 44100.0
            },
            {
                'name': 'Built-in Speaker',
                'maxInputChannels': 0,  # Output only
                'defaultSampleRate': 44100.0
            },
            {
                'name': 'Elgato HD60+',
                'maxInputChannels': 2,
                'defaultSampleRate': 48000.0
            }
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        devices = handler.list_devices()

        # Should only return devices with input channels
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]['name'], 'Built-in Microphone')
        self.assertEqual(devices[1]['name'], 'Elgato HD60+')

    @patch('audio_handler.pyaudio.PyAudio')
    def test_find_capture_card_audio_found(self, mock_pyaudio_class):
        """Test finding capture card audio device"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2

        mock_audio.get_device_info_by_index.side_effect = [
            {
                'name': 'Built-in Microphone',
                'maxInputChannels': 2,
                'defaultSampleRate': 44100.0
            },
            {
                'name': 'Elgato HD60+ Game Capture',
                'maxInputChannels': 2,
                'defaultSampleRate': 48000.0
            }
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        device_index = handler.find_capture_card_audio()

        # Should find the Elgato device at index 1
        self.assertEqual(device_index, 1)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_find_capture_card_audio_not_found(self, mock_pyaudio_class):
        """Test when capture card audio is not found"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1

        mock_audio.get_device_info_by_index.side_effect = [
            {
                'name': 'Built-in Microphone',
                'maxInputChannels': 2,
                'defaultSampleRate': 44100.0
            }
        ]

        mock_pyaudio_class.return_value = mock_audio
        handler = AudioHandler()

        device_index = handler.find_capture_card_audio()

        # Should return None when not found
        self.assertIsNone(device_index)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_start_passthrough_success(self, mock_pyaudio_class):
        """Test successful audio passthrough start"""
        mock_audio = Mock()
        mock_stream = Mock()
        mock_stream.start_stream.return_value = None

        mock_audio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        result = handler.start_passthrough(input_device_index=0)

        self.assertTrue(result)
        self.assertTrue(handler.is_running)
        self.assertIsNotNone(handler.stream)
        mock_stream.start_stream.assert_called_once()

    @patch('audio_handler.pyaudio.PyAudio')
    def test_start_passthrough_already_running(self, mock_pyaudio_class):
        """Test starting passthrough when already running"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        handler.is_running = True

        result = handler.start_passthrough(input_device_index=0)

        # Should return False when already running
        self.assertFalse(result)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_start_passthrough_auto_detect(self, mock_pyaudio_class):
        """Test auto-detection of capture card when no device specified"""
        mock_audio = Mock()
        mock_stream = Mock()

        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {
                'name': 'Built-in Mic',
                'maxInputChannels': 2,
                'defaultSampleRate': 44100.0
            },
            {
                'name': 'Elgato Capture',
                'maxInputChannels': 2,
                'defaultSampleRate': 48000.0
            }
        ]
        mock_audio.open.return_value = mock_stream

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        result = handler.start_passthrough()

        # Should auto-detect and start
        self.assertTrue(result)
        self.assertTrue(handler.is_running)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_start_passthrough_auto_detect_not_found(self, mock_pyaudio_class):
        """Test auto-detection when capture card not found"""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 1
        mock_audio.get_device_info_by_index.return_value = {
            'name': 'Built-in Mic',
            'maxInputChannels': 2,
            'defaultSampleRate': 44100.0
        }

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        result = handler.start_passthrough()

        # Should fail when device not found
        self.assertFalse(result)
        self.assertFalse(handler.is_running)

    @patch('audio_handler.pyaudio.PyAudio')
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

    @patch('audio_handler.pyaudio.PyAudio')
    def test_stop_passthrough(self, mock_pyaudio_class):
        """Test stopping audio passthrough"""
        mock_audio = Mock()
        mock_stream = Mock()

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        handler.stream = mock_stream
        handler.is_running = True

        handler.stop_passthrough()

        # Check stream was stopped and closed
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        self.assertIsNone(handler.stream)
        self.assertFalse(handler.is_running)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_stop_passthrough_no_stream(self, mock_pyaudio_class):
        """Test stopping when no stream exists"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        handler.is_running = False

        # Should not raise exception
        handler.stop_passthrough()
        self.assertIsNone(handler.stream)
        self.assertFalse(handler.is_running)

    @patch('audio_handler.subprocess.run')
    @patch('audio_handler.pyaudio.PyAudio')
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
        self.assertEqual(sources[0]['index'], '0')
        self.assertIn('alsa_input', sources[0]['name'])
        self.assertEqual(sources[1]['index'], '1')
        self.assertIn('Elgato', sources[1]['name'])

    @patch('audio_handler.subprocess.run')
    @patch('audio_handler.pyaudio.PyAudio')
    def test_get_pulse_sources_exception(self, mock_pyaudio_class, mock_run):
        """Test handling exception when getting PulseAudio sources"""
        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio
        mock_run.side_effect = Exception("pactl not found")

        handler = AudioHandler()
        sources = handler.get_pulse_sources()

        # Should return empty list on exception
        self.assertEqual(sources, [])

    @patch('audio_handler.pyaudio.PyAudio')
    def test_audio_callback(self, mock_pyaudio_class):
        """Test audio callback function"""
        import pyaudio

        mock_audio = Mock()
        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()

        # Test callback
        test_data = b'test audio data'
        result, flag = handler._audio_callback(test_data, 1024, None, None)

        self.assertEqual(result, test_data)
        self.assertEqual(flag, pyaudio.paContinue)

    @patch('audio_handler.pyaudio.PyAudio')
    def test_cleanup(self, mock_pyaudio_class):
        """Test cleanup method"""
        mock_audio = Mock()
        mock_stream = Mock()

        mock_pyaudio_class.return_value = mock_audio

        handler = AudioHandler()
        handler.stream = mock_stream
        handler.is_running = True

        handler.cleanup()

        # Check everything is cleaned up
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_audio.terminate.assert_called_once()
        self.assertIsNone(handler.stream)
        self.assertFalse(handler.is_running)


if __name__ == '__main__':
    unittest.main()
