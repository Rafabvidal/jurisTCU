from core.services import atualizar_movimentos_processos
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django management command to update process movements from the DataJud API (TRT6)."""

    help = (
        "Busca na API pública do DataJud (TRT6) as movimentações de todos os processos "
        "cadastrados no banco de dados e as atualiza usando compressão zlib para otimização de espaço."
    )

    def handle(self, *args, **options):
        # standard wrapper for printing with styles
        def stdout_writer(msg, style=None):
            if style == "error":
                self.stdout.write(self.style.ERROR(msg))
            elif style == "warning":
                self.stdout.write(self.style.WARNING(msg))
            elif style == "success":
                self.stdout.write(self.style.SUCCESS(msg))
            elif style == "notice":
                self.stdout.write(self.style.NOTICE(msg))
            else:
                self.stdout.write(msg)

        try:
            res = atualizar_movimentos_processos(stdout_writer=stdout_writer)

            total = res.get("total", 0)
            atualizados = res.get("atualizados", 0)
            erros = res.get("erros", 0)

            self.stdout.write("\n=== Relatório de Atualização de Movimentos ===")
            self.stdout.write(f"Total de processos no banco: {total}")
            self.stdout.write(self.style.SUCCESS(f"  -> Atualizados com sucesso: {atualizados}"))
            if erros > 0:
                self.stdout.write(self.style.WARNING(f"  -> Erros ou não localizados: {erros}"))
            else:
                self.stdout.write(self.style.SUCCESS("  -> Erros ou não localizados: 0"))

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"❌ Erro inesperado durante execução: {exc}"))
            import traceback
            self.stdout.write(traceback.format_exc())
