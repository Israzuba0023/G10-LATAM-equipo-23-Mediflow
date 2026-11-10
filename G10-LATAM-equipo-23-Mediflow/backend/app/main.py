from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Imports do Core do Agente e Schemas
from app.agent.core import extrair
from app.agent.routing import rotear
from app.schemas.clinical import DocumentoExtraido

# Imports do Módulo de Segurança Defensiva
from app.security.file_checker import SecureFileValidator
from app.security.guardrails import PromptGuardrail
from app.security.anonymizer import ClinicalDataAnonymizer

app = FastAPI(
    title="MediFlow API - Triagem Clínica Segura",
    version="1.0.0",
    description="Backend para extração, roteamento e triagem de documentos clínicos com camadas defensivas anti-prompt injection e proteção de PII/PHI."
)

# 1. Configuração de CORS Rígido (Apenas Frontend Autorizado)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",  # Live Server / Ambiente Local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Inicialização das Instâncias de Segurança
guardrail = PromptGuardrail()
anonymizer = ClinicalDataAnonymizer()


@app.get("/health", tags=["Healthcheck"])
def health_check():
    """Endpoint para verificação do estado operacional da API."""
    return {"status": "ok", "service": "MediFlow Core API"}


@app.post("/api/v1/triage/text", tags=["Triagem"])
async def process_clinical_text(texto: str = Form(...)):
    """
    Processa e tria texto clínico enviado via formulário.
    Aplica filtros anti-prompt injection, anonimização LGPD/HIPAA e validação com o Agente LLM.
    """
    # Passo 1: Inspeção Defensiva contra Injeção de Prompt (OWASP LLM01)
    verdict = guardrail.validate_input(texto)
    if not verdict.is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "erro": "Inspecção de segurança rejeitou o texto",
                "motivo": verdict.reason,
                "risk_score": verdict.risk_score
            }
        )

    # Passo 2: Sanitização e Anonimização de Dados Sensíveis (PII/PHI)
    texto_anonimizado, mapa_pii = anonymizer.anonymize_text(texto)

    try:
        # Passo 3: Chamada ao Agente Inteligente (Gemini Structured Output)
        documento_extraido: DocumentoExtraido = extrair(texto_anonimizado)
        
        # Passo 4: Grafo/Regras de Roteamento Clínico
        decisao_roteamento = rotear(documento_extraido)

        # Passo 5: Reconstrução Segura de Dados (Desanonimização dos Outputs se necessário)
        # Se o paciente tiver nome mascarado, desanonimizamos apenas na resposta autorizada
        if documento_extraido.paciente.nome:
            documento_extraido.paciente.nome = anonymizer.deanonymize_text(
                documento_extraido.paciente.nome, mapa_pii
            )

        return {
            "sucesso": True,
            "seguranca": {
                "input_sanitizado": True,
                "pii_mascarada": len(mapa_pii) > 0
            },
            "dados_extraidos": documento_extraido.model_dump(),
            "decisao_roteamento": decisao_roteamento
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha durante o processamento do documento pelo Agente: {str(e)}"
        )


@app.post("/api/v1/triage/file", tags=["Triagem"])
async def process_clinical_file(
    file: UploadFile = File(...),
    texto_adicional: Optional[str] = Form(None)
):
    """
    Recebe anexos de documentos médicos, valida os Magic Bytes para prevenir malwares 
    e encaminha para o pipeline de segurança e extração.
    """
    contents = await file.read()

    # Passo 1: Validação Estrita do Ficheiro (Magic Bytes / Extensão / Tamanho)
    valido, msg_erro = SecureFileValidator.validate_upload(file.filename, contents)
    if not valido:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"erro": "Ficheiro Rejeitado", "motivo": msg_erro}
        )

    # Para ficheiros de texto/json lidos via formulário:
    if file.filename.endswith(('.txt', '.json')):
        texto_extraido = contents.decode('utf-8', errors='ignore')
        return await process_clinical_text(texto=texto_extraido)

    # Para imagens/PDFs (em integrações futuras com OCR Vision):
    return {
        "sucesso": True,
        "ficheiro": file.filename,
        "validacao_seguranca": "Magic Bytes validados com sucesso.",
        "mensagem": "Ficheiro pronto para o pipeline OCR Vision do backend."
    }