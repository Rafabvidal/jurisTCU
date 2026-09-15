from core.services import sincronizar_processos_minio
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django management command to synchronize processes between MinIO PDFs and PostgreSQL DB."""

    help = (
        "Sincroniza os processos no banco de dados com os PDFs armazenados no MinIO. "
        "Permite importar processos faltantes, disparar análise de LLM ou limpar arquivos órfãos."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--status",
            action="store_true",
            help="Apenas exibe o status atual de sincronização (padrão).",
        )
        group.add_argument(
            "--import-missing",
            action="store_true",
            help="Importa processos órfãos (PDFs no MinIO sem registro no DB) e dispara processamento.",
        )
        group.add_argument(
            "--trigger-llm",
            action="store_true",
            help="Dispara a task do LLM worker para todos os processos no DB com PDF no MinIO mas sem análise.",
        )
        group.add_argument(
            "--cleanup-minio",
            action="store_true",
            help="Remove do MinIO todos os arquivos PDFs órfãos (que não existem no DB).",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa a simulação das ações sem persistir no banco ou remover do MinIO.",
        )
        parser.add_argument(
            "--no-trigger",
            action="store_true",
            help="Na importação, evita o envio de tasks do worker-llm para os novos processos criados.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== Iniciando Sincronizador MinIO ↔ Banco ==="))

        dry_run = options.get("dry_run", False)
        no_trigger = options.get("no_trigger", False)

        if dry_run:
            self.stdout.write(self.style.NOTICE("⚠️ [MODO DRY-RUN] Nenhuma alteração real será feita."))

        # Define the orchestration mode
        if options.get("import_missing"):
            modo = "import"
        elif options.get("trigger_llm"):
            modo = "trigger"
        elif options.get("cleanup_minio"):
            modo = "cleanup"
        else:
            modo = "status"

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
            res = sincronizar_processos_minio(
                modo=modo,
                dry_run=dry_run,
                no_trigger=no_trigger,
                stdout_writer=stdout_writer,
            )

            if "erro" in res:
                self.stdout.write(self.style.ERROR(f"❌ Sincronização interrompida devido a erro: {res['erro']}"))
                return

            self.stdout.write(self.style.SUCCESS("\n=== Relatório de Sincronização ==="))
            self.stdout.write(f"Total PDFs no MinIO: {res['total_s3']}")
            self.stdout.write(f"Total Processos no DB: {res['total_db']}")
            self.stdout.write(self.style.SUCCESS(f"  -> Correspondidos (OK): {res['matched']}"))

            if res['orphaned'] > 0:
                self.stdout.write(self.style.WARNING(f"  -> Órfãos (Apenas S3): {res['orphaned']}"))
            else:
                self.stdout.write(self.style.SUCCESS("  -> Órfãos (Apenas S3): 0"))

            if modo == "import":
                self.stdout.write(self.style.SUCCESS(f"\n✅ Importados no DB: {res.get('importados', 0)}"))
                if not no_trigger:
                    self.stdout.write(self.style.SUCCESS(f"✅ Celery LLM Tasks Enviadas: {res.get('tasks_disparadas', 0)}"))
            elif modo == "trigger":
                self.stdout.write(self.style.SUCCESS(f"\n✅ Celery LLM Tasks Enviadas: {res.get('tasks_disparadas', 0)}"))
            elif modo == "cleanup":
                self.stdout.write(self.style.SUCCESS(f"\n✅ PDFs removidos do MinIO: {res.get('removidos', 0)}"))

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"❌ Erro inesperado durante execução: {exc}"))
            import traceback
            self.stdout.write(traceback.format_exc())
