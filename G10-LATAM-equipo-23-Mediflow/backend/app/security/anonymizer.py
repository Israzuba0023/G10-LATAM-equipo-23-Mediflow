import re
from typing import Dict, Tuple

class ClinicalDataAnonymizer:
    """
    Sanitizador de Dados Pessoais (PII) e de Saúde (PHI).
    Garante a conformidade com LGPD/HIPAA ao mascarar entidades antes de submeter ao LLM.
    """
    
    def __init__(self):
        # Padrões Regex para PII/PHI comuns em documentação clínica
        self.patterns = {
            "CPF_NIF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{9}[A-Z]{2}\d{3}\b",  # Padrões Brasil/Angola
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "TELEFONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}\b",
            "PRONTUARIO": r"\b(?:PRONT|REC|LAUDO)[-:\s]?\d{5,10}\b",
            "DATA_NASC": r"\b(?:0[1-9]|[12][0-9]|3[01])[-/](?:0[1-9]|1[012])[-/](?:19|20)\d{2}\b"
        }

    def anonymize_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Substitui PIIs detectadas por tokens neutros e retorna o texto seguro 
        junto com o mapa de mapeamento (para reconstrução local se necessário).
        """
        anonymized_text = text
        mapping_registry = {}
        counter = 1

        for entity_type, pattern in self.patterns.items():
            matches = set(re.findall(pattern, anonymized_text, flags=re.IGNORECASE))
            for match in matches:
                placeholder = f"[{entity_type}_{counter}]"
                mapping_registry[placeholder] = match
                anonymized_text = anonymized_text.replace(match, placeholder)
                counter += 1

        return anonymized_text, mapping_registry

    def deanonymize_text(self, text: str, mapping_registry: Dict[str, str]) -> str:
        """
        Reconstrói os dados originais no output final sanitizado do agente.
        """
        restored_text = text
        for placeholder, original_value in mapping_registry.items():
            restored_text = restored_text.replace(placeholder, original_value)
        return restored_text