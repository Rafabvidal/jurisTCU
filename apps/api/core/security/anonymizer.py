import re


_CPF_PATTERN = re.compile(r"\b(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})\b")
_NAME_PATTERN = re.compile(
    r"\b([A-ZÀ-ÖÙ-Ý][a-zà-öù-ÿ]{2,}(?:\s+(?:de|do|da|dos|das|e)\s+)?(?:\s+[A-ZÀ-ÖÙ-Ý][a-zà-öù-ÿ]{2,})+)\b"
)


def mask_cpf(text: str) -> str:
    """Mascara CPFs no formato 123.456.789-00 → 123.***.***-00."""
    return _CPF_PATTERN.sub(r"\1.***.***-\4", text)


def mask_name(name: str) -> str:
    """Mascara um nome próprio: 'João Silva' → 'J*** S***'."""
    parts = name.split()
    masked = []
    for part in parts:
        if part.lower() in {"de", "do", "da", "dos", "das", "e"}:
            masked.append(part)
        elif len(part) > 1:
            masked.append(part[0] + "***")
        else:
            masked.append(part)
    return " ".join(masked)


def mask_names_in_text(text: str) -> str:
    """Detecta e mascara nomes próprios compostos em um texto."""
    def replacer(match: re.Match) -> str:
        return mask_name(match.group(0))
    return _NAME_PATTERN.sub(replacer, text)


def anonymize_text(text: str) -> str:
    """Aplica mascaramento de CPF e nomes em um texto."""
    result = mask_cpf(text)
    result = mask_names_in_text(result)
    return result
