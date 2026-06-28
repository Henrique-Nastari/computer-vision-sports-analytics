.PHONY: setup extract-frames

# Cria o ambiente Conda
setup:
	conda env create -f environment.yml
	@echo "\nAmbiente 'soccer-cv' criado! Agora ative com: conda activate soccer-cv"

# Atalho para rodar a extração de frames (exemplo)
# Uso: make extract-frames VIDEO=data/raw/videos/minha_luta.mp4 INTERVAL=15
extract-frames:
	python backend/app/services/video_processor.py --video $(VIDEO) --interval $(INTERVAL)

# Atalho para baixar vídeos do YouTube forçando o formato MP4 (H.264)
# Uso: make download-video URL="link_do_video"
download-video:
	yt-dlp -f "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "data/raw/videos/futebol_teste.%(ext)s" $(URL)

# Roda o servidor back-end em modo de desenvolvimento
run-api:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

