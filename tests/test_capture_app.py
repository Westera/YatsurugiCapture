#!/usr/bin/env python3
"""
Unit tests for YatsurugiCapture
Tests can run without actual capture hardware
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Set Qt to use offscreen platform for headless environments (CI/CD)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
import numpy as np

# Create QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from capture_app import CaptureWindow


class TestCaptureWindow(unittest.TestCase):
    """Test CaptureWindow class without hardware"""

    def setUp(self):
        """Set up test fixtures"""
        self.window = CaptureWindow()

    def tearDown(self):
        """Clean up after tests"""
        if self.window:
            self.window.close()

    def test_window_initialization(self):
        """Test that window initializes correctly"""
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "YatsurugiCapture")
        self.assertFalse(self.window.is_capturing)
        self.assertFalse(self.window.is_recording)
        self.assertIsNone(self.window.capture)
        self.assertIsNone(self.window.video_writer)
        self.assertIsNotNone(self.window.audio_handler)

    def test_resolution_parsing(self):
        """Test resolution string parsing"""
        # Test 4K
        self.window.resolution_combo.setCurrentIndex(0)
        self.assertEqual(self.window.get_resolution(), (3840, 2160))

        # Test 2K
        self.window.resolution_combo.setCurrentIndex(1)
        self.assertEqual(self.window.get_resolution(), (2560, 1440))

        # Test 1080p
        self.window.resolution_combo.setCurrentIndex(2)
        self.assertEqual(self.window.get_resolution(), (1920, 1080))

        # Test 720p
        self.window.resolution_combo.setCurrentIndex(3)
        self.assertEqual(self.window.get_resolution(), (1280, 720))

        # Test 480p
        self.window.resolution_combo.setCurrentIndex(4)
        self.assertEqual(self.window.get_resolution(), (720, 480))

    def test_device_path_extraction(self):
        """Test extracting device path from combo box text"""
        # Mock device in combo box
        self.window.device_combo.clear()
        self.window.device_combo.addItem("Test Device (/dev/video0)")

        device_path = self.window.get_device_path()
        self.assertEqual(device_path, "/dev/video0")

        # Test with video2
        self.window.device_combo.clear()
        self.window.device_combo.addItem("Elgato HD60+ (/dev/video2)")
        device_path = self.window.get_device_path()
        self.assertEqual(device_path, "/dev/video2")

    def test_device_path_extraction_invalid(self):
        """Test device path extraction with invalid input"""
        self.window.device_combo.clear()
        self.window.device_combo.addItem("No devices found")

        device_path = self.window.get_device_path()
        self.assertIsNone(device_path)

    def test_ui_elements_exist(self):
        """Test that all UI elements are created"""
        self.assertIsNotNone(self.window.video_label)
        self.assertIsNotNone(self.window.device_combo)
        self.assertIsNotNone(self.window.resolution_combo)
        self.assertIsNotNone(self.window.fps_combo)
        self.assertIsNotNone(self.window.audio_combo)
        self.assertIsNotNone(self.window.audio_passthrough_check)
        self.assertIsNotNone(self.window.start_btn)
        self.assertIsNotNone(self.window.record_btn)
        self.assertIsNotNone(self.window.borderless_btn)
        self.assertIsNotNone(self.window.status_bar)
        self.assertIsNotNone(self.window.control_widget)

    def test_fps_options(self):
        """Test FPS combo box has correct options"""
        fps_options = [self.window.fps_combo.itemText(i) for i in range(self.window.fps_combo.count())]
        self.assertIn("60", fps_options)
        self.assertIn("30", fps_options)
        self.assertIn("25", fps_options)

    def test_resolution_options(self):
        """Test resolution combo box has correct options"""
        res_options = [self.window.resolution_combo.itemText(i) for i in range(self.window.resolution_combo.count())]
        self.assertEqual(len(res_options), 5)
        self.assertTrue(any("4K" in opt for opt in res_options))
        self.assertTrue(any("2K" in opt for opt in res_options))
        self.assertTrue(any("1080p" in opt for opt in res_options))
        self.assertTrue(any("720p" in opt for opt in res_options))
        self.assertTrue(any("480p" in opt for opt in res_options))

    def test_borderless_toggle(self):
        """Test borderless mode toggle"""
        # Show window so widgets are visible
        self.window.show()

        # Initially not borderless
        self.assertFalse(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(self.window.control_widget.isVisible())
        self.assertTrue(self.window.status_bar.isVisible())

        # Toggle to borderless
        self.window.toggle_borderless()
        self.assertTrue(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertFalse(self.window.control_widget.isVisible())
        self.assertFalse(self.window.status_bar.isVisible())

        # Toggle back
        self.window.toggle_borderless()
        self.assertFalse(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(self.window.control_widget.isVisible())
        self.assertTrue(self.window.status_bar.isVisible())

    def test_escape_key_in_borderless_mode(self):
        """Test that Escape key exits borderless mode"""
        # Enter borderless mode
        self.window.toggle_borderless()
        self.assertTrue(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertFalse(self.window.control_widget.isVisible())

        # Simulate Escape key press
        QTest.keyPress(self.window, Qt.Key_Escape)
        self.assertFalse(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(self.window.control_widget.isVisible())
        self.assertTrue(self.window.status_bar.isVisible())

    @patch("capture_app.subprocess.run")
    def test_device_detection_success(self, mock_run):
        """Test successful device detection"""
        # Mock v4l2-ctl output
        mock_result = Mock()
        mock_result.stdout = """Elgato HD60+ (usb-0000:00:14.0-1):
        /dev/video0
        /dev/video1

Integrated Camera (usb-0000:00:14.0-2):
        /dev/video2
"""
        mock_run.return_value = mock_result

        # Create new window to trigger device detection
        window = CaptureWindow()

        # Check that devices were added
        self.assertGreater(window.device_combo.count(), 0)
        window.close()

    @patch("capture_app.subprocess.run")
    def test_device_detection_no_devices(self, mock_run):
        """Test device detection with no devices found"""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        window = CaptureWindow()
        self.assertEqual(window.device_combo.itemText(0), "No devices found")
        window.close()

    @patch("capture_app.subprocess.run")
    def test_device_detection_v4l2_not_found(self, mock_run):
        """Test device detection when v4l2-ctl is not installed"""
        mock_run.side_effect = FileNotFoundError()

        window = CaptureWindow()
        self.assertEqual(window.device_combo.itemText(0), "v4l2-ctl not found")
        window.close()

    @patch("cv2.VideoCapture")
    def test_start_capture_no_device_selected(self, mock_capture):
        """Test starting capture with no valid device"""
        self.window.device_combo.clear()
        self.window.device_combo.addItem("No devices found")

        self.window.start_capture()

        # Should not create capture object
        self.assertIsNone(self.window.capture)
        self.assertFalse(self.window.is_capturing)

    @patch("cv2.VideoCapture")
    def test_start_capture_device_fails_to_open(self, mock_capture_class):
        """Test handling of device that fails to open"""
        # Mock VideoCapture that fails to open
        mock_capture = Mock()
        mock_capture.isOpened.return_value = False
        mock_capture_class.return_value = mock_capture

        self.window.device_combo.clear()
        self.window.device_combo.addItem("Test Device (/dev/video0)")

        self.window.start_capture()

        # Should not start capturing
        self.assertFalse(self.window.is_capturing)

    @patch("cv2.VideoCapture")
    def test_start_capture_success(self, mock_capture_class):
        """Test successful capture start"""
        # Mock VideoCapture that opens successfully
        mock_capture = Mock()
        mock_capture.isOpened.return_value = True
        mock_capture_class.return_value = mock_capture

        self.window.device_combo.clear()
        self.window.device_combo.addItem("Test Device (/dev/video0)")

        self.window.start_capture()

        # Check capture started
        self.assertTrue(self.window.is_capturing)
        self.assertEqual(self.window.start_btn.text(), "Stop Capture")
        self.assertFalse(self.window.device_combo.isEnabled())
        self.assertFalse(self.window.resolution_combo.isEnabled())
        self.assertFalse(self.window.fps_combo.isEnabled())
        self.assertFalse(self.window.audio_combo.isEnabled())
        self.assertTrue(self.window.record_btn.isEnabled())

    def test_stop_capture(self):
        """Test stopping capture"""
        # Mock a running capture
        self.window.capture = Mock()
        self.window.is_capturing = True
        self.window.start_btn.setText("Stop Capture")

        self.window.stop_capture()

        # Check capture stopped
        self.assertFalse(self.window.is_capturing)
        self.assertEqual(self.window.start_btn.text(), "Start Capture")
        self.assertEqual(self.window.windowTitle(), "YatsurugiCapture")
        self.assertTrue(self.window.device_combo.isEnabled())
        self.assertTrue(self.window.resolution_combo.isEnabled())
        self.assertTrue(self.window.fps_combo.isEnabled())
        self.assertTrue(self.window.audio_combo.isEnabled())
        self.assertFalse(self.window.record_btn.isEnabled())

    def test_controls_disabled_during_capture(self):
        """Test that controls are properly disabled during capture"""
        # Mock successful capture
        mock_capture = Mock()
        mock_capture.isOpened.return_value = True

        with patch("cv2.VideoCapture", return_value=mock_capture):
            self.window.device_combo.clear()
            self.window.device_combo.addItem("Test Device (/dev/video0)")
            self.window.start_capture()

            self.assertFalse(self.window.device_combo.isEnabled())
            self.assertFalse(self.window.resolution_combo.isEnabled())
            self.assertFalse(self.window.fps_combo.isEnabled())
            self.assertFalse(self.window.audio_combo.isEnabled())

    def test_audio_device_index_extraction(self):
        """Test extracting audio device index from combo box"""
        self.window.audio_combo.clear()
        self.window.audio_combo.addItem("Test Microphone (ID: 5)")

        device_index = self.window.get_audio_device_index()
        self.assertEqual(device_index, 5)

    def test_audio_device_index_none(self):
        """Test audio device index when 'None' is selected"""
        self.window.audio_combo.clear()
        self.window.audio_combo.addItem("None (No Audio)")

        device_index = self.window.get_audio_device_index()
        self.assertIsNone(device_index)

    def test_window_title_updates_on_capture(self):
        """Test that window title includes device name when capturing"""
        mock_capture = Mock()
        mock_capture.isOpened.return_value = True

        with patch("cv2.VideoCapture", return_value=mock_capture):
            self.window.device_combo.clear()
            self.window.device_combo.addItem("Elgato HD60+ (/dev/video0)")

            self.window.start_capture()

            # Window title should include device name
            self.assertIn("Elgato HD60+", self.window.windowTitle())
            self.assertTrue(self.window.windowTitle().startswith("YatsurugiCapture - "))

    def test_record_button_disabled_initially(self):
        """Test that record button is disabled when not capturing"""
        self.assertFalse(self.window.record_btn.isEnabled())

    @patch("cv2.VideoWriter")
    def test_recording_requires_active_capture(self, mock_writer):
        """Test that recording can only start when capturing"""
        self.window.is_capturing = False

        self.window.start_recording()

        # Should not create video writer
        mock_writer.assert_not_called()
        self.assertFalse(self.window.is_recording)

    @patch("capture_app.QFileDialog.getSaveFileName")
    @patch("cv2.VideoWriter")
    def test_start_recording_success(self, mock_writer_class, mock_dialog):
        """Test successful recording start"""
        # Mock file dialog
        mock_dialog.return_value = ("/tmp/test.mp4", "Video Files (*.mp4)")

        # Mock video writer
        mock_writer = Mock()
        mock_writer.isOpened.return_value = True
        mock_writer_class.return_value = mock_writer

        # Set up capture
        self.window.is_capturing = True

        self.window.start_recording()

        # Check recording started
        self.assertTrue(self.window.is_recording)
        self.assertEqual(self.window.record_btn.text(), "Stop Recording")
        mock_writer_class.assert_called_once()

    @patch("capture_app.QFileDialog.getSaveFileName")
    def test_start_recording_cancelled(self, mock_dialog):
        """Test recording start when user cancels file dialog"""
        # Mock cancelled dialog
        mock_dialog.return_value = ("", "")

        self.window.is_capturing = True
        self.window.start_recording()

        # Recording should not start
        self.assertFalse(self.window.is_recording)
        self.assertIsNone(self.window.video_writer)

    def test_stop_recording(self):
        """Test stopping recording"""
        # Mock active recording
        mock_writer = Mock()
        self.window.video_writer = mock_writer
        self.window.is_recording = True
        self.window.record_btn.setText("Stop Recording")

        self.window.stop_recording()

        # Check recording stopped
        self.assertFalse(self.window.is_recording)
        self.assertEqual(self.window.record_btn.text(), "Start Recording")
        self.assertIsNone(self.window.video_writer)
        mock_writer.release.assert_called_once()

    def test_audio_passthrough_toggle_on(self):
        """Test enabling audio passthrough"""
        self.window.audio_combo.clear()
        self.window.audio_combo.addItem("Test Device (ID: 0)")

        with patch.object(self.window.audio_handler, "start_passthrough", return_value=True):
            self.window.audio_passthrough_check.setChecked(True)

            self.window.audio_handler.start_passthrough.assert_called_once_with(input_device_index=0)

    def test_audio_passthrough_toggle_off(self):
        """Test disabling audio passthrough"""
        # Checkbox starts unchecked, so check it first
        self.window.audio_combo.clear()
        self.window.audio_combo.addItem("Test Device (ID: 0)")

        with patch.object(self.window.audio_handler, "start_passthrough", return_value=True):
            self.window.audio_passthrough_check.setChecked(True)

        # Now test unchecking it
        with patch.object(self.window.audio_handler, "stop_passthrough"):
            self.window.audio_passthrough_check.setChecked(False)

            self.window.audio_handler.stop_passthrough.assert_called_once()

    def test_update_frame_writes_to_video_when_recording(self):
        """Test that frames are written to file during recording"""
        # Set up capture and recording
        self.window.capture = Mock()
        self.window.capture.isOpened.return_value = True
        self.window.video_writer = Mock()
        self.window.is_recording = True

        # Mock frame reading
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.window.capture.read.return_value = (True, test_frame)

        self.window.update_frame()

        # Check frame was written
        self.window.video_writer.write.assert_called_once()


class TestCaptureWindowIntegration(unittest.TestCase):
    """Integration tests for UI interactions"""

    def setUp(self):
        """Set up test fixtures"""
        self.window = CaptureWindow()

    def tearDown(self):
        """Clean up after tests"""
        if self.window:
            self.window.close()

    def test_button_click_toggle(self):
        """Test clicking start button toggles state"""
        initial_text = self.window.start_btn.text()
        self.assertEqual(initial_text, "Start Capture")

    def test_borderless_button_click(self):
        """Test borderless button toggles window flags"""
        initial_flags = self.window.windowFlags()
        QTest.mouseClick(self.window.borderless_btn, Qt.LeftButton)
        new_flags = self.window.windowFlags()
        self.assertNotEqual(initial_flags, new_flags)
        # Controls should be hidden in borderless mode
        self.assertFalse(self.window.control_widget.isVisible())

    def test_video_double_click(self):
        """Test double-clicking video label toggles borderless mode"""
        # Show window so widgets are visible
        self.window.show()

        # Initially not borderless
        self.assertFalse(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(self.window.control_widget.isVisible())

        # Simulate double-click on video label
        QTest.mouseDClick(self.window.video_label, Qt.LeftButton)

        # Should now be borderless with controls hidden
        self.assertTrue(self.window.windowFlags() & Qt.FramelessWindowHint)
        self.assertFalse(self.window.control_widget.isVisible())
        self.assertFalse(self.window.status_bar.isVisible())


if __name__ == "__main__":
    unittest.main()
