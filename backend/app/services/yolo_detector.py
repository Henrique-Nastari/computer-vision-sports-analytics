from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

class YoloDetector:
    def __init__(self, weights_path: str = "weights/yolo11_football.pt"):
        self.weights_path = Path(weights_path)
        if not self.weights_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado em: {self.weights_path}")
        
        # Carrega o modelo YOLO11 (otimizado para inferência rápida)
        self.model = YOLO(str(self.weights_path))
        print("✅ Modelo YOLO11 carregado com sucesso na memória!")

    def get_team_by_color(self, image_crop: np.ndarray):
        """
        Abordagem ultra-robusta com Máscaras HSV:
        Em vez de calcular a média (o que quebra o Vermelho pois ele fica nas pontas 0 e 180 do círculo),
        nós contamos quantos pixels da camisa caem exatamente na faixa de cor de cada time!
        """
        # Converte a imagem (BGR) para HSV
        hsv_crop = cv2.cvtColor(image_crop, cv2.COLOR_BGR2HSV)
        
        # Máscara para Amarelo (Brasil)
        # Ajustamos a saturação e o brilho para pegar inclusive na sombra
        yellow_mask = cv2.inRange(hsv_crop, np.array([15, 50, 50]), np.array([35, 255, 255]))
        
        # Máscara para Vermelho (Marrocos)
        # O Vermelho no OpenCV é chato, ele fica no começo (0-10) e no fim (160-180) do disco
        red_mask1 = cv2.inRange(hsv_crop, np.array([0, 50, 50]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(hsv_crop, np.array([160, 50, 50]), np.array([180, 255, 255]))
        
        # Máscara para Preto (Árbitro)
        # Ignora a cor (0-180), mas exige que seja muito escuro (Value < 50)
        black_mask = cv2.inRange(hsv_crop, np.array([0, 0, 0]), np.array([180, 255, 50]))
        
        # Conta a quantidade de pixels que acenderam em cada máscara
        y_count = cv2.countNonZero(yellow_mask)
        r_count = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
        b_count = cv2.countNonZero(black_mask)
        
        # Se não achou quase nada de nenhum (ex: pura grama verde, erro do crop)
        if max(y_count, r_count, b_count) < 10:
            return "Jogador", (150, 150, 150)
            
        # Descobre quem ganhou a "eleição" de pixels
        counts = {"Brasil": y_count, "Marrocos": r_count, "Arbitro": b_count}
        best_team = max(counts, key=counts.get)
        
        if best_team == "Brasil":
            return "Brasil", (0, 255, 255) # BGR
        elif best_team == "Marrocos":
            return "Marrocos", (0, 0, 255) # BGR
        else:
            return "Arbitro", (0, 0, 0)

    def detect_frame(self, frame: np.ndarray, conf_threshold: float = 0.15):
        """
        Processa um frame. Baixamos a confiança global para 0.15 para tentar 'pescar' a bola.
        """
        results = self.model.predict(source=frame, conf=conf_threshold, device=0, verbose=False)[0]
        
        annotated_frame = frame.copy()
        
        for box in results.boxes:
            # Pega as coordenadas e o nome da classe
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            class_name = self.model.names[cls_id]
            conf = float(box.conf[0])
            
            # Filtragem de confiança customizada
            is_ball = "ball" in class_name.lower()
            
            # Se for humano e tiver pouca certeza, ignoramos (evitar lixo)
            if not is_ball and conf < 0.40:
                continue
                
            # Bypass: Assumimos que tudo que não é bola é humano.
            if not is_ball:
                # Recorta o 'peito' do jogador (evitando cabeça, calção e chão)
                h = y2 - y1
                shirt_crop = frame[y1 + int(h*0.1): y1 + int(h*0.5), x1:x2]
                
                if shirt_crop.size == 0:
                    continue
                    
                # Descobre quem é pela cor no espaço HSV
                team_name, box_color = self.get_team_by_color(shirt_crop)
                
                label = f"{team_name} {conf:.2f}"
            else:
                # É a bola (Abaixamos a régua da bola para tentar achá-la)
                box_color = (255, 255, 255) # Branco para a bola
                label = f"Bola {conf:.2f}"
            
            # Desenha a caixa customizada
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
            
            # Fundo para o texto ficar legível
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + text_width, y1), box_color, -1)
            
            # Texto contrastante (branco ou preto dependendo do fundo)
            text_color = (0, 0, 0) if team_name == "Brasil" or "Bola" in label else (255, 255, 255)
            cv2.putText(annotated_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
            
        return annotated_frame
