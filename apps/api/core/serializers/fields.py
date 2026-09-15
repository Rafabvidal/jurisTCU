from rest_framework import serializers
from shared.formatters.currency import BRLParser


class BRLDecimalField(serializers.DecimalField):
    """DecimalField that accepts common BRL-formatted strings and normalizes them.

    Accepts strings like "62,00", "62.000,00", "R$ 62.000,00", and parentheses for negatives.
    """

    def to_internal_value(self, data):
        # Allow None to be handled by parent
        if isinstance(data, str):
            s = data.strip()
            if s == "":
                return super().to_internal_value(data)
            try:
                normalized = BRLParser.parse_to_decimal_string(s)
            except Exception as e:
                raise serializers.ValidationError("Formato monetário inválido.") from e
            return super().to_internal_value(normalized)
        return super().to_internal_value(data)
