#include "MainWindow.h"
#include "VideoStream.h"
#include "MapView.h"
#include "CameraCalibration.h"
#include <QTabWidget>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      tabWidget(new QTabWidget(this)),
      videoStream(new VideoStream(this)),
      mapView(new MapView(this)),
      cameraCalibration(new CameraCalibration(this)) {

    setWindowTitle("Video Stream with Maps");

    tabWidget->addTab(videoStream, "Video Stream");
    tabWidget->addTab(mapView, "Maps");
    tabWidget->addTab(cameraCalibration, "Camera Calibration");

    setCentralWidget(tabWidget);
}

MainWindow::~MainWindow() {
    delete videoStream;
    delete mapView;
    delete cameraCalibration;
}
