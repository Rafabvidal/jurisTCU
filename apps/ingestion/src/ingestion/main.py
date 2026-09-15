
from __future__ import annotations

from dateutil.parser import parse as parse_date
from shared.celery_client import app
from shared.constants import PDF_BUCKET, WORKER_LLM_TASK_NAME, WORKER_SCRAPPER_TASK_NAME
from shared.logger import get_logger
from shared.schemas.data_jud import SearchResponse

from ingestion.cli import IngestionParser
from ingestion.providers import DataProvider
from ingestion.submitter import ProcessSubmitter

logger = get_logger("ingestion_pipeline")

def get_topics():
    return [
        "Aposentadoria e Pensão",
        "Categoria Profissional Especial",
        "Contrato Individual de Trabalho",
        "Direito Coletivo do Trabalho",
        "Direito de Greve / Lockout",
        "Direito Individual do Trabalho",
        "Direito Sindical e Questões Análogas",
        "Duração do Trabalho",
        "Férias",
        "Outras Relações de Trabalho",
        "Prescrição",
        "Prescrição e Decadência no Direito do Trabalho",
        "Questões de Alta Complexidade, Grande Impacto e Repercussão",
        "Redução à Condição Análoga à de Escravo",
        "Rescisão do Contrato de Trabalho",
        "Rescisão do Contrato de Trabalho",
        "Responsabilidade Civil do Empregador",
        "Responsabilidade Solidária / Subsidiária",
        "Sentença Normativa",
        "Verbas Remuneratórias, Indenizatórias e Benefícios",
    ]


def mapear_processos(search_response: SearchResponse) -> list[dict]:
   result = []
   for model in search_response.hits.hits:
        dump = model.source.model_dump()

        dump["data_ajuizamento"] = (
            parse_date(model.source.data_ajuizamento)
            .date()
            .isoformat()
        )
        dump["data_hora_ultima_atualizacao"] = (
            parse_date(model.source.data_hora_ultima_atualizacao)
            .date()
            .isoformat()
        )
        dump["@timestamp"] = parse_date(model.source.timestamp).isoformat()

        result.append(dump)

   return result

def fetch_for_topic(provider: DataProvider, topic: str) -> list[dict]:
    search_response = provider.get_data_and_persist(topic)

    if not search_response:
        logger.warning(f"Sem resultados ou erro para '{topic}'")
        return None

    logger.info(f"Resposta para '{topic}': {len(search_response.hits.hits)} processos encontrados")

    return mapear_processos(search_response)


def main():
    args = IngestionParser()

    if args.pending_analise:
        submitter = ProcessSubmitter(pending_analise_api_url=args.pending_analise_api_url)
        processos_sem_analise = submitter.fetch_pending_analise()

        if processos_sem_analise is None:
            logger.error("Erro ao buscar processos sem analise na API")
            return

        logger.info(f"Processos sem analise encontrados: {len(processos_sem_analise)}")
        logger.info(f"Celery app: {app} | Task name: {WORKER_LLM_TASK_NAME} | Queue: llm_queue")

        dispatch_count = 0
        for processo in processos_sem_analise:
            object_name = f"{processo.numero_processo}_{processo.grau}.pdf"
            try:
                logger.info(
                    "Disparando worker-llm para processo %s grau %s object %s",
                    processo.numero_processo,
                    processo.grau,
                    object_name,
                )
                task_result = app.send_task(
                    WORKER_LLM_TASK_NAME,
                    kwargs={
                        "numero_processo": processo.numero_processo,
                        "grau": processo.grau,
                        "bucket_name": PDF_BUCKET,
                        "object_name": object_name,
                    },
                )
                logger.info(f"Task enviada com sucesso: task_id={task_result.id}")
                dispatch_count += 1
            except Exception as e:
                logger.error(f"Erro ao enviar task para {processo.numero_processo}: {e}", exc_info=True)

        logger.info(f"Total de tasks disparadas: {dispatch_count}/{len(processos_sem_analise)}")
        return

    if args.pending_pdf:
        submitter = ProcessSubmitter(pending_api_url=args.pending_api_url)
        pendentes = submitter.fetch_pending_pdf()

        if pendentes is None:
            logger.error("Erro ao buscar pendencias de PDF na API")
            return

        logger.info(f"Pendencias de PDF encontradas: {len(pendentes)}")
        for processo in pendentes:
            logger.info(
                "Disparando worker para processo %s grau %s",
                processo.numero_processo,
                processo.grau,
            )
            app.send_task(WORKER_SCRAPPER_TASK_NAME, args=[processo.numero_processo, processo.grau])

        return

    provider = args.get_cli_provider()
    topics = get_topics()


    todos_processos = []
    submitter = ProcessSubmitter()
    logger.info(f"Consultando {len(topics)} assuntos do CNJ...")

    for assunto in topics:
        processos = fetch_for_topic(provider, assunto)

        if not processos:
            continue

        todos_processos.extend(processos)
        n = len(processos) if processos else 0
        logger.info(f"  -> {n} processos encontrados para '{assunto}'")

        api_response = submitter.submit(processos)
        if api_response is None:
            logger.error(f"Erro ao enviar processos para API para '{assunto}'")
            return

        logger.info(f"Processos para '{assunto}' enviados com sucesso. Resposta: {len(api_response)} retornados")

    if args.trigger:
        for p in todos_processos:
            logger.info(f"Disparando worker para processo {p['numero_processo']} grau {p['grau']}")
            app.send_task(WORKER_SCRAPPER_TASK_NAME, args=[p["numero_processo"], p["grau"]])

if __name__ == "__main__":
    main()
