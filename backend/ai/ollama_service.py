# Serviço Ollama - Wrapper

import httpx
from backend.config.server_config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

class OllamaService:
    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    async def generate(self, prompt: str, context: str = "") -> str:
        """Gera texto via Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "context": context
                },
                timeout=self.timeout
            )
            return response.json()["response"]
