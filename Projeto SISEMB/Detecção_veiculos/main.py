import sys
sys.path.append('D:/Documentos/OneDrive/Ibmec/Sistemas Embarcados/teste1/yolov5')
import cv2
import torch
import numpy as np
import yt_dlp
from collections import deque
from sort import Sort

import yt_dlp

# Função para baixar vídeo usando yt-dlp
def download_video(url, path="test_video.mp4"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"Vídeo baixado em: {path}")
# URL do vídeo que você deseja testar (substitua com um link válido)
video_url = "https://www.youtube.com/watch?v=3IaKJuZN55k"

# Baixe o vídeo usando yt-dlp
download_video(video_url, "test_video.mp4")


# Configurações do YOLO e do rastreador SORT
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # YOLOv5 pré-treinado
video_path = 'test_video.mp4'  # Caminho do vídeo
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)  # Taxa de quadros do vídeo
scale_factor = 0.03  # Ajuste para um valor realista para a sua câmera e configuração

# Inicializa o rastreador SORT
tracker = Sort(max_age=5, min_hits=2, iou_threshold=0.3)

# Dicionário para armazenar posições anteriores dos veículos para calcular velocidades
velocidades = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Reduz a resolução do quadro para melhorar o desempenho
    frame = cv2.resize(frame, (640, 360))

    # Detecção de veículos usando YOLO
    results = model(frame)
    detections = results.pandas().xyxy[0]  # DataFrame com as detecções
    detections = detections[detections['name'].isin(['car', 'truck', 'bus', 'motorbike'])]

    # Formata as detecções para o rastreador SORT [xmin, ymin, xmax, ymax, confidence]
    dets = []
    for _, detection in detections.iterrows():
        x1, y1, x2, y2, confidence = detection[['xmin', 'ymin', 'xmax', 'ymax', 'confidence']]
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

            # Exibe a velocidade no quadro
            if speed_kmh > 0 and speed_kmh < 200:  # Filtra valores irreais
                cv2.putText(frame, f"{int(speed_kmh)} km/h", (center_x, center_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Desenha a caixa delimitadora com ID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Exibir o vídeo com as detecções e velocidades
    cv2.imshow('Detecção de Carros e Velocidade', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
