# Computer Vision Sports Analytics

[![Computer Vision](https://img.shields.io/badge/Computer_Vision-YOLO-blue.svg)]()
[![Python](https://img.shields.io/badge/Language-Python-green.svg)]()
[![OpenCV](https://img.shields.io/badge/Library-OpenCV-red.svg)]()

Um projeto válido como avaliação parcial da terceira unidade da disciplina de Aprendeizado de Máquina abordando Visão Computacional focado em análise tática esportiva (Futebol). Este repositório processa partidas de futebol extraindo dados sobre os jogadores, times e suas movimentações ao longo de todo o campo.

## 🚀 Funcionalidades

- **Rastreamento (Tracking) de Jogadores:** Utilizando o modelo YOLOv8 integrado ao ByteTrack para acompanhar os jogadores quadro a quadro sem perder a identidade de cada um.
- **Identificação de Times via Espectro de Cor (HSV):** Ao invés de fine-tuning custoso, extraímos o espectro superior (torso) dos jogadores e separamos as equipes (Brasil x Marrocos) e o árbitro de forma automatizada via máscaras de cor em HSV.
- **Geração Dinâmica de Trajetórias:** Desenho de um rastro dinâmico que segue a movimentação de todos os jogadores para evidenciar as linhas de ataque, passes e arranques físicos.
- **Mapa de Calor (Heatmap) Tático:** Um algoritmo que acumula os pontos centrais de movimentação e compila num Heatmap no final do processamento, evidenciando zonas de perigo, posse de bola e áreas mortas do campo.

## 🎥 Demonstração

![Demonstração do Rastreamento](./demo.gif)

> *Tracking completo: segmentação por times (Amarelo e Vermelho), detecção do árbitro (Preto) e desenho das linhas de movimentação, ignorando iluminação e sombras da grama!*

---

## 🛠️ Tecnologias Utilizadas

- `YOLOv8-Seg`: Segmentação instanciada state-of-the-art.
- `Supervision (Roboflow)`: Para detecção, tracking robusto (ByteTrack) e desenho das caixas.
- `OpenCV`: Processamento de imagem bruto e máscaras de cor HSV.
- `MoviePy`: Tratamento final, clipping e renderização em formato web (`h264`).

## 📁 Estrutura do Projeto

- `/notebooks/03_cv_tracking_pipeline.py`: O "coração" do projeto. Script completo de Visão Computacional que baixa, segmenta, rastreia e exporta o vídeo.
- `/frontend/`: Uma interface em React.js + Next.js onde você pode exibir os resultados (vídeo rastreado final) para o cliente final.
- `/data/`: Pasta designada para manter seus vídeos brutos e exports de peso.

## ⚙️ Como executar
1. Instale as dependências usando `pip install -r requirements.txt`.
2. Insira o vídeo desejado em `data/raw/videos/futebol_teste.mp4`.
3. Navegue até a pasta `notebooks` e execute `python 03_cv_tracking_pipeline.py`.
4. O resultado final será exportado em H.264 para uso direto na web.

---

