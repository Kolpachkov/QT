#include "SocketClient.h"

SocketClient::SocketClient(QObject *parent) : QTcpSocket(parent) {
    connect(this, &QTcpSocket::readyRead, this, &SocketClient::readData);
}

SocketClient::~SocketClient() {}

void SocketClient::connectToServer(const QString &address, int port) {
    this->connectToHost(address, port);
}

void SocketClient::disconnectFromServer() {
    this->disconnectFromHost();
}

void SocketClient::sendData(const QByteArray &data) {
    this->write(data);
}

void SocketClient::readData() {
    QByteArray data = this->readAll();
    emit dataReceived(data);
}
