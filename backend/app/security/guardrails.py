import re
from typing import NamedTuple

class GuardrailVerdict(NamedTuple):
    is_safe: bool
    risk_score: float
    reason: str

class PromptGuardrail:
    """
    Motor de inspeção defensiva contra Injeção de Prompt Direta e Indireta (OWASP LLM01).
    """

    def __init__(self):
        # Assinaturas e vetores de ataque conhecidos contra agentes LLM
        self.suspicious_patterns = [
            (r"ignore\s+(previous|all)\s+instructions", 0.95, "Tentativa de substituição de contexto"),
            (r"you\s+are\s+now\s+a", 0.85, "Tentativa de alteração de persona / Jailbreak"),
            (r"system\s*prompt|show\s+me\s+your\s+instructions", 0.90, "Tentativa de vazamento de System Prompt"),
            (r"base64|eval\(|exec\(", 0.75, "Codificação maliciosa ou injeção de código"),
            (r"\[SYSTEM\]|\[ADMIN\]|<\|im_start\|>", 0.99, "Injeção de tags de controle de modelo"),
            (r"bypass\s+safety\s+filter", 0.90, "Tentativa explícita de bypass de segurança")
        ]

    def validate_input(self, input_text: str) -> GuardrailVerdict:
        """
        Analisa o texto antes de entregar ao LLM / Agente.
        """
        clean_text = input_text.strip()
        
        # 1. Checagem por assinaturas de injeção
        for pattern, score, reason in self.suspicious_patterns:
            if re.search(pattern, clean_text, flags=re.IGNORECASE):
                return GuardrailVerdict(
                    is_safe=False,
                    risk_score=score,
                    reason=f"Ataque bloqueado: {reason}"
                )

        # 2. Heurística de densidade de caracteres especiais (prevenção a fuzzing / estouro de janela)
        special_chars = set('@#$%^&*()_{}[]|\\<>~`')
        special_char_count = sum(1 for char in clean_text if char in special_chars)
        ratio = special_char_count / max(len(clean_text), 1)

        if ratio > 0.35 and len(clean_text) > 50:
            return GuardrailVerdict(
                is_safe=False,
                risk_score=0.80,
                reason="Alta densidade de caracteres especiais (Suspeita de Payload/Fuzzing)"
            )

        return GuardrailVerdict(is_safe=True, risk_score=0.0, reason="Input Limpo e Seguro")