#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QWidget>
#include <QVBoxLayout>
#include <QTabWidget>

class VideoStream;
class MapView;
class CameraCalibration;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    QTabWidget *tabWidget;
    VideoStream *videoStream;
    MapView *mapView;
    CameraCalibration *cameraCalibration;
};

#endif // MAINWINDOW_H
