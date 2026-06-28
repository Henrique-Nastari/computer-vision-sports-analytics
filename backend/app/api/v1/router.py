from fastapi import APIRouter
from backend.app.api.v1 import image

router = APIRouter()

# Registra a rota /analyze/image
router.include_router(image.router, tags=["Análise de Imagem"])

@router.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    """
    return {
        "status": "online", 
        "message": "Servidor rodando e pronto para receber vídeos! ⚽"
    }
