// main.cpp
#include "mainwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    MainWindow window;
    window.show();

    return app.exec();
}

// mainwindow.h
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QTextEdit>
#include <QSplitter>
#include <QTabWidget>
#include <QSpinBox>
#include <QVBoxLayout> 
#include <QWebEngineView>
#include <QTimer>
#include <QMouseEvent>
#include <opencv2/opencv.hpp> 
#include <vector>
#include <QTcpSocket>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    void closeEvent(QCloseEvent *event) override;

private slots:
    void connectToServer();
    void disconnectFromServer();
    void receiveVideo();
    void loadImage();
    void deleteRectangle();

private:
    void setupTab1();
    void setupTab2();
    void loadYandexMaps();
    void updateVideo();
    void repaintWithOpenCV();

    void startDrawing(QMouseEvent *event);
    void updateDrawing(QMouseEvent *event);
    void finishDrawing(QMouseEvent *event);

    QTabWidget *tabWidget;

    // Tab 1 elements
    QLineEdit *ipInput;
    QPushButton *connectButton;
    QPushButton *disconnectButton;
    QTextEdit *infoText;
    QLabel *videoLabel;
    QWebEngineView *mapView;

    // Tab 2 elements
    QLabel *imageLabel;
    QPushButton *loadImageButton;
    QPushButton *calibrationInputsButton;
    QLineEdit *deleteRectInput;
    QPushButton *deleteRectButton;
    std::vector<QSpinBox*> calibrationInputs;

    // Networking
    QTcpSocket *clientSocket;
    QTimer *timer;

    // OpenCV
    cv::Mat frame;
    cv::Mat originalImage;

    // Drawing attributes
    bool drawing;
    QPoint startPoint;
    QPoint endPoint;
    std::vector<QRect> rectangles;
};

#endif // MAINWINDOW_H

// mainwindow.cpp
#include "mainwindow.h"
#include <QFileDialog>
#include <QMessageBox>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QTcpSocket>
#include <QCloseEvent>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      clientSocket(new QTcpSocket(this)),
      timer(new QTimer(this)),
      drawing(false)
{
    setWindowTitle("Video Stream Client with Yandex Maps and Camera Calibration");
    setGeometry(100, 100, 3000, 1200);

    tabWidget = new QTabWidget(this);
    setCentralWidget(tabWidget);

    setupTab1();
    setupTab2();

    connect(timer, &QTimer::timeout, this, &MainWindow::receiveVideo);
}

MainWindow::~MainWindow()
{
    if (clientSocket->isOpen()) {
        clientSocket->close();
    }
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    if (clientSocket->isOpen()) {
        clientSocket->close();
    }
    event->accept();
}

void MainWindow::setupTab1()
{
    QWidget *tab1Widget = new QWidget(this);
    QVBoxLayout *tab1Layout = new QVBoxLayout(tab1Widget);

    ipInput = new QLineEdit(this);
    ipInput->setPlaceholderText("Enter IP Address");

    connectButton = new QPushButton("Connect", this);
    disconnectButton = new QPushButton("Disconnect", this);
    disconnectButton->setEnabled(false);

    infoText = new QTextEdit(this);
    infoText->setReadOnly(true);

    videoLabel = new QLabel(this);
    videoLabel->setAlignment(Qt::AlignCenter);

    mapView = new QWebEngineView(this);
    loadYandexMaps();

    QSplitter *splitter = new QSplitter(Qt::Horizontal, this);
    QWidget *sidebarWidget = new QWidget(this);
    QVBoxLayout *sidebarLayout = new QVBoxLayout(sidebarWidget);
    sidebarLayout->addWidget(ipInput);
    sidebarLayout->addWidget(connectButton);
    sidebarLayout->addWidget(disconnectButton);

    splitter->addWidget(sidebarWidget);
    splitter->addWidget(mapView);
    splitter->addWidget(videoLabel);

    tab1Layout->addWidget(infoText);
    tab1Layout->addWidget(splitter);

    tabWidget->addTab(tab1Widget, "Video & Map");

    connect(connectButton, &QPushButton::clicked, this, &MainWindow::connectToServer);
    connect(disconnectButton, &QPushButton::clicked, this, &MainWindow::disconnectFromServer);
}

void MainWindow::setupTab2()
{
    QWidget *tab2Widget = new QWidget(this);
    QVBoxLayout *tab2Layout = new QVBoxLayout(tab2Widget);

    imageLabel = new QLabel(this);
    imageLabel->setAlignment(Qt::AlignCenter);

    loadImageButton = new QPushButton("Load Image", this);
    calibrationInputsButton = new QPushButton("Calibrate", this);

    deleteRectInput = new QLineEdit(this);
    deleteRectInput->setPlaceholderText("Enter rectangle number to delete");
    deleteRectButton = new QPushButton("Delete Rectangle", this);

    QVBoxLayout *calibrationLayout = new QVBoxLayout;
    for (int i = 0; i < 10; ++i) {
        QSpinBox *spinBox = new QSpinBox(this);
        spinBox->setRange(-1000, 1000);
        calibrationInputs.push_back(spinBox);
        calibrationLayout->addWidget(spinBox);
    }

    QVBoxLayout *deleteLayout = new QVBoxLayout;
    deleteLayout->addWidget(deleteRectInput);
    deleteLayout->addWidget(deleteRectButton);

    QSplitter *splitter = new QSplitter(Qt.Horizontal, this);
    QWidget *calibrationWidget = new QWidget(this);
    calibrationWidget->setLayout(calibrationLayout);

    QWidget *deleteWidget = new QWidget(this);
    deleteWidget->setLayout(deleteLayout);

    splitter->addWidget(calibrationWidget);
    splitter->addWidget(deleteWidget);
    splitter->addWidget(imageLabel);

    tab2Layout->addWidget(splitter);

    tabWidget->addTab(tab2Widget, "Camera Calibration");

    connect(loadImageButton, &QPushButton::clicked, this, &MainWindow::loadImage);
    connect(deleteRectButton, &QPushButton::clicked, this, &MainWindow::deleteRectangle);
}

void MainWindow::loadYandexMaps()
{
    QString yandexMapsHtml = R"(
        <!DOCTYPE html>
        <html>
        <head>
            <script src=\"https://api-maps.yandex.ru/2.1/?lang=ru_RU\"></script>
        </head>
        <body>
            <div id=\"map\" style=\"width:100%; height:100%;\"></div>
            <script>
                ymaps.ready(function() {
                    var map = new ymaps.Map("map", { center: [56.479187, 85.068086], zoom: 10 });
                });
            </script>
        </body>
        </html>
    )";
    mapView->setHtml(yandexMapsHtml);
}

void MainWindow::connectToServer()
{
    QString ipAddress = ipInput->text();
    if (ipAddress.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please enter an IP address.");
        return;
    }

    clientSocket->connectToHost(ipAddress, 1234);
    if (clientSocket->waitForConnected(5000)) {
        infoText->append("Connected to server.");
        connectButton->setEnabled(false);
        disconnectButton->setEnabled(true);
        timer->start(33);
    } else {
        QMessageBox::critical(this, "Error", "Could not connect to server.");
    }
}

void MainWindow::disconnectFromServer()
{
    timer->stop();
    clientSocket->disconnectFromHost();
    connectButton->setEnabled(true);
    disconnectButton->setEnabled(false);
    infoText->append("Disconnected from server.");
}

void MainWindow::receiveVideo()
{
    if (clientSocket->bytesAvailable() < sizeof(quint32)) {
        return;
    }

    QByteArray data = clientSocket->readAll();
    frame = cv::imdecode(std::vector<uchar>(data.begin(), data.end()), cv::IMREAD_COLOR);
    updateVideo();
}

void MainWindow::updateVideo()
{
    if (!frame.empty()) {
        cv::Mat rgbFrame;
        cv::cvtColor(frame, rgbFrame, cv::COLOR_BGR2RGB);
        QImage qImg(rgbFrame.data, rgbFrame.cols, rgbFrame.rows, rgbFrame.step, QImage::Format_RGB888);
        videoLabel->setPixmap(QPixmap::fromImage(qImg));
    }
}

void MainWindow::loadImage()
{
    QString fileName = QFileDialog::getOpenFileName(this, "Open Image", "", "Images (*.png *.xpm *.jpg)");
    if (!fileName.isEmpty()) {
        originalImage = cv::imread(fileName.toStdString());
        repaintWithOpenCV();
    }
}

void MainWindow::deleteRectangle()
{
    bool ok;
    int index = deleteRectInput->text().toInt(&ok);
    if (ok && index >= 0 && index < rectangles.size()) {
        rectangles.erase(rectangles.begin() + index);
        repaintWithOpenCV();
    } else {
        QMessageBox::warning(this, "Error", "Invalid rectangle index.");
    }
}

void MainWindow::repaintWithOpenCV()
{
    if (!originalImage.empty()) {
        cv::Mat displayImage = originalImage.clone();
        for (const QRect &rect : rectangles) {
            cv::rectangle(displayImage, cv::Rect(rect.x(), rect.y(), rect.width(), rect.height()), cv::Scalar(0, 255, 0), 2);
        }
        cv::cvtColor(displayImage, displayImage, cv::COLOR_BGR2RGB);
        QImage qImg(displayImage.data, displayImage.cols, displayImage.rows, displayImage.step, QImage::Format_RGB888);
        imageLabel->setPixmap(QPixmap::fromImage(qImg));
    }
}

void MainWindow::startDrawing(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        drawing = true;
        startPoint = event->pos();
    }
}

void MainWindow::updateDrawing(QMouseEvent *event)
{
    if (drawing) {
        endPoint = event->pos();
        repaintWithOpenCV();
    }
}

void MainWindow::finishDrawing(QMouseEvent *event)
{
    if (drawing && event->button() == Qt::LeftButton) {
        drawing = false;
        rectangles.push_back(QRect(startPoint, endPoint));
        repaintWithOpenCV();
    }
}
