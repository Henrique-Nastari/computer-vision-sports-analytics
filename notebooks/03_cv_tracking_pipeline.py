import cv2
import numpy as np
import supervision as sv
import torch
from collections import defaultdict, Counter
from ultralytics import YOLO
from tqdm import tqdm

VIDEO_PATH = "../data/raw/videos/futebol_teste.mp4"
OUTPUT_PATH = "../data/raw/videos/futebol_cv_tracking.mp4"

# Cores: 0: Brasil (Amarelo), 1: Marrocos (Vermelho), 2: Arbitro (Preto)
# Usaremos BGR format for cv2
TEAM_COLORS = {
    0: (0, 255, 255),    # Yellow (BGR)
    1: (0, 0, 255),      # Red (BGR)
    2: (0, 0, 0)         # Black (BGR)
}
TEAM_NAMES = {0: "Brasil", 1: "Marrocos", 2: "Arbitro"}

yolo_model = YOLO('yolov8s-seg.pt')
if torch.cuda.is_available():
    yolo_model.to('cuda')

tracker = sv.ByteTrack()

def get_team_id(masked_player):
    h, w = masked_player.shape[:2]
    torso = masked_player[int(h*0.15):int(h*0.60), :]
    if torso.size == 0: return 2
    
    hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
    
    mask_red1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
    mask_red2 = cv2.inRange(hsv, np.array([160, 70, 50]), np.array([180, 255, 255]))
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_yellow = cv2.inRange(hsv, np.array([15, 70, 50]), np.array([35, 255, 255]))
    
    # Ignorar pixels de fundo [0,0,0] ajustando o limite inferior para V=1
    mask_black = cv2.inRange(hsv, np.array([0, 0, 1]), np.array([180, 255, 80]))
    
    counts = {
        0: cv2.countNonZero(mask_yellow),
        1: cv2.countNonZero(mask_red),
        2: cv2.countNonZero(mask_black)
    }
    
    if all(v == 0 for v in counts.values()): return 2
    return max(counts, key=counts.get)

cap = cv2.VideoCapture(VIDEO_PATH)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

tracker_team_memory = defaultdict(list)
trajectories = defaultdict(list)
heatmaps = {0: np.zeros((height, width), dtype=np.float32), 1: np.zeros((height, width), dtype=np.float32)}

print(f"Processando {total_frames} frames...")
for frame_index in tqdm(range(total_frames)):
    ret, frame = cap.read()
    if not ret: break
    
    # Detecção (classes=[0] = pessoa)
    results = yolo_model(frame, classes=[0], conf=0.4, verbose=False)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)
    
    if len(detections) == 0:
        out.write(frame)
        continue
    
    for i in range(len(detections)):
        tracker_id = detections.tracker_id[i]
        x1, y1, x2, y2 = detections.xyxy[i].astype(int)
        
        # Identificação de Time via HSV (somente nos primeiros 5 frames de aparição)
        if len(tracker_team_memory[tracker_id]) < 5:
            if detections.mask is not None:
                mask_crop = detections.mask[i][y1:y2, x1:x2]
                player_crop = frame[y1:y2, x1:x2]
                masked_player = cv2.bitwise_and(player_crop, player_crop, mask=mask_crop.astype(np.uint8))
                team_id = get_team_id(masked_player)
                tracker_team_memory[tracker_id].append(team_id)
        
        if len(tracker_team_memory[tracker_id]) > 0:
            final_team_id = Counter(tracker_team_memory[tracker_id]).most_common(1)[0][0]
        else:
            final_team_id = 2
            
        color = TEAM_COLORS[final_team_id]
        
        # Desenhar Box e Label
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"Jogador {tracker_id}" if final_team_id != 2 else "Arbitro"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Trajetórias e Heatmap (somente jogadores, ignorando árbitro para o heatmap)
        cx, cy = int((x1 + x2) / 2), int(y2)
        cx = min(max(cx, 0), width - 1)
        cy = min(max(cy, 0), height - 1)
        
        trajectories[tracker_id].append((cx, cy))
        
        if final_team_id != 2:
            heatmaps[final_team_id][cy, cx] += 1
        
        # Desenhar linha de trajetória (rastro de até 30 frames para não poluir muito)
        if len(trajectories[tracker_id]) >= 2:
            pts = trajectories[tracker_id][-30:]
            for j in range(1, len(pts)):
                cv2.line(frame, pts[j - 1], pts[j], color, 2)

    out.write(frame)

cap.release()
out.release()
print("Vídeo com Trajetórias concluído!")

# Gerar Heatmap Final
print("Gerando Heatmap Final...")
# Pegar um frame de fundo (usando o frame 100)
cap = cv2.VideoCapture(VIDEO_PATH)
cap.set(cv2.CAP_PROP_POS_FRAMES, 100)
ret, base_frame = cap.read()
cap.release()

if ret:
    overlay = base_frame.copy()
    alpha = 0.6
    
    # Aplicar GaussianBlur no heatmap para espalhar os pontos
    for team_id in [0, 1]:
        hm = heatmaps[team_id]
        hm = cv2.GaussianBlur(hm, (31, 31), 0)
        hm_norm = cv2.normalize(hm, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        colored = cv2.applyColorMap(hm_norm, cv2.COLORMAP_JET)
        
        # Mascara onde o heatmap é relevante
        mask = hm_norm > 10
        overlay[mask] = cv2.addWeighted(colored, alpha, overlay, 1 - alpha, 0)[mask]
        
    cv2.imwrite("../frontend/public/heatmap_final.png", overlay)
    print("Heatmap salvo em heatmap_final.png")
    
print("Convertendo para H.264...")
from moviepy import VideoFileClip
clip = VideoFileClip(OUTPUT_PATH)
clip.write_videofile("../frontend/public/videos/futebol_cv_tracking_h264.mp4", codec="libx264", audio_codec="aac")
print("Tudo concluído!")
