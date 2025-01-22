#include "CameraCalibration.h"
#include <QVBoxLayout>
#include <QFileDialog>
#include <opencv2/opencv.hpp>

CameraCalibration::CameraCalibration(QWidget *parent) : QWidget(parent),
    loadImageButton(new QPushButton("Load Image", this)),
    deleteRectInput(new QLineEdit(this)),
    deleteRectButton(new QPushButton("Delete Rectangle", this)),
    imageLabel(new QLabel(this)) {

    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->addWidget(loadImageButton);
    layout->addWidget(deleteRectInput);
    layout->addWidget(deleteRectButton);
    layout->addWidget(imageLabel);

    connect(loadImageButton, &QPushButton::clicked, this, &CameraCalibration::loadImage);
    connect(deleteRectButton, &QPushButton::clicked, this, &CameraCalibration::deleteRectangle);
}

CameraCalibration::~CameraCalibration() {
    delete loadImageButton;
    delete deleteRectInput;
    delete deleteRectButton;
    delete imageLabel;
}

void CameraCalibration::loadImage() {
    QString filename = QFileDialog::getOpenFileName(this, "Open Image", "", "Images (*.png *.jpg *.bmp)");
    if (!filename.isEmpty()) {
        cv::Mat img = cv::imread(filename.toStdString());
        if (!img.empty()) {
            cv::cvtColor(img, img, cv::COLOR_BGR2RGB);
            QImage qImage(img.data, img.cols, img.rows, img.step, QImage::Format_RGB888);
            imageLabel->setPixmap(QPixmap::fromImage(qImage));
        }
    }
}

void CameraCalibration::deleteRectangle() {
    bool ok;
    int rectIndex = deleteRectInput->text().toInt(&ok);
    if (ok && rectIndex >= 0) {
        // Implement rectangle deletion logic
    }
}
