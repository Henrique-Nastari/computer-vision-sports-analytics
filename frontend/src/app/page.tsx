"use client";

import React, { useState, useRef } from 'react';

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MOCK_TRAJECTORIES: Record<string, { x: number; y: number }[]> = {
    "Neymar": [ { x: 50, y: 50 }, { x: 45, y: 60 }, { x: 40, y: 70 }, { x: 35, y: 65 }, { x: 20, y: 80 } ],
    "10": [ { x: 50, y: 50 }, { x: 45, y: 60 }, { x: 40, y: 70 }, { x: 35, y: 65 }, { x: 20, y: 80 } ],
    "Camisa 10 Brasil": [ { x: 50, y: 50 }, { x: 45, y: 60 }, { x: 40, y: 70 }, { x: 35, y: 65 }, { x: 20, y: 80 } ],
    "Messi": [ { x: 80, y: 20 }, { x: 75, y: 30 }, { x: 60, y: 35 }, { x: 50, y: 40 }, { x: 40, y: 45 } ],
    "7": [ { x: 80, y: 20 }, { x: 75, y: 30 }, { x: 60, y: 35 }, { x: 50, y: 40 }, { x: 40, y: 45 } ],
    "Camisa 7 Brasil": [ { x: 80, y: 20 }, { x: 75, y: 30 }, { x: 60, y: 35 }, { x: 50, y: 40 }, { x: 40, y: 45 } ]
  };

  const getTrajectory = () => {
    const key = Object.keys(MOCK_TRAJECTORIES).find(k => k.toLowerCase() === searchQuery.toLowerCase());
    return key ? MOCK_TRAJECTORIES[key] : null;
  };
  
  const playerTrajectory = getTrajectory();

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Chamada para a nossa FastAPI local!
      const response = await fetch('http://localhost:8000/api/v1/analyze/image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Falha ao processar a imagem na API');
      }

      // Recebe a imagem processada como Blob
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setProcessedImageUrl(imageUrl);
      
    } catch (error) {
      console.error(error);
      alert('Erro ao conectar com a API. A FastAPI está rodando?');
    } finally {
      setIsUploading(false);
    }
  };
  return (
    <main className="dashboard-container">
      <header className="dashboard-header">
        <div className="logo-section">
          <div className="pulse-dot"></div>
          <h1>SoccerCV Analytics</h1>
        </div>
        <nav>
          <input 
            type="file" 
            accept="image/*" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
          />
          <button 
            className="btn-primary" 
            onClick={handleUploadClick}
            disabled={isUploading}
          >
            {isUploading ? 'Processando na IA...' : 'Testar Imagem na API Local'}
          </button>
        </nav>
      </header>

      {/* Modal / Área flutuante para a Imagem Processada da API local */}
      {processedImageUrl && (
        <div className="api-result-modal glass-panel">
          <header className="panel-header">
            <h2>Resultado da API (YOLO Local)</h2>
            <button className="btn-close" onClick={() => setProcessedImageUrl(null)}>✕</button>
          </header>
          <img src={processedImageUrl} alt="Processado pela API" className="processed-image" />
        </div>
      )}

      <div className="dashboard-grid">
        {/* Main Video Area */}
        <section className="video-section glass-panel">
          <header className="panel-header">
            <h2>Live Feed</h2>
            <span className="badge">Tracking Active</span>
          </header>
          <div className="video-player-container">
            <video 
              controls 
              autoPlay 
              loop 
              muted 
              className="main-video"
            >
              <source src="/videos/futebol_rastreado_h264.mp4" type="video/mp4" />
              Seu navegador não suporta vídeos HTML5.
            </video>
          </div>
        </section>

        {/* Sidebar / Minimap */}
        <aside className="sidebar-section">
          <div className="minimap-panel glass-panel">
            <header className="panel-header" style={{flexDirection: 'column', alignItems: 'flex-start', gap: '10px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', width: '100%'}}>
                <h2>Tactical Radar</h2>
              </div>
              <div className="search-box">
                <input 
                  type="text" 
                  placeholder="Buscar jogador (ex: Neymar)..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="player-search-input"
                />
              </div>
            </header>
            <div className="minimap-placeholder">
              <div className="pitch-lines">
                <div className="center-circle"></div>
                <div className="half-way-line"></div>
              </div>
              <svg className="trajectory-layer" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 10 }}>
                {playerTrajectory && (
                  <polyline 
                    points={playerTrajectory.map(pt => `${pt.x},${pt.y}`).join(' ')} 
                    fill="none" 
                    stroke="#00e5ff" 
                    strokeWidth="1" 
                    strokeDasharray="2"
                  />
                )}
                {playerTrajectory && playerTrajectory.map((pt, idx) => (
                  <circle key={idx} cx={pt.x} cy={pt.y} r="1.5" fill="#00e5ff" />
                ))}
              </svg>
            </div>
          </div>
          
          <div className="stats-panel glass-panel">
            <header className="panel-header">
              <h2>Match Stats</h2>
            </header>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Time A</span>
                <span className="stat-value">4</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Time B</span>
                <span className="stat-value">5</span>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <style jsx>{`
        .dashboard-container {
          padding: 32px;
          max-width: 1600px;
          margin: 0 auto;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
        }

        .logo-section {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .pulse-dot {
          width: 10px;
          height: 10px;
          background-color: var(--accent-primary);
          border-radius: 50%;
          animation: pulseGlow 2s infinite;
        }

        .dashboard-header h1 {
          font-size: 24px;
          background: linear-gradient(to right, #fff, #8b9bb4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 24px;
        }

        .player-search-input {
          width: 100%;
          padding: 8px 12px;
          border-radius: var(--radius-sm, 6px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          background: rgba(0, 0, 0, 0.3);
          color: white;
          font-size: 14px;
          outline: none;
          transition: border-color 0.3s;
        }
        
        .player-search-input:focus {
          border-color: var(--accent-primary, #00e5ff);
        }
        
        .search-box {
          width: 100%;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          border-bottom: 1px solid var(--bg-panel-border);
          padding-bottom: 12px;
        }

        .panel-header h2 {
          font-size: 16px;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .badge {
          background: rgba(0, 229, 255, 0.1);
          color: var(--accent-primary);
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
        }

        .video-player-container {
          aspect-ratio: 16/9;
          background: #000;
          border-radius: var(--radius-md);
          overflow: hidden;
          border: var(--glass-border);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .main-video {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .sidebar-section {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .minimap-placeholder {
          aspect-ratio: 2/3;
          background: #1a2332;
          border-radius: var(--radius-md);
          position: relative;
          overflow: hidden;
        }

        .pitch-lines {
          position: absolute;
          top: 10px; left: 10px; right: 10px; bottom: 10px;
          border: 2px solid rgba(255,255,255,0.1);
        }

        .center-circle {
          position: absolute;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          width: 60px; height: 60px;
          border: 2px solid rgba(255,255,255,0.1);
          border-radius: 50%;
        }

        .half-way-line {
          position: absolute;
          top: 50%; left: 0; right: 0;
          height: 2px;
          background: rgba(255,255,255,0.1);
        }

        .stats-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }

        .stat-card {
          background: rgba(0,0,0,0.2);
          padding: 16px;
          border-radius: var(--radius-sm);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
        }

        .stat-label {
          font-size: 12px;
          color: var(--text-muted);
        }

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: var(--accent-primary);
        }

        .api-result-modal {
          margin-bottom: 24px;
          border: 1px solid var(--accent-secondary);
          box-shadow: 0 0 20px rgba(255, 0, 85, 0.2);
        }

        .btn-close {
          background: transparent;
          color: white;
          border: none;
          font-size: 18px;
          cursor: pointer;
        }

        .processed-image {
          width: 100%;
          border-radius: var(--radius-sm);
          max-height: 400px;
          object-fit: contain;
          background: #000;
        }

        @media (max-width: 1024px) {
          .dashboard-grid {
            grid-template-columns: 1fr;
          }
          .minimap-placeholder {
            aspect-ratio: 16/9;
          }
        }
      `}</style>
    </main>
  );
}
