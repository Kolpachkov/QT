#ifndef MAPVIEW_H
#define MAPVIEW_H

#include <QWidget>
#include <QWebEngineView>

class MapView : public QWidget {
    Q_OBJECT

public:
    explicit MapView(QWidget *parent = nullptr);
    ~MapView();

private:
    QWebEngineView *mapView;
    void loadYandexMaps();
};

#endif // MAPVIEW_H
