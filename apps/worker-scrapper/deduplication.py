from shared.celery_client import app


@app.task(name="pje_scraper.deduplication.run")
def deduplicate_processos():
    """Temporary cleanup for the MinIO bucket."""
    from shared.minio_cleanup import cleanup_minio_pdf_objects

    return cleanup_minio_pdf_objects()
