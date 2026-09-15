from celery import shared_task


@shared_task(bind=True, name="scraper.run_pipeline")
def run_pipeline(self, payload: dict) -> dict:
    """Celery task wrapper around the existing pipeline.
    *payload* is the JSON that would have been passed directly to
    `pje_scraper.worker.run_pipeline`. The function returns a JSON‑serialisable
    dictionary that Celery will send back to the caller.
    """
    # Local import keeps heavy deps out of the worker‑process startup.
    from .worker import run_pipeline as _run
    result = _run(payload)
    return result
