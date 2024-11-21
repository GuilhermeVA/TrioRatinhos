import cv2
import numpy as np
import time
from collections import deque
from sort import Sort
from ultralytics import YOLO

# Configurações do YOLO e do rastreador SORT
model = YOLO('yolov8s.pt')  # Carrega o modelo YOLOv8 pré-treinado
video_path = 'a.h264'  # Caminho do vídeo
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)  # Taxa de quadros do vídeo

# Definição das linhas de profundidade
depth_lines = [
    {'y_position': 100, 'scale_factor': 0.045},  
    {'y_position': 250, 'scale_factor': 0.033},
    {'y_position': 350, 'scale_factor': 0.045},  
    
]

# Inicializa o rastreador SORT
tracker = Sort(max_age=5, min_hits=2, iou_threshold=0.3)

# Dicionários para armazenar posições, tempos de início e médias móveis de velocidades
velocidades = {}
media_velocidades = {}
inicializar_tempo = {}
ultimo_tempo_mostrado = {}
ultimo_valor_exibido = {}

# Tamanho da média móvel para suavizar a velocidade
window_size = 20  # Tamanho da janela da média móvel
delay_para_media = 0.5  # Delay de 0.5 segundos

# Função para desenhar as linhas de profundidade
def draw_depth_lines(frame, depth_lines):
    for line in depth_lines:
        y = line['y_position']
        cv2.line(frame, (0, y), (frame.shape[1], y), (0, 0, 255), 1)  # Linhas amarelas
        cv2.putText(frame, f"Scale: {line['scale_factor']:.3f}", 
                    (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

# Função para determinar o scale factor com base na posição y
def get_scale_factor(y_position, depth_lines):
    for line in depth_lines:
        if y_position <= line['y_position']:
            return line['scale_factor']
    return depth_lines[-1]['scale_factor']  # Retorna o scale factor da última linha se fora do alcance

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 360))

    # Desenha as linhas de profundidade no vídeo
    #draw_depth_lines(frame, depth_lines)

    # Detecção de veículos usando YOLO
    results = model(frame)
    detections = results[0].boxes.data.cpu().numpy()

    # Filtra apenas os veículos
    vehicles = [d for d in detections if int(d[5]) in [2, 5, 7, 3]]

    # Formata as detecções para o rastreador SORT
    dets = []
    for vehicle in vehicles:
        x1, y1, x2, y2, confidence, cls_id = vehicle[:6]
        dets.append([x1, y1, x2, y2, confidence])

    dets = np.array(dets)
    if len(dets) > 0:
        tracks = tracker.update(dets)
    else:
        tracks = []

    # Processa cada rastreamento
    for track in tracks:
        x1, y1, x2, y2, track_id = track.astype(int)
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        # Determina o scale factor baseado na posição y
        current_scale_factor = get_scale_factor(center_y, depth_lines)

        # Inicializa o tempo de rastreamento
        if track_id not in inicializar_tempo:
            inicializar_tempo[track_id] = time.time()

        # Atualiza a posição do veículo
        if track_id not in velocidades:
            velocidades[track_id] = deque(maxlen=2)
        velocidades[track_id].append((center_x, center_y))

        # Calcula a velocidade
        if len(velocidades[track_id]) == 2:
            (x_prev, y_prev), (x_curr, y_curr) = velocidades[track_id]
            pixel_distance = np.sqrt((x_curr - x_prev) ** 2 + (y_curr - y_prev) ** 2)
            distance_m = pixel_distance * current_scale_factor
            speed_m_s = distance_m * fps
            speed_kmh = speed_m_s * 3.6

            # Adiciona a velocidade no deque de média móvel
            if track_id not in media_velocidades:
                media_velocidades[track_id] = deque(maxlen=window_size)
            media_velocidades[track_id].append(speed_kmh)

            # Calcula a média móvel e exibe se passou o delay especificado
            if track_id not in ultimo_tempo_mostrado:
                ultimo_tempo_mostrado[track_id] = 0

            tempo_atual = time.time()
            if (tempo_atual - ultimo_tempo_mostrado[track_id]) >= delay_para_media:
                average_speed_kmh = np.mean(media_velocidades[track_id])

                if average_speed_kmh > 0 and average_speed_kmh < 200:
                    ultimo_valor_exibido[track_id] = int(average_speed_kmh)
                    ultimo_tempo_mostrado[track_id] = tempo_atual
                    if average_speed_kmh > 40:
                        print(f"{track_id},{ultimo_valor_exibido[track_id]}")
                        with open("velocidades_carros.txt", "a") as f:
                            f.write(f"{track_id}, {ultimo_valor_exibido[track_id]}\n")

        if track_id in ultimo_valor_exibido:
            cv2.putText(frame, f"{ultimo_valor_exibido[track_id]} km/h", (center_x, center_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow('Detecção de Carros e Velocidade', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
