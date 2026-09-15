import os


class EnviromentManager:

    def get_with_default(self, variable_name: str, default_value: str = None) -> str:
        value = os.getenv(variable_name)
        if value is None and default_value is not None:
            return default_value

        if value is None:
            raise ValueError(f"Environment variable '{variable_name}' not found.")

        return value

    def get_datajud_api_url(self) -> str:
        return self.get_with_default("DATAJUD_API_URL", "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search")

    def get_lmstudio_base_url(self) -> str:
        return self.get_with_default("LMSTUDIO_API_URL", "http://host.docker.internal:1234/v1")

    def get_lmstudio_api_key(self) -> str:
        return self.get_with_default("LMSTUDIO_API_KEY", "lm-studio")

    def get_lmstudio_model(self) -> str:
        return self.get_with_default("LMSTUDIO_MODEL", "expert/trt6-model") # Facade name

    def get_api_base_url(self) -> str:
        return self.get_with_default("API_BASE_URL", "http://api:8000")

    def get_log_errors(self):
        return (
            self.get_with_default("LOG_ERRORS", "false")
                .strip()
                .lower() in {"1", "true", "yes", "on"}
        )

    # Database configuration helper methods
    def get_postgres_host(self) -> str:
        return self.get_with_default("POSTGRES_HOST", "localhost")

    def get_postgres_db(self) -> str:
        return self.get_with_default("POSTGRES_DB", "trt6")

    def get_postgres_user(self) -> str:
        return self.get_with_default("POSTGRES_USER", "trt6")

    def get_postgres_password(self) -> str:
        return self.get_with_default("POSTGRES_PASSWORD", "trt6")

    def get_postgres_port(self) -> str:
        return self.get_with_default("POSTGRES_PORT", "5432")

    # SMTP configuration helper methods
    def get_smtp_host(self) -> str:
        return self.get_with_default("SMTP_HOST", "smtp.gmail.com")

    def get_smtp_port(self) -> int:
        return int(self.get_with_default("SMTP_PORT", "587"))

    def get_smtp_user(self) -> str:
        return self.get_with_default("SMTP_USER", "")

    def get_smtp_password(self) -> str:
        return self.get_with_default("SMTP_PASSWORD", "")

    def get_smtp_sender(self) -> str:
        return self.get_with_default("SMTP_SENDER", self.get_smtp_user())
