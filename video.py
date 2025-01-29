import numpy as np
import cv2

# Задаем размер шахматной доски (количество внутренних углов)
chessboard_size = (9, 6)
frame_size = (640, 480)

# Подготовка объектных точек, например (0,0,0), (1,0,0), (2,0,0) ..., (8,5,0)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Массивы для хранения объектных точек и точек на изображении
objpoints = []  # 3d точки в реальном мире
imgpoints = []  # 2d точки на изображении

# Захват видеопотока с камеры
cap = cv2.VideoCapture(1)  # 0 - индекс камеры, может быть изменен на другой, если подключено несколько камер

# Установка параметров камеры для увеличения фреймрейта и других настроек
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
cap.set(cv2.CAP_PROP_FPS, 30)  # Установка желаемого фреймрейта (например, 30 FPS)


while True:
    ret, img = cap.read()
    if not ret:
        print("Не удалось захватить изображение с камеры.")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Поиск углов шахматной доски
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    # Если углы найдены, добавляем объектные точки и точки на изображении
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # Отрисовка и отображение углов
        cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('Chessboard', img)

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()

# Калибровка камеры
if len(objpoints) > 0:
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame_size, None, None)

    # Сохранение параметров калибровки
    np.savez('calibration_params.npz', camera_matrix=camera_matrix, dist_coeffs=dist_coeffs, rvecs=rvecs, tvecs=tvecs)

    # Пример использования параметров калибровки для исправления искажений
    cap = cv2.VideoCapture(1)  # Снова открываем видеопоток для демонстрации исправленного изображения
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
    cap.set(cv2.CAP_PROP_FPS, 30)  # Установка желаемого фреймрейта
    

    while True:
        ret, img = cap.read()
        if not ret:
            print("Не удалось захватить изображение с камеры.")
            break

        h, w = img.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

        # Исправление искажений
        dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

        # Обрезка изображения
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        # Отображение исправленного изображения
        cv2.imshow('Undistorted Image', dst)

        # Выход по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()
else:
    print("Не удалось найти углы шахматной доски для калибровки.")