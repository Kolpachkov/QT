#ifndef CAMERACALIBRATION_H
#define CAMERACALIBRATION_H

#include <QWidget>
#include <QPushButton>
#include <QLineEdit>
#include <QLabel>

class CameraCalibration : public QWidget {
    Q_OBJECT

public:
    explicit CameraCalibration(QWidget *parent = nullptr);
    ~CameraCalibration();

private:
    QPushButton *loadImageButton;
    QLineEdit *deleteRectInput;
    QPushButton *deleteRectButton;
    QLabel *imageLabel;

private slots:
    void loadImage();
    void deleteRectangle();
};

#endif // CAMERACALIBRATION_H
