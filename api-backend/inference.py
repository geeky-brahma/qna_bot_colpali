import httpx
import json
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class InferenceBackend:
    """
    Client for communicating with GCP Cloud Functions inference backend.
    Handles ColPali embedding and LLM generation.
    """

    def __init__(self):
        self.url = settings.inference_function_url
        self.api_key = settings.inference_function_key
        self.timeout = 60

    async def query(
        self,
        text: str,
        subject: str,
        pdf_path: Optional[str] = None
    ) -> dict:
        """
        Send query to inference backend and get answer.
        
        Args:
            text: The user's query
            subject: The selected subject
            pdf_path: Path or reference to the PDF document
            
        Returns:
            dict with 'answer' and 'sourcePages'
        """
        try:
            payload = {
                "query": text,
                "subject": subject,
                "pdf_path": pdf_path or f"documents/{subject.lower().replace(' ', '_')}.pdf"
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.url}/query",
                    json=payload,
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "answer": result.get("answer", ""),
                        "sourcePages": result.get("source_pages", [])
                    }
                else:
                    logger.error(f"Inference backend error: {response.status_code}")
                    raise Exception(f"Inference backend returned {response.status_code}")

        except httpx.TimeoutException:
            logger.error("Inference backend timeout")
            raise Exception("Request to inference backend timed out")
        except Exception as e:
            logger.error(f"Error calling inference backend: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check if inference backend is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.url}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False


inference_backend = InferenceBackend()
