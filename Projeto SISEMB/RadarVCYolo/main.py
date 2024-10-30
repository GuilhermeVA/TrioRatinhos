import cv2
import torch
import time

# Parâmetros de calibração
distancia_metros = 3  # Distância real entre as barras em metros

# Carrega o modelo YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # 'yolov5s' é a versão mais leve

# Carrega o vídeo
cap = cv2.VideoCapture('test3.h264')

# Defina as posições das linhas
linha_inicio = (100, 200)
linha_fim = (100, 400)

carros_ativos = {}

# Função para calcular a velocidade
def calcula_velocidade(pixels_percorridos, tempo, ppx_metros):
    metros_percorridos = pixels_percorridos * ppx_metros
    velocidade_ms = metros_percorridos / tempo
    return velocidade_ms * 3.6  # Converte para km/h

# Processo principal
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Barras de detecção
    cv2.line(frame, (linha_inicio[0], linha_inicio[1]), (linha_inicio[0] + 200, linha_inicio[1]), (0, 255, 0), 2)
    cv2.line(frame, (linha_fim[0], linha_fim[1]), (linha_fim[0] + 200, linha_fim[1]), (0, 0, 255), 2)

    # Passa o frame pelo YOLOv5
    results = model(frame)

    # Filtra as detecções para carros
    for detection in results.xyxy[0]:
        class_id = int(detection[5])
        confidence = detection[4]
        if confidence > 0.5 and model.names[class_id] == "car":  # A classe 'car' para YOLOv5
            x, y, w, h = int(detection[0]), int(detection[1]), int(detection[2]), int(detection[3])
            centro_x = (x + w) // 2
            centro_y = (y + h) // 2

            # Identifica se o carro atravessa as linhas
            if y < linha_inicio[1] < h:
                carros_ativos[centro_x] = time.time()
            elif y < linha_fim[1] < h and centro_x in carros_ativos:
                tempo_decorrido = time.time() - carros_ativos.pop(centro_x)
                pixels_percorridos = abs(linha_inicio[1] - linha_fim[1])
                ppx_metros = distancia_metros / pixels_percorridos

                velocidade_kmh = calcula_velocidade(pixels_percorridos, tempo_decorrido, ppx_metros)
                print(f"Velocidade do carro (YOLOv5): {velocidade_kmh:.2f} km/h")

    # Mostre o quadro com as linhas
    cv2.imshow('Video YOLOv5', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
