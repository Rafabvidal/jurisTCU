import re
from decimal import Decimal, InvalidOperation


class BRLParser:
    """Parse common Brazilian currency formats into normalized Decimal objects."""

    THOUSAND_SEPARATOR = "."
    DECIMAL_SEPARATOR = ","
    NON_NUMERIC_REGEX = r"[^0-9.]"

    @classmethod
    def to_decimal(cls, currency_input: str) -> Decimal:
        """Main entry point to convert a Brazilian currency string into a Decimal."""
        normalized_str = cls.parse_to_decimal_string(currency_input)
        try:
            return Decimal(normalized_str)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal format after parsing: {normalized_str}") from exc

    @classmethod
    def parse_to_decimal_string(cls, currency_input: str) -> str:
        """Coordinates the sanitization, signal handling, and separator normalization."""
        cls._validate_input_presence(currency_input)

        cleaned_input = cls._sanitize_whitespace_and_currency_symbol(str(currency_input))
        is_negative, input_without_sign = cls._extract_negative_sign(cleaned_input)
        standardized_separators = cls._normalize_separators(input_without_sign)

        final_numeric_str = re.sub(cls.NON_NUMERIC_REGEX, "", standardized_separators)

        cls._validate_is_numeric(final_numeric_str, original_input=currency_input)

        return f"-{final_numeric_str}" if is_negative else final_numeric_str

    @staticmethod
    def _validate_input_presence(currency_input: str) -> None:
        if currency_input is None:
            raise ValueError("Value is None")
        if str(currency_input).strip() == "":
            raise ValueError("Empty string")

    @staticmethod
    def _sanitize_whitespace_and_currency_symbol(raw_string: str) -> str:
        """Removes 'R$', spaces, and non-breaking spaces."""
        # Remove case-insensitive 'R$'
        no_symbol = re.sub(r"(?i)r\$", "", raw_string)
        # Remove regular spaces and non-breaking spaces (\u00A0)
        return no_symbol.replace("\u00A0", "").replace(" ", "").strip()

    @staticmethod
    def _extract_negative_sign(cleaned_string: str) -> tuple[bool, str]:
        """Detects if the value is negative (either by '-' or '(...)') and returns the sign and the inner string."""
        if cleaned_string.startswith("(") and cleaned_string.endswith(")"):
            return True, cleaned_string[1:-1].strip()

        if cleaned_string.startswith("-"):
            return True, cleaned_string[1:].strip()

        return False, cleaned_string

    @classmethod
    def _normalize_separators(cls, numeric_string: str) -> str:
        """Converts Brazilian currency symbols (1.234,56) to standard float format (1234.56)."""
        has_thousand = cls.THOUSAND_SEPARATOR in numeric_string
        has_decimal = cls.DECIMAL_SEPARATOR in numeric_string

        if has_thousand and has_decimal:
            return numeric_string.replace(cls.THOUSAND_SEPARATOR, "").replace(cls.DECIMAL_SEPARATOR, ".")

        if has_decimal and not has_thousand:
            return numeric_string.replace(cls.DECIMAL_SEPARATOR, ".")

        return numeric_string

    @staticmethod
    def _validate_is_numeric(numeric_string: str, original_input: str) -> None:
        # Garante que sobrou algo e que esse algo possui apenas números e o ponto decimal
        digits_only = numeric_string.replace(".", "")
        if not digits_only or not digits_only.isdigit():
            raise ValueError(f"Could not parse numeric value: {original_input}")
