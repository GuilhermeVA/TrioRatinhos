import cv2
import numpy as np
import time

# Parâmetros de calibração
distancia_metros = 3  # Distância real entre as barras em metros

# Carrega o modelo DNN
net = cv2.dnn.readNetFromTensorflow("frozen_inference_graph.pb", "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")

# Carrega o vídeo
cap = cv2.VideoCapture('video_sinal.h264')

# Defina as posições das linhas
linha_inicio = (100, 200)
linha_fim = (100, 400)

carros_ativos = {}
frame_anterior = None

# Função para calcular a velocidade
def calcula_velocidade(pixels_percorridos, tempo, ppx_metros):
    metros_percorridos = pixels_percorridos * ppx_metros
    velocidade_ms = metros_percorridos / tempo
    return velocidade_ms * 3.6

# Processo principal
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Barras de detecção
    cv2.line(frame, (linha_inicio[0], linha_inicio[1]), (linha_inicio[0] + 200, linha_inicio[1]), (0, 255, 0), 2)
    cv2.line(frame, (linha_fim[0], linha_fim[1]), (linha_fim[0] + 200, linha_fim[1]), (0, 0, 255), 2)

    # Passa o frame pelo DNN
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        class_id = int(detections[0, 0, i, 1])

        if confidence > 0.5 and class_id == 3:  # Classe "carro" é 3 em COCO
            x_left_bottom = int(detections[0, 0, i, 3] * frame.shape[1])
            y_left_bottom = int(detections[0, 0, i, 4] * frame.shape[0])
            x_right_top = int(detections[0, 0, i, 5] * frame.shape[1])
            y_right_top = int(detections[0, 0, i, 6] * frame.shape[0])

            # Identifica se o carro atravessa as linhas
            if y_left_bottom < linha_inicio[1] < y_right_top:
                carros_ativos[x_left_bottom] = time.time()
            elif y_left_bottom < linha_fim[1] < y_right_top and x_left_bottom in carros_ativos:
                tempo_decorrido = time.time() - carros_ativos.pop(x_left_bottom)
                pixels_percorridos = abs(linha_inicio[1] - linha_fim[1])
                ppx_metros = distancia_metros / pixels_percorridos

                velocidade_kmh = calcula_velocidade(pixels_percorridos, tempo_decorrido, ppx_metros)
                print(f"Velocidade do carro (DNN): {velocidade_kmh:.2f} km/h")

    # Mostre o quadro com as linhas
    cv2.imshow('Video DNN', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
