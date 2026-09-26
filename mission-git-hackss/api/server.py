"""REST API server"""

import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from core.engine import ExploitEngine
from core.challenge import Challenge


class ChallengeRequest(BaseModel):
    """Challenge solving request"""
    name: str
    category: Optional[str] = None
    description: str = ""
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None


class ChallengeResponse(BaseModel):
    """Challenge solving response"""
    success: bool
    flag: Optional[str] = None
    error: Optional[str] = None
    method: Optional[str] = None
    duration: float


class APIServer:
    """FastAPI server for MD-EXPLOIT-ENGINE"""
    
    def __init__(self, config, host: str = '127.0.0.1', port: int = 5000):
        self.config = config
        self.host = host
        self.port = port
        self.logger = logging.getLogger('md-exploit-engine.api')
        
        self.app = FastAPI(
            title="MD-EXPLOIT-ENGINE API",
            description="Automated CTF Challenge Solver API",
            version="1.0.0"
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.get('api.cors_origins', ['*']),
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        
        self.engine = ExploitEngine(config)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get('/')
        async def root():
            return {
                'name': 'MD-EXPLOIT-ENGINE',
                'version': '1.0.0',
                'status': 'running'
            }
        
        @self.app.post('/solve', response_model=ChallengeResponse)
        async def solve_challenge(request: ChallengeRequest):
            """Solve a CTF challenge"""
            try:
                challenge = Challenge(
                    name=request.name,
                    category=request.category,
                    description=request.description,
                    url=request.url,
                    host=request.host,
                    port=request.port
                )
                
                result = self.engine.solve_challenge(
                    challenge.name,
                    category=challenge.category
                )
                
                return ChallengeResponse(
                    success=result.success,
                    flag=result.flag,
                    error=result.error,
                    method=result.method,
                    duration=result.duration
                )
            
            except Exception as e:
                self.logger.exception(f"Error solving challenge: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get('/health')
        async def health():
            return {'status': 'healthy'}
    
    def run(self):
        """Start API server"""
        self.logger.info(f"Starting API server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
