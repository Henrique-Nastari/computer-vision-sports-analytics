import cv2
import os
import argparse
from pathlib import Path

def extract_frames(video_path: str, output_dir: str, frame_interval: int = 30):
    """
    Extrai frames de um vídeo a cada `frame_interval` frames.
    Por exemplo, se o vídeo é 30 FPS e interval=30, extrai 1 frame por segundo.
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    
    if not video_path.exists():
        print(f"Erro: Vídeo não encontrado em {video_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Processando: {video_path.name} | FPS: {fps:.2f} | Total Frames: {total_frames}")
    
    count = 0
    saved_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if count % frame_interval == 0:
            # Salvar o frame em JPG de alta qualidade
            frame_filename = output_dir / f"{video_path.stem}_frame_{count:06d}.jpg"
            cv2.imwrite(str(frame_filename), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            saved_count += 1
            
        count += 1
        
    cap.release()
    print(f"Extração concluída! {saved_count} frames salvos em {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrator de Frames para Dataset de Sanda")
    parser.add_argument("--video", type=str, required=True, help="Caminho para o vídeo de entrada")
    parser.add_argument("--output", type=str, default="data/raw/frames", help="Diretório de saída")
    parser.add_argument("--interval", type=int, default=30, help="Salvar 1 frame a cada N frames")
    
    args = parser.parse_args()
    extract_frames(args.video, args.output, args.interval)
