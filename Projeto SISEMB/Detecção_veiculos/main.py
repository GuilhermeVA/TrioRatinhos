import sys
sys.path.append('D:/Documentos/OneDrive/Ibmec/Sistemas Embarcados/teste1/yolov5')
import cv2
import numpy as np
import time
from collections import deque
from sort import Sort
from ultralytics import YOLO  # Importa YOLO diretamente

# Configurações do YOLO e do rastreador SORT
model = YOLO('yolov8s.pt')  # Carrega o modelo YOLOv8 pré-treinado
video_path = 'test3.h264'  # Caminho do vídeo
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)  # Taxa de quadros do vídeo
scale_factor = 0.03  # Ajuste para um valor realista para a sua câmera e configuração

# Inicializa o rastreador SORT
tracker = Sort(max_age=5, min_hits=2, iou_threshold=0.3)

# Dicionários para armazenar posições anteriores, tempos de início e velocidades médias dos veículos
velocidades = {}
media_velocidades = {}  # Armazena uma média móvel das velocidades
inicializar_tempo = {}  # Armazena o tempo de início de rastreamento do veículo

# Tamanho da média móvel para suavizar a velocidade
window_size = 5  # Ajuste conforme necessário
delay_para_media = 0.5  # Delay de 0.5 segundos

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Reduz a resolução do quadro para melhorar o desempenho
    frame = cv2.resize(frame, (640, 360))

    # Detecção de veículos usando YOLO
    results = model(frame)  # Executa a detecção
    detections = results[0].boxes.data.cpu().numpy()  # Extrai as detecções como um array numpy

    # Filtra apenas os veículos (IDs 2: 'car', 5: 'bus', 7: 'truck', 3: 'motorbike')
    vehicles = [d for d in detections if int(d[5]) in [2, 5, 7, 3]]

    # Formata as detecções para o rastreador SORT [xmin, ymin, xmax, ymax, confidence]
    dets = []
    for vehicle in vehicles:
        x1, y1, x2, y2, confidence, cls_id = vehicle[:6]
        dets.append([x1, y1, x2, y2, confidence])

    dets = np.array(dets)
    if len(dets) > 0:
        tracks = tracker.update(dets)  # Atualiza o rastreamento com SORT
    else:
        tracks = []

    # Processa cada rastreamento
    for track in tracks:
        x1, y1, x2, y2, track_id = track.astype(int)
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        # Marca o tempo de início para cálculo de delay
        if track_id not in inicializar_tempo:
            inicializar_tempo[track_id] = time.time()

        # Atualiza a posição do veículo para cálculo da velocidade
        if track_id not in velocidades:
            velocidades[track_id] = deque(maxlen=2)  # Armazena as últimas duas posições do objeto
        velocidades[track_id].append((center_x, center_y))

        # Calcula a velocidade quando há histórico de posição suficiente
        if len(velocidades[track_id]) == 2:
            (x_prev, y_prev), (x_curr, y_curr) = velocidades[track_id]
            pixel_distance = np.sqrt((x_curr - x_prev) ** 2 + (y_curr - y_prev) ** 2)
            distance_m = pixel_distance * scale_factor

            # Calcula a velocidade em km/h
            speed_m_s = distance_m * fps
            speed_kmh = speed_m_s * 3.6

            # Armazena a velocidade no deque de média móvel para suavizar as variações
            if track_id not in media_velocidades:
                media_velocidades[track_id] = deque(maxlen=window_size)
            media_velocidades[track_id].append(speed_kmh)

            # Verifica se passaram 0.5 segundos
            if (time.time() - inicializar_tempo[track_id]) >= delay_para_media:
                # Calcula a média das últimas velocidades
                average_speed_kmh = np.mean(media_velocidades[track_id])

                # Exibe a velocidade média no quadro e console se ultrapassar 40 km/h
                if average_speed_kmh > 0 and average_speed_kmh < 200:  # Filtra valores irreais
                    cv2.putText(frame, f"{int(average_speed_kmh)} km/h", (center_x, center_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    if average_speed_kmh > 40:
                        print(f"{track_id},{int(average_speed_kmh)}")
                        
                        # Grava o ID e a velocidade no arquivo txt
                        with open("velocidades_carros.txt", "a") as f:
                            f.write(f"{track_id}, {int(average_speed_kmh)}\n")

        # Desenha a caixa delimitadora com ID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Exibir o vídeo com as detecções e velocidades
    cv2.imshow('Detecção de Carros e Velocidade', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
