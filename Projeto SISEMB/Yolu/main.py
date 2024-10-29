import torch
import cv2
import numpy as np
import time

# Função para calcular dois pontos
def calculate_distance(point1, point2):
    return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# Função para calcular o fator de escala usando estimativa de profundidade
def get_depth_scale(depth_map, bounding_box):
    x1, y1, x2, y2 = map(int, bounding_box)
    object_depth = depth_map[y1:y2, x1:x2].mean()
    return max(1 / (object_depth * 50), 0.0001)

# Função principal para detecção e cálculo da velocidade com rastreamento de objetos
def detect_speed(video_path):
    cap = cv2.VideoCapture(video_path)
    previous_centroid = {}
    previous_time = {}

    # Carregando o modelo YOLOv5 e MiDaS para profundidade
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
    midas_transform = torch.hub.load("intel-isl/MiDaS", "transforms").default_transform

    # Configurando o MiDaS para GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas.to(device)
    midas.eval()

    # Dicionário para armazenar rastreadores de cada carro
    trackers = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Reduzir a resolução e definir a ROI
        frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))
        height, width = frame.shape[:2]
        roi_x1, roi_y1, roi_x2, roi_y2 = int(0.25 * width), int(0.4 * height), int(0.75 * width), int(0.9 * height)
        roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]
        gray_frame = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        gray_frame_colored = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        # Processar profundidade com MiDaS
        input_batch = midas_transform(gray_frame_colored).to(device)
        with torch.no_grad():
            depth_map = midas(input_batch)
            depth_map = torch.nn.functional.interpolate(
                depth_map.unsqueeze(1),
                size=gray_frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        depth_map = depth_map.cpu().numpy()

        # YOLO: Detectar apenas carros em novas frames para adicionar ao rastreador
        if len(trackers) == 0:
            results = model(gray_frame_colored)
            detections = results.xyxy[0].cpu().numpy()

            for detection in detections:
                x1, y1, x2, y2, conf, cls = detection
                if cls == 2 and conf > 0.4:
                    x1, y1, x2, y2 = int(x1) + roi_x1, int(y1) + roi_y1, int(x2) + roi_x1, int(y2) + roi_y1
                    bbox = (x1, y1, x2 - x1, y2 - y1)
                    tracker = cv2.TrackerKCF_create()  # Cria um rastreador para cada carro(melhorando a leitura individual)
                    tracker.init(frame, bbox)
                    car_id = f"{int(x1)}-{int(y1)}"
                    trackers[car_id] = tracker

                    # Inicializar o rastreador para o carro detectado
                    previous_centroid[car_id] = ((x1 + x2) / 2, (y1 + y2) / 2)
                    previous_time[car_id] = time.time()

        # Atualizar as detecções de rastreamento
        for car_id, tracker in list(trackers.items()):
            ok, new_box = tracker.update(frame)
            if ok:
                x1, y1, w, h = [int(v) for v in new_box]
                x2, y2 = x1 + w, y1 + h
                centroid = ((x1 + x2) / 2, (y1 + y2) / 2)

                # Calcular o fator de escala com base na profundidade
                scale_factor = get_depth_scale(depth_map, (x1 - roi_x1, y1 - roi_y1, x2 - roi_x1, y2 - roi_y1))

                # Cálculo de velocidade
                if car_id in previous_centroid:
                    current_time = time.time()
                    time_diff = current_time - previous_time[car_id]
                    if time_diff > 0.1:  # Adcionei para melhorar a leitura pois estava travando muito
                        distance = calculate_distance(previous_centroid[car_id], centroid)
                        real_world_distance = distance * scale_factor
                        speed_m_s = real_world_distance / time_diff
                        speed_kmh = speed_m_s * 3.6

                        # Desenhar a caixa e exibir a velocidade
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, f'{speed_kmh:.2f} km/h', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Atualizar para o próximo quadro
                        previous_centroid[car_id] = centroid
                        previous_time[car_id] = current_time
            else:
                # Remove o rastreador se a atualização falhar
                trackers.pop(car_id, None)
                previous_centroid.pop(car_id, None)
                previous_time.pop(car_id, None)

        # Exibir o frame completo com ROI e detecções
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

video_path = "test2.mp4"
detect_speed(video_path)
