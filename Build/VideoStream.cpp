#include "VideoStream.h"
#include <QVBoxLayout>
#include <QLabel>
#include <QImage>
#include <QPixmap>
#include <QTcpSocket>
#include <opencv2/opencv.hpp>

VideoStream::VideoStream(QWidget *parent) : QWidget(parent),
    clientSocket(nullptr),
    timer(new QTimer(this)),
    ipInput(new QLineEdit(this)),
    connectButton(new QPushButton("Connect", this)),
    disconnectButton(new QPushButton("Disconnect", this)),
    videoLabel(new QLabel(this)) {

    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->addWidget(ipInput);
    layout->addWidget(connectButton);
    layout->addWidget(disconnectButton);
    layout->addWidget(videoLabel);

    connect(connectButton, &QPushButton::clicked, this, &VideoStream::connectToServer);
    connect(disconnectButton, &QPushButton::clicked, this, &VideoStream::disconnectFromServer);
    connect(timer, &QTimer::timeout, this, &VideoStream::receiveVideo);
}

VideoStream::~VideoStream() {
    delete clientSocket;
    delete timer;
    delete ipInput;
    delete connectButton;
    delete disconnectButton;
    delete videoLabel;
}

void VideoStream::connectToServer() {
    QString ipAddress = ipInput->text();
    if (ipAddress.isEmpty()) {
        return;
    }

    clientSocket = new QTcpSocket(this);
    clientSocket->connectToHost(ipAddress, 12345);
    connect(clientSocket, &QTcpSocket::readyRead, this, &VideoStream::receiveVideo);
    timer->start(30);
}

void VideoStream::disconnectFromServer() {
    if (clientSocket) {
        clientSocket->close();
        clientSocket = nullptr;
    }
    timer->stop();
}

void VideoStream::receiveVideo() {
    QByteArray data = clientSocket->readAll();
    updateVideo(data);
}

void VideoStream::updateVideo(const QByteArray &data) {
    cv::Mat frame = cv::imdecode(cv::Mat(data), cv::IMREAD_COLOR);
    if (!frame.empty()) {
        cv::Mat rgbFrame;
        cv::cvtColor(frame, rgbFrame, cv::COLOR_BGR2RGB);
        QImage img(rgbFrame.data, rgbFrame.cols, rgbFrame.rows, rgbFrame.step, QImage::Format_RGB888);
        videoLabel->setPixmap(QPixmap::fromImage(img).scaled(videoLabel->size(), Qt::KeepAspectRatio));
    }
}
