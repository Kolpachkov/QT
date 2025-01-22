import sys
import socket
import struct
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QSize, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QTextEdit, QHBoxLayout, QSplitter, QTabWidget, QFileDialog, QSpinBox
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
        self.tab1 = QWidget()
        self.setup_tab1()
        

        # Tab 2: Camera Calibration
        self.tab2 = QWidget()
        self.setup_tab2()
        

        # Socket setup
        self.client_socket = None
        self.frame = None

        # Timer for video updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.receive_video)

    def setup_tab1(self):
    # Создаем виджет для первой вкладки
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)

    # Создаем боковую панель для ввода IP и кнопки подключения
        self.sidebar_widget = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)

    # Поле для ввода IP и кнопка подключения
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Enter IP Address")
        self.ip_input.setFixedHeight(80)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setFixedHeight(80)
        self.connect_button.clicked.connect(self.connect_to_server)

    # Кнопка для разрыва соединения
        self.disconnect_button = QPushButton("Disconnect", self)
        self.disconnect_button.setFixedHeight(80)
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)

        self.sidebar_layout.addWidget(self.ip_input)
        self.sidebar_layout.addWidget(self.connect_button)
        self.sidebar_layout.addWidget(self.disconnect_button)

    # Создаем центральный виджет для видео
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(1280, 960)

    # Поле для вывода сообщений о подключении и разрыве соединения
        self.info_text = QTextEdit(self)
        self.info_text.setPlaceholderText("Connection status will appear here...")
        self.info_text.setReadOnly(True)
        self.info_text.setFixedHeight(50)

    # Создаем веб-виджет для карт Яндекс
        self.map_view = QWebEngineView(self)
        self.map_view.setFixedSize(1280, 960)
        self.load_yandex_maps()

    # Создаем разделитель для боковой панели, карты и видео
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(self.map_view)
        splitter.addWidget(self.video_label)

    # Добавляем разделитель в layout вкладки
        tab1_layout.addWidget(self.info_text)
        tab1_layout.addWidget(splitter)

    # Устанавливаем виджет для вкладки
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
        self.image_label.setFixedSize(1280, 960)

    # Layout setup
        calibration_layout = QVBoxLayout()
        for spin_box in self.calibration_inputs:
            calibration_layout.addWidget(spin_box)
        calibration_widget = QWidget()
        calibration_widget.setLayout(calibration_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(calibration_widget)
        splitter2.addWidget(self.load_image_button)
        splitter2.addWidget(self.calibration_inputs_button)
        splitter.addWidget(splitter2)
        splitter.addWidget(self.image_label)
        splitter.addWidget(self.video_label2)
        

    # Add the splitter to the layout of the tab
        
        
        tab2_layout.addWidget(splitter)


    # Tracking rectangles
        self.drawing = False
        self.current_rect = None
        self.rectangles = []
        self.image_label.mousePressEvent = self.start_drawing
        self.image_label.mouseMoveEvent = self.update_drawing
        self.image_label.mouseReleaseEvent = self.finish_drawing

    # Set the layout for the widget
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
            print("IP Address is required")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((ip_address, 12345))
            print(f"Connected to server at {ip_address}")
            self.timer.start(30)
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        except Exception as e:
            print(f"Connection failed: {e}")

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

    def update_video(self):
        if self.frame is None:
            return

        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio))
        self.video_label2.setPixmap(pixmap.scaled(self.video_label2.size(), Qt.KeepAspectRatio))

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            pixmap = QPixmap(filename)
            self.image_label.setPixmap(pixmap)

    def start_drawing(self, event):
        self.drawing = True
        self.current_rect = QRect(event.pos(), QSize())

    def update_drawing(self, event):
        if self.drawing and self.current_rect:
            self.current_rect.setBottomRight(event.pos())
            self.repaint_image()

    def finish_drawing(self, event):
        if self.drawing:
            self.drawing = False
            self.rectangles.append(self.current_rect)
            self.current_rect = None

    def repaint_image(self):
        pixmap = self.image_label.pixmap()
        if pixmap:
            pixmap_copy = pixmap.copy()
            painter = QPainter(pixmap_copy)
            painter.setPen(QColor(255, 0, 0))
            for rect in self.rectangles:
                painter.drawRect(rect)
            if self.current_rect:
                painter.drawRect(self.current_rect)
            painter.end()
            self.image_label.setPixmap(pixmap_copy)

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoStreamWindow()
    window.show()
    sys.exit(app.exec_())
