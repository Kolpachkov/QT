import sys
import socket
import struct
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QTextEdit, QSplitter, QTabWidget, QFileDialog, QSpinBox, QHBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class VideoStreamWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Stream Client with Yandex Maps and Camera Calibration")
        self.setGeometry(100, 100, 3000, 1200)

        # Tab widget to hold multiple tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab 1: Video Stream and Map
        self.setup_tab1()

        # Tab 2: Camera Calibration
        self.setup_tab2()

        # Socket setup
        self.client_socket = None
        self.frame = None

        # Timer for video updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.receive_video)

        # Attributes for drawing
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rectangles = []
        self.original_image = None  # OpenCV image for drawing

    def setup_tab1(self):
        """Setup the first tab with video stream and map."""
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)

        # Sidebar for IP input and buttons
        self.sidebar_widget = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Enter IP Address")
        self.ip_input.setFixedHeight(80)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setFixedHeight(80)
        self.connect_button.clicked.connect(self.connect_to_server)

        self.disconnect_button = QPushButton("Disconnect", self)
        self.disconnect_button.setFixedHeight(80)
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)

        self.sidebar_layout.addWidget(self.ip_input)
        self.sidebar_layout.addWidget(self.connect_button)
        self.sidebar_layout.addWidget(self.disconnect_button)

        # Video display
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(1280, 960)

        # Connection status
        self.info_text = QTextEdit(self)
        self.info_text.setPlaceholderText("Connection status will appear here...")
        self.info_text.setReadOnly(True)
        self.info_text.setFixedHeight(50)

        # Yandex Map
        self.map_view = QWebEngineView(self)
        self.map_view.setFixedSize(1280, 960)
        self.load_yandex_maps()

        # Splitter layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(self.map_view)
        splitter.addWidget(self.video_label)

        tab1_layout.addWidget(self.info_text)
        tab1_layout.addWidget(splitter)

        self.tab_widget.addTab(tab1_widget, "Video & Map")

    def setup_tab2(self):
        """Setup the second tab for camera calibration."""
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)

        # Calibration coefficients inputs
        self.calibration_inputs = []
        for i in range(10):
            spin_box = QSpinBox()
            spin_box.setRange(-1000, 1000)
            spin_box.setPrefix(f"Coeff {i + 1}: ")
            self.calibration_inputs.append(spin_box)

        # Load image button
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)

        self.calibration_inputs_button = QPushButton("Calibrate")

        self.video_label2 = QLabel(self)
        self.video_label2.setAlignment(Qt.AlignCenter)
        self.video_label2.setFixedSize(1280, 960)    

        # Image display and editing
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(959, 926)

        # Add delete rectangle button
        self.delete_rect_input = QLineEdit(self)
        self.delete_rect_input.setPlaceholderText("Enter rectangle number to delete")
        self.delete_rect_button = QPushButton("Delete Rectangle", self)
        self.delete_rect_button.clicked.connect(self.delete_rectangle)

        # Layout setup for calibration
        calibration_layout = QVBoxLayout()
        for spin_box in self.calibration_inputs:
            calibration_layout.addWidget(spin_box)
        calibration_widget = QWidget()
        calibration_widget.setLayout(calibration_layout)

        # Layout for delete rectangle
        delete_layout = QHBoxLayout()
        delete_layout.addWidget(self.delete_rect_input)
        delete_layout.addWidget(self.delete_rect_button)
        delete_widget = QWidget()
        delete_widget.setLayout(delete_layout)

        # Create splitter and add widgets
        splitter = QSplitter(Qt.Horizontal)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(calibration_widget)
        splitter2.addWidget(self.load_image_button)
        splitter2.addWidget(self.calibration_inputs_button)
        splitter2.addWidget(delete_widget)  # Add delete layout to the splitter

        # Add vertical splitter and image/video widgets
        splitter.addWidget(splitter2)
        splitter.addWidget(self.image_label)
        splitter.addWidget(self.video_label2)

        tab2_layout.addWidget(splitter)

        # Add drawing functionality
        self.image_label.mousePressEvent = self.start_drawing
        self.image_label.mouseMoveEvent = self.update_drawing
        self.image_label.mouseReleaseEvent = self.finish_drawing

        self.tab_widget.addTab(tab2_widget, "Camera Calibration")

    def load_yandex_maps(self):
        """Load Yandex Maps in the map view."""
        yandex_maps_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
            <style>
                html, body, #map {
                    width: 100%;
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                ymaps.ready(init);
                function init() {
                    var map = new ymaps.Map("map", {
                        center: [56.479187, 85.068086],
                        zoom: 10
                    });
                }
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(yandex_maps_html)

    def connect_to_server(self):
        ip_address = self.ip_input.text()
        if not ip_address:
            self.info_text.append("IP Address is required")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((ip_address, 12345))
            self.info_text.append(f"Connected to server at {ip_address}")
            self.timer.start(30)
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        except Exception as e:
            self.info_text.append(f"Connection failed: {e}")

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.timer.stop()

    def receive_video(self):
        if not self.client_socket:
            return

        try:
            length_data = self.client_socket.recv(4)
            if len(length_data) < 4:
                return

            length = struct.unpack('I', length_data)[0]
            data = b"" 
            while len(data) < length:
                data += self.client_socket.recv(length - len(data))

            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                self.frame = frame
                self.update_video()
        except Exception as e:
            self.info_text.append(f"Video reception failed: {e}")

    def update_video(self):
        if self.frame is None:
            return

        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio))

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.original_image = cv2.imread(filename)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            height, width, channel = self.original_image.shape
            bytes_per_line = channel * width
            qimage = QImage(self.original_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)

    def start_drawing(self, event):
        if self.original_image is None:
            self.info_text.append("Please load an image before drawing.")
            return
        self.drawing = True
        self.start_point = event.pos()

    def update_drawing(self, event):
        if self.drawing and self.original_image is not None:
            self.end_point = event.pos()
            self.repaint_with_opencv()

    def finish_drawing(self, event):
        if self.drawing and self.original_image is not None:
            self.drawing = False
            self.rectangles.append(QRect(self.start_point, self.end_point))
            self.repaint_with_opencv()

    def repaint_with_opencv(self):
        if self.original_image is None:
            return

        image_copy = self.original_image.copy()

        for rect in self.rectangles:
            cv2.rectangle(
                image_copy,
                (rect.x(), rect.y()),
                (rect.x() + rect.width(), rect.y() + rect.height()),
                (0, 0, 255),
                2
            )

        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(
                image_copy,
                (self.start_point.x(), self.start_point.y()),
                (self.end_point.x(), self.end_point.y()),
                (0, 255, 0),
                2
            )

        height, width, channel = image_copy.shape
        bytes_per_line = channel * width
        qimage = QImage(image_copy.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

    def delete_rectangle(self):
        rect_number = self.delete_rect_input.text()
        if not rect_number.isdigit() or int(rect_number) >= len(self.rectangles) or int(rect_number) < 0:
            self.info_text.append("Invalid rectangle number.")
            return

        # Remove the specified rectangle
        self.rectangles.pop(int(rect_number))
        self.repaint_with_opencv()

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoStreamWindow()
    window.show()
    sys.exit(app.exec_())
