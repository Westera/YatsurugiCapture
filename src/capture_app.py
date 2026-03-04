#!/usr/bin/env python3
"""
YatsurugiCapture - Video Capture Application for Linux
Captures video and displays it in a window for Discord screen sharing
"""

import re
import subprocess
import sys
from datetime import datetime
from typing import Optional, Tuple

import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QStatusBar,
    QFileDialog,
    QCheckBox,
    QToolTip,
)

from audio_handler import AudioHandler


class CaptureWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.is_capturing = False
        self.is_recording = False
        self.video_writer = None
        self.audio_handler = AudioHandler()

        self.init_ui()
        self.detect_devices()
        self.detect_audio_devices()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("YatsurugiCapture")
        self.setGeometry(100, 100, 1280, 720)

        # Set global stylesheet with tooltip styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: black;
            }
            QToolTip {
                background-color: #ffffcc;
                color: black;
                border: 1px solid black;
                padding: 3px;
                font-size: 10pt;
            }
        """
        )

        # Set tooltip font
        QToolTip.setFont(QFont("SansSerif", 10))

        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # Video display label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(1280, 720)
        self.video_label.mouseDoubleClickEvent = self.video_double_click
        main_layout.addWidget(self.video_label)

        # Control panel widget (so we can hide it)
        self.control_widget = QWidget()
        self.control_widget.setStyleSheet("background-color: #2b2b2b; color: white;")
        control_main_layout = QVBoxLayout()
        control_main_layout.setSpacing(5)
        control_main_layout.setContentsMargins(5, 5, 5, 5)
        self.control_widget.setLayout(control_main_layout)

        # First row - Device and video settings
        row1_layout = QHBoxLayout()

        device_label = QLabel("Capture Device:")
        row1_layout.addWidget(device_label)

        self.device_combo = QComboBox()
        self.device_combo.setToolTip("Select the video capture device (e.g., capture card, webcam)")
        self.device_combo.setStatusTip("Select the video capture device (e.g., capture card, webcam)")
        row1_layout.addWidget(self.device_combo)

        res_label = QLabel("Resolution:")
        row1_layout.addWidget(res_label)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(
            ["3840x2160 (4K)", "2560x1440 (2K)", "1920x1080 (1080p)", "1280x720 (720p)", "720x480 (480p)"]
        )
        self.resolution_combo.setCurrentIndex(2)
        self.resolution_combo.setToolTip("Set the capture resolution - higher resolutions require more system resources")
        self.resolution_combo.setStatusTip("Set the capture resolution - higher resolutions require more system resources")
        row1_layout.addWidget(self.resolution_combo)

        fps_label = QLabel("FPS:")
        row1_layout.addWidget(fps_label)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["60", "30", "25"])
        self.fps_combo.setCurrentIndex(1)
        self.fps_combo.setToolTip("Set frames per second - 60 FPS for smooth motion, 30 FPS for standard capture")
        self.fps_combo.setStatusTip("Set frames per second - 60 FPS for smooth motion, 30 FPS for standard capture")
        row1_layout.addWidget(self.fps_combo)

        row1_layout.addStretch()
        control_main_layout.addLayout(row1_layout)

        # Second row - Audio settings and buttons
        row2_layout = QHBoxLayout()

        audio_label = QLabel("Audio Device:")
        row2_layout.addWidget(audio_label)

        self.audio_combo = QComboBox()
        self.audio_combo.setToolTip("Select audio input device from capture card or other source")
        self.audio_combo.setStatusTip("Select audio input device from capture card or other source")
        row2_layout.addWidget(self.audio_combo)

        self.audio_passthrough_check = QCheckBox("Audio Passthrough")
        self.audio_passthrough_check.stateChanged.connect(self.toggle_audio_passthrough)
        self.audio_passthrough_check.setToolTip("Enable to hear audio from the capture source in real-time")
        self.audio_passthrough_check.setStatusTip("Enable to hear audio from the capture source in real-time")
        row2_layout.addWidget(self.audio_passthrough_check)

        self.start_btn = QPushButton("Start Capture")
        self.start_btn.clicked.connect(self.toggle_capture)
        self.start_btn.setToolTip("Start capturing video from the selected device")
        self.start_btn.setStatusTip("Start capturing video from the selected device")
        row2_layout.addWidget(self.start_btn)

        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setEnabled(False)
        self.record_btn.setToolTip("Record the captured video to a file (requires active capture)")
        self.record_btn.setStatusTip("Record the captured video to a file (requires active capture)")
        row2_layout.addWidget(self.record_btn)

        self.borderless_btn = QPushButton("Toggle Borderless")
        self.borderless_btn.clicked.connect(self.toggle_borderless)
        self.borderless_btn.setToolTip("Toggle borderless mode for clean streaming (double-click video or press Esc to exit)")
        self.borderless_btn.setStatusTip(
            "Toggle borderless mode for clean streaming (double-click video or press Esc to exit)"
        )
        row2_layout.addWidget(self.borderless_btn)

        row2_layout.addStretch()
        control_main_layout.addLayout(row2_layout)

        main_layout.addWidget(self.control_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Select device and click Start Capture")

    def detect_devices(self):
        """Detect available V4L2 video devices"""
        try:
            # List video devices
            result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True)

            devices = []
            current_device = None

            for line in result.stdout.split("\n"):
                # Device name line (doesn't start with whitespace)
                if line and not line[0].isspace():
                    current_device = line.strip().rstrip(":")
                # Device path line (starts with whitespace)
                elif line.strip().startswith("/dev/video"):
                    device_path = line.strip()
                    if current_device:
                        devices.append(f"{current_device} ({device_path})")

            if devices:
                self.device_combo.addItems(devices)
            else:
                self.device_combo.addItem("No devices found")
                self.status_bar.showMessage("No capture devices detected!")

        except FileNotFoundError:
            self.device_combo.addItem("v4l2-ctl not found")
            self.status_bar.showMessage("Please install v4l-utils package")
        except Exception as e:
            self.device_combo.addItem(f"Error: {str(e)}")
            self.status_bar.showMessage(f"Error detecting devices: {str(e)}")

    def detect_audio_devices(self):
        """Detect available audio input devices"""
        try:
            devices = self.audio_handler.list_devices()

            if devices:
                # Add "None" option first
                self.audio_combo.addItem("None (No Audio)")

                # Add all available audio devices
                for device in devices:
                    self.audio_combo.addItem(f"{device['name']} (ID: {device['index']})")

                # Try to auto-select capture card audio
                capture_index = self.audio_handler.find_capture_card_audio()
                if capture_index is not None:
                    # Find and select this device in combo box
                    for i in range(self.audio_combo.count()):
                        if f"(ID: {capture_index})" in self.audio_combo.itemText(i):
                            self.audio_combo.setCurrentIndex(i)
                            break
            else:
                self.audio_combo.addItem("No audio devices found")

        except Exception as e:
            self.audio_combo.addItem(f"Error: {str(e)}")
            self.status_bar.showMessage(f"Error detecting audio devices: {str(e)}")

    def get_device_path(self) -> Optional[str]:
        """Extract device path from combo box selection"""
        text = self.device_combo.currentText()
        match = re.search(r"/dev/video\d+", text)
        if match:
            return match.group(0)
        return None

    def get_audio_device_index(self) -> Optional[int]:
        """Extract audio device index from combo box selection"""
        text = self.audio_combo.currentText()
        if "None" in text or "No audio" in text:
            return None
        match = re.search(r"ID: (\d+)", text)
        if match:
            return int(match.group(1))
        return None

    def get_resolution(self) -> Tuple[int, int]:
        """Get selected resolution as tuple"""
        res_text = self.resolution_combo.currentText()
        if "3840x2160" in res_text:
            return 3840, 2160
        elif "2560x1440" in res_text:
            return 2560, 1440
        elif "1920x1080" in res_text:
            return 1920, 1080
        elif "1280x720" in res_text:
            return 1280, 720
        else:
            return 720, 480

    def toggle_capture(self):
        """Start or stop video capture"""
        if not self.is_capturing:
            self.start_capture()
        else:
            self.stop_capture()

    def start_capture(self):
        """Initialize and start video capture"""
        device_path = self.get_device_path()

        if not device_path:
            self.status_bar.showMessage("Please select a valid capture device")
            return

        try:
            # Open capture device
            self.capture = cv2.VideoCapture(device_path, cv2.CAP_V4L2)

            if not self.capture.isOpened():
                self.status_bar.showMessage(f"Failed to open {device_path}")
                return

            # Set capture properties
            width, height = self.get_resolution()
            fps = int(self.fps_combo.currentText())

            # Set MJPEG format FIRST for better performance and quality
            self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

            # Then set resolution and FPS
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture.set(cv2.CAP_PROP_FPS, fps)

            # Optimize buffer settings for lower latency
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffering for real-time

            # Try to use hardware acceleration if available
            self.capture.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)

            # Start timer to update frames
            self.timer.start(int(1000 / fps))
            self.is_capturing = True

            self.start_btn.setText("Stop Capture")
            self.device_combo.setEnabled(False)
            self.resolution_combo.setEnabled(False)
            self.fps_combo.setEnabled(False)
            self.audio_combo.setEnabled(False)
            self.record_btn.setEnabled(True)

            # Update window title with capture source
            device_name = self.device_combo.currentText().split("(")[0].strip()
            self.setWindowTitle(f"YatsurugiCapture - {device_name}")

            self.status_bar.showMessage(f"Capturing from {device_path} at {width}x{height}@{fps}fps")

        except Exception as e:
            self.status_bar.showMessage(f"Error starting capture: {str(e)}")

    def stop_capture(self):
        """Stop video capture"""
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()

        self.timer.stop()

        if self.capture:
            self.capture.release()
            self.capture = None

        self.is_capturing = False
        self.start_btn.setText("Start Capture")
        self.device_combo.setEnabled(True)
        self.resolution_combo.setEnabled(True)
        self.fps_combo.setEnabled(True)
        self.audio_combo.setEnabled(True)
        self.record_btn.setEnabled(False)

        # Reset window title
        self.setWindowTitle("YatsurugiCapture")

        # Clear video display
        self.video_label.clear()
        self.video_label.setStyleSheet("background-color: black;")

        self.status_bar.showMessage("Capture stopped")

    def toggle_audio_passthrough(self, state):
        """Toggle audio passthrough on/off"""
        if state == Qt.Checked:
            # Start audio passthrough
            audio_device_index = self.get_audio_device_index()
            if audio_device_index is not None:
                success = self.audio_handler.start_passthrough(input_device_index=audio_device_index)
                if success:
                    self.status_bar.showMessage("Audio passthrough enabled")
                else:
                    self.status_bar.showMessage("Failed to start audio passthrough")
                    self.audio_passthrough_check.setChecked(False)
            else:
                self.status_bar.showMessage("No audio device selected")
                self.audio_passthrough_check.setChecked(False)
        else:
            # Stop audio passthrough
            self.audio_handler.stop_passthrough()
            self.status_bar.showMessage("Audio passthrough disabled")

    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording video to file"""
        if not self.is_capturing:
            self.status_bar.showMessage("Start capture first before recording")
            return

        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Recording", f"capture_{timestamp}.mp4", "Video Files (*.mp4 *.avi *.mkv)"
            )

            if not filename:
                return

            # Get video properties
            width, height = self.get_resolution()
            fps = int(self.fps_combo.currentText())

            # Use best available codec based on file extension
            ext = filename.lower().split(".")[-1]
            if ext == "mkv":
                # For MKV, try H264 first (best quality/compression)
                fourcc = cv2.VideoWriter_fourcc(*"H264")
            elif ext == "avi":
                # For AVI, use MJPEG (fast, lossless-like)
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            else:  # mp4 or default
                # For MP4, try H264, fallback to mp4v
                fourcc = cv2.VideoWriter_fourcc(*"avc1")  # H264 variant

            self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

            # If failed, try fallback codec
            if not self.video_writer.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

            if self.video_writer.isOpened():
                self.is_recording = True
                self.record_btn.setText("Stop Recording")
                self.status_bar.showMessage(f"Recording to {filename}")
            else:
                self.status_bar.showMessage("Failed to create video file")
                self.video_writer = None

        except Exception as e:
            self.status_bar.showMessage(f"Error starting recording: {str(e)}")

    def stop_recording(self):
        """Stop recording video"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.is_recording = False
        self.record_btn.setText("Start Recording")
        self.status_bar.showMessage("Recording stopped")

    def update_frame(self):
        """Read and display frame from capture device"""
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()

            if ret:
                # Write frame to file if recording (use original BGR frame)
                if self.is_recording and self.video_writer:
                    self.video_writer.write(frame)

                # Convert BGR to RGB for display (in-place for better performance)
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)

                # Convert to QImage with zero-copy approach
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                # Keep frame data alive by making a copy for QImage
                frame_copy = frame.copy()
                qt_image = QImage(frame_copy.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # Use faster scaling - FastTransformation instead of SmoothTransformation
                # SmoothTransformation is only needed when scaling DOWN significantly
                label_size = self.video_label.size()
                if w > label_size.width() * 1.5 or h > label_size.height() * 1.5:
                    # Large downscale - use smooth transformation for quality
                    scaled_pixmap = QPixmap.fromImage(qt_image).scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    # Small or no scaling - use fast transformation
                    scaled_pixmap = QPixmap.fromImage(qt_image).scaled(label_size, Qt.KeepAspectRatio, Qt.FastTransformation)

                self.video_label.setPixmap(scaled_pixmap)
            else:
                self.status_bar.showMessage("Failed to read frame")

    def toggle_borderless(self):
        """Toggle between normal window and borderless fullscreen"""
        if self.windowFlags() & Qt.FramelessWindowHint:
            # Switch back to normal window
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
            self.control_widget.show()
            self.status_bar.show()
            self.showNormal()
            self.status_bar.showMessage("Borderless mode disabled")
        else:
            # Switch to borderless - hide controls and status bar
            self.control_widget.hide()
            self.status_bar.hide()
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            self.show()

    def video_double_click(self, _event):
        """Handle double-click on video feed to toggle borderless"""
        self.toggle_borderless()

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        # Allow Escape key to exit borderless mode
        if event.key() == Qt.Key_Escape and (self.windowFlags() & Qt.FramelessWindowHint):
            self.toggle_borderless()

    def closeEvent(self, event):
        """Clean up when closing the window"""
        self.stop_capture()
        self.audio_handler.stop_passthrough()  # Always explicitly stop passthrough
        self.audio_handler.cleanup()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = CaptureWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
