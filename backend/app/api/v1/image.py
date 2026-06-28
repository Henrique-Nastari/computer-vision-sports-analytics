from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import Response
import cv2
import numpy as np

router = APIRouter()

@router.post("/analyze/image")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    """
    Recebe uma imagem, passa pelo modelo YOLO e devolve a imagem com os bounding boxes desenhados.
    """
    # 1. Lemos os bytes do arquivo enviado
    contents = await file.read()
    
    # 2. Convertendo os bytes brutos para o formato de imagem do OpenCV (Numpy Array)
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Pegamos nosso "cérebro" (YOLO) que carregou na memória lá no main.py
    detector = request.app.state.detector
    
    # 3. Fazemos a Inferência e já recebemos o frame desenhado com K-Means
    annotated_frame = detector.detect_frame(frame)
    
    # 5. Convertemos a imagem anotada de volta para JPEG
    success, encoded_image = cv2.imencode('.jpg', annotated_frame)
    
    if not success:
        return Response(content="Erro ao codificar imagem", status_code=500)
        
    # 6. Devolvemos a imagem pro usuário como se fossemos um site!
    return Response(content=encoded_image.tobytes(), media_type="image/jpeg")
