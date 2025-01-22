#include "MapView.h"
#include <QWebEngineView>

MapView::MapView(QWidget *parent) : QWidget(parent), mapView(new QWebEngineView(this)) {
    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->addWidget(mapView);
    loadYandexMaps();
}

MapView::~MapView() {
    delete mapView;
}

void MapView::loadYandexMaps() {
    QString yandexMapHtml = R"(
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100%;"></div>
            <script>
                ymaps.ready(function() {
                    var map = new ymaps.Map("map", {
                        center: [55.7558, 37.6173],
                        zoom: 10
                    });
                });
            </script>
        </body>
        </html>
    )";
    mapView->setHtml(yandexMapHtml);
}
