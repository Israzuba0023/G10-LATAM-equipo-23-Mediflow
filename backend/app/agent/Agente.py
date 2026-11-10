)
from dotenv import load_dotenv
from google import genai
from google.genai import types
from roteamento import DocumentoExtraido
from app.schemas.clinical import DocumentoExtraido  # Atualizado!

load_dotenv()
client = genai.Client()

def extrair(texto: str) -> DocumentoExtraido:
    resp = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"Extraia os dados do documento. Não invente informações ausentes; use null.\n\n{texto}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DocumentoExtraido,
        ),
    )
    return resp.parsed
