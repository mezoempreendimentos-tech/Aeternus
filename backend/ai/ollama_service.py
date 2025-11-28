import httpx
import logging
import time
from backend.config.server_config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    async def generate(self, prompt: str) -> str:
        """
        Gera texto via Ollama e mede o tempo de resposta.
        """
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                # O payload deve ser limpo. Não enviamos 'context' se não for usado.
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
                
                logger.info(f"🤖 OLLAMA: Enviando solicitação... (Timeout: {self.timeout}s)")
                
                response = await client.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code != 200:
                    logger.error(f"❌ OLLAMA: Rejeitado em {elapsed:.2f}s (Erro {response.status_code}): {response.text}")
                    return "As vozes ancestrais estão confusas."
                    
                data = response.json()
                logger.info(f"✅ OLLAMA: Resposta recebida em {elapsed:.2f} segundos.")
                
                return data.get("response", "")

        except httpx.ConnectError:
            elapsed = time.time() - start_time
            logger.error(f"❌ OLLAMA: Falha de Conexão em {elapsed:.2f}s. Verifique se o Docker está rodando.")
            raise
        except httpx.ReadTimeout:
            elapsed = time.time() - start_time
            logger.error(f"⌛ OLLAMA: Timeout! A IA demorou mais de {elapsed:.2f}s para responder.")
            raise
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"💀 OLLAMA: Erro crítico após {elapsed:.2f}s: {e}")
            raise