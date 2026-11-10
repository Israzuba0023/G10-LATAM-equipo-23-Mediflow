from pydantic import BaseModel, Field
from typing import Optional, Literal

class Paciente(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None

class Medico(BaseModel):
    nome: Optional[str] = None
    crm: Optional[str] = None

class Medicamento(BaseModel):
    nome: str
    dosagem: Optional[str] = None
    posologia: Optional[str] = None

class Classificacao(BaseModel):
    tipo_documento: Literal[
        "Receituario", "Laudo Laboratorial", "Laudo de Imagem",
        "Guia de Procedimento", "Relatorio de Alta", "Atestado", "Desconhecido"
    ]
    nivel_prioridade: Literal["Rotina", "Urgente", "Indefinido"]
    score_confianca: float = Field(ge=0, le=1)

class DocumentoExtraido(BaseModel):
    classificacao: Classificacao
    paciente: Paciente
    medico_solicitante: Medico
    diagnostico_principal: Optional[str] = None
    cid_sugerido: Optional[str] = None
    medicamentos: list[Medicamento] = []
    exames_solicitados: list[str] = []
    campos_ilegiveis: list[str] = []