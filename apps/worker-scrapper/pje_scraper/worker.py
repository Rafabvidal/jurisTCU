import tempfile

from pje_scraper import PjePipeline
from shared.celery_client import app
from shared.constants import PDF_BUCKET, WORKER_LLM_TASK_NAME, WORKER_SCRAPPER_TASK_NAME
from shared.logger import get_logger
from shared.s3_client import get_s3_client

client = get_s3_client()
logger = get_logger("worker_scrapper")


@app.task(name=WORKER_SCRAPPER_TASK_NAME)
def run_pipeline(numero: str, grau: str = "1", headless: bool = True):
    logger.info("Iniciando pipeline scraper: numero=%s grau=%s", numero, grau)
    pipeline = PjePipeline(headless=headless)
    session = pipeline.resolve(numero, grau=grau)
    response = pipeline.fetch_with_token(session)

    object_name = f"{session.numero_processo}_{session.grau}.pdf"

    client.create_bucket(PDF_BUCKET)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name
    client.upload_object(PDF_BUCKET, object_name, tmp_path)

    async_result = app.send_task(
        WORKER_LLM_TASK_NAME,
        kwargs={
            "numero_processo": session.numero_processo,
            "grau": session.grau,
            "bucket_name": PDF_BUCKET,
            "object_name": object_name,
        },
    )
    logger.info(
        "Task worker-llm disparada: task_id=%s numero=%s grau=%s object=%s",
        async_result.id,
        session.numero_processo,
        session.grau,
        object_name,
    )
