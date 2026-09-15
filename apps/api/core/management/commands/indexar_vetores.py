from django.core.management.base import BaseCommand

from core.services import reindexar_processos_sem_embedding


class Command(BaseCommand):
    """Django management command to batch calculate embeddings for existing processes that lack them."""

    help = (
        "Calcula e indexa os embeddings vetoriais no PostgreSQL para todos os processos "
        "que possuem análise estruturada mas ainda não foram vetorizados."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== Iniciando indexação em lote de embeddings ==="))

        try:
            count = reindexar_processos_sem_embedding()
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"✅ Sucesso: {count} processos foram indexados vetorialmente!"))
            else:
                self.stdout.write(self.style.SUCCESS("Nenhum processo pendente de indexação encontrado."))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"❌ Erro fatal durante a indexação: {exc}"))
