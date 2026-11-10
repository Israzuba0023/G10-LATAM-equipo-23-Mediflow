from schemas import DocumentoExtraido
from app.schemas.clinical import DocumentoExtraido  # Atualizado!

LIMITE_CONFIANCA = 0.80

def rotear(doc: DocumentoExtraido) -> dict:
    c = doc.classificacao

    duvida = (
        c.score_confianca < LIMITE_CONFIANCA
        or c.tipo_documento == "Desconhecido"
        or c.nivel_prioridade == "Indefinido"
        or len(doc.campos_ilegiveis) > 0
    )

    if c.nivel_prioridade == "Urgente":
        return {
            "destino_principal": "Fila_Emergencia_Medica",
            "requer_auditoria_humana": duvida,
            "justificativa_roteamento": "Documento classificado como urgente.",
        }

    if duvida:
        return {
            "destino_principal": "Auditoria_Humana",
            "requer_auditoria_humana": True,
            "justificativa_roteamento": "Baixa confiança, dados ilegíveis ou classificação indefinida.",
        }

    return {
        "destino_principal": "Processado",
        "requer_auditoria_humana": False,
        "justificativa_roteamento": "Documento padrão, extração confiável.",
    }
