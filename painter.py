import cv2

# Открываем камеру (0 - это обычно встроенная камера, но может быть и другая, если у вас несколько камер)
cap = cv2.VideoCapture(1)

# Проверяем, удалось ли открыть камеру
if not cap.isOpened():
    print("Ошибка: Не удалось открыть камеру.")
    exit()

# Устанавливаем параметры камеры для увеличения фреймрейта
# CAP_PROP_FPS - параметр для установки желаемого фреймрейта
desired_fps = 30  # Желаемый фреймрейт (например, 30 кадров в секунду)
cap.set(cv2.CAP_PROP_FPS, desired_fps)

# CAP_PROP_FRAME_WIDTH и CAP_PROP_FRAME_HEIGHT - параметры для установки разрешения
# Меньшее разрешение может помочь увеличить фреймрейт
desired_width = 640
desired_height = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

# Получаем текущие параметры камеры для проверки
actual_fps = cap.get(cv2.CAP_PROP_FPS)
actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(f"Текущий фреймрейт: {actual_fps} FPS")
print(f"Текущее разрешение: {actual_width}x{actual_height}")

# Чтение и отображение кадров с камеры
while True:
    ret, frame = cap.read()
    if not ret:
        print("Ошибка: Не удалось получить кадр.")
        break

    # Отображаем кадр
    cv2.imshow('Camera', frame)

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()