#ifndef SOCKETCLIENT_H
#define SOCKETCLIENT_H

#include <QTcpSocket>

class SocketClient : public QTcpSocket {
    Q_OBJECT

public:
    explicit SocketClient(QObject *parent = nullptr);
    ~SocketClient();

    void connectToServer(const QString &address, int port);
    void disconnectFromServer();
    void sendData(const QByteArray &data);

signals:
    void dataReceived(const QByteArray &data);
};

#endif // SOCKETCLIENT_H
