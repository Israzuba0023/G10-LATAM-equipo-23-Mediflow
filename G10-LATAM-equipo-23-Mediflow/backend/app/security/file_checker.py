from typing import Tuple

class SecureFileValidator:
    """
    Inspeção profunda de anexos enviados para triagem médica.
    """

    MAGIC_BYTES = {
        "pdf": b"%PDF",
        "png": b"\x89PNG\r\n\x1a\n",
        "jpeg": b"\xff\xd8\xff",
    }

    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    MAX_FILE_SIZE_MB = 15

    @classmethod
    def validate_upload(cls, filename: str, file_bytes: bytes) -> Tuple[bool, str]:
        # 1. Validação de Tamanho
        if len(file_bytes) > cls.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, f"Arquivo excede o tamanho máximo permitido ({cls.MAX_FILE_SIZE_MB}MB)."

        # 2. Validação de Extensão
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"Extensão de arquivo não permitida: '.{ext}'"

        # 3. Validação de Magic Bytes (Cabeçalho Binário Real)
        is_magic_valid = False
        if ext == "pdf" and file_bytes.startswith(cls.MAGIC_BYTES["pdf"]):
            is_magic_valid = True
        elif ext == "png" and file_bytes.startswith(cls.MAGIC_BYTES["png"]):
            is_magic_valid = True
        elif ext in ["jpg", "jpeg"] and file_bytes.startswith(cls.MAGIC_BYTES["jpeg"]):
            is_magic_valid = True

        if not is_magic_valid:
            return False, "Assinatura do arquivo (Magic Bytes) incompatível com a extensão informada. Upload rejeitado por segurança."

        return True, "Arquivo validado com sucesso."