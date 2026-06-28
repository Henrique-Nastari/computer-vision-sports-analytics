from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import router as api_router
from backend.app.services.yolo_detector import YoloDetector

app = FastAPI(
    title="Soccer CV Analytics API",
    description="API para detecção e análise tática de futebol usando YOLOv11.",
    version="1.0.0"
)

# Configuração de CORS (Para o front-end Next.js conseguir fazer requisições)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, limitamos isso
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o modelo YOLO na subida do servidor
# (Armazenamos no state da aplicação para usar nos endpoints depois)
detector = None

@app.on_event("startup")
async def startup_event():
    global detector
    print("🚀 Iniciando servidor...")
    try:
        # Carregamos assumindo que o uvicorn será rodado na raiz do projeto
        detector = YoloDetector(weights_path="weights/best.pt")
        app.state.detector = detector
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível carregar o modelo YOLO no startup. Erro: {e}")

# Inclui as rotas da v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Soccer CV Analytics!"}
