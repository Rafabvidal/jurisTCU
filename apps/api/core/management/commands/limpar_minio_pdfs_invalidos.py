from django.core.management.base import BaseCommand
from shared.minio_cleanup import cleanup_minio_pdf_objects


class Command(BaseCommand):
    """Django management command to clean invalid MinIO PDF object names."""

    help = (
        "Remove do bucket do MinIO os arquivos que nao seguem o padrao `numero_grau.pdf` "
        "e remove nomes duplicados exatos como protecao adicional."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--bucket",
            default="pje-documents",
            help="Nome do bucket MinIO a ser limpo.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra o que seria removido sem apagar nada.",
        )

    def handle(self, *args, **options):
        bucket_name = options["bucket"]
        dry_run = options["dry_run"]

        self.stdout.write(self.style.WARNING("=== Iniciando limpeza de PDFs no MinIO ==="))

        result = cleanup_minio_pdf_objects(bucket_name=bucket_name, dry_run=dry_run)

        mode_label = "[DRY-RUN] " if dry_run else ""
        self.stdout.write(f"{mode_label}Bucket: {result['bucket']}")
        self.stdout.write(f"Total de objetos: {result['total']}")
        self.stdout.write(self.style.SUCCESS(f"Total removidos: {result['removed']}"))
        self.stdout.write(self.style.SUCCESS(f"  -> invalidos: {result['invalid_removed']}"))
        self.stdout.write(self.style.SUCCESS(f"  -> duplicados: {result['duplicate_removed']}"))

        if result["invalid_objects"]:
            self.stdout.write(self.style.WARNING("Arquivos invalidos removidos:"))
            for object_name in result["invalid_objects"]:
                self.stdout.write(f"- {object_name}")

        if result["duplicate_objects"]:
            self.stdout.write(self.style.WARNING("Arquivos duplicados removidos:"))
            for object_name in result["duplicate_objects"]:
                self.stdout.write(f"- {object_name}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("Executado em modo dry-run; nenhum arquivo foi apagado."))
