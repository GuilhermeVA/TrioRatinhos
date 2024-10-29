import torch
import cv2
import numpy as np
import time

# Função para calcular a distância Euclidiana entre dois pontos
def calculate_distance(point1, point2):
    return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# Função para calcular o fator de escala usando estimativa de profundidade
def get_depth_scale(depth_map, bounding_box):
    x1, y1, x2, y2 = map(int, bounding_box)
    object_depth = depth_map[y1:y2, x1:x2].mean()
    return 1 / (object_depth * 100)  # Ajuste o valor conforme necessário para o seu caso

# Função principal para detecção e cálculo da velocidade
def detect_speed(video_path):
    cap = cv2.VideoCapture(video_path)  # Abre o vídeo
    previous_centroid = {}
    previous_time = {}

    # Carregando o modelo YOLOv5 e MiDaS para profundidade
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # YOLOv5 para detecção
    midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")  # MiDaS para profundidade
    midas_transform = torch.hub.load("intel-isl/MiDaS", "transforms").default_transform

    # Configurando o MiDaS para execução na GPU, se disponível
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas.to(device)
    midas.eval()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Reduzir a resolução do quadro para metade
        frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

        # Definir uma região de interesse (ROI) no centro da tela para processamento
        height, width = frame.shape[:2]
        roi_x1, roi_y1, roi_x2, roi_y2 = int(0.25 * width), int(0.4 * height), int(0.75 * width), int(0.9 * height)
        roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        # Converter o quadro da ROI para escala de cinza para otimizar o cálculo de profundidade
        gray_frame = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        gray_frame_colored = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        # Processamento de profundidade com MiDaS na ROI
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

        # Detecção com YOLO apenas dentro da ROI
        results = model(gray_frame_colored)
        detections = results.xyxy[0].cpu().numpy()

        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            if cls == 2:  # Classe "carro" em YOLOv5
                # Ajustar coordenadas para a região de interesse
                x1, y1, x2, y2 = x1 + roi_x1, y1 + roi_y1, x2 + roi_x1, y2 + roi_y1
                centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
                car_id = f"{int(x1)}-{int(y1)}"

                # Calcular o fator de escala com base na profundidade da ROI
                scale_factor = get_depth_scale(depth_map, (x1 - roi_x1, y1 - roi_y1, x2 - roi_x1, y2 - roi_y1))

                if car_id in previous_centroid:
                    # Calcule a velocidade em km/h
                    current_time = time.time()
                    time_diff = current_time - previous_time[car_id]
                    distance = calculate_distance(previous_centroid[car_id], centroid)
                    real_world_distance = distance * scale_factor
                    speed_m_s = real_world_distance / time_diff
                    speed_kmh = speed_m_s * 3.6

                    # Desenhar a caixa de detecção e exibir a velocidade em km/h
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                    cv2.putText(frame, f'{speed_kmh:.2f} km/h', (int(x1), int(y1)-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Atualizar as variáveis para o próximo quadro
                previous_centroid[car_id] = centroid
                previous_time[car_id] = time.time()

        # Desenhar o contorno da ROI na tela
        cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 255), 2)
        
        # Exibir o frame completo com a ROI e detecções
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# URL ou caminho do vídeo a ser analisado
video_path = "test_video.mp4"

# Executa a função principal com o vídeo
detect_speed(video_path)
