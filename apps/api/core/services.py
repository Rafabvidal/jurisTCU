
from collections.abc import Mapping, Sequence

from django.db.models import Q
from shared.logger import get_logger
from shared.s3_client import get_s3_client

from core.models.analise import Analise
from core.models.palavra_chave import PalavraChave
from core.models.processo import Processo

logger = get_logger("core.services")

PDF_BUCKET_NAME = "pje-documents"


class ProcessoSemPdfLookupError(Exception):
    """Raised when pending PDF lookup cannot be completed."""


class ProcessoNotFoundError(Exception):
    """Raised when process cannot be found for requested keys."""


def _normalize_grau(grau: str) -> str:
    raw = (grau or "").strip().upper()
    if raw.startswith("G") and len(raw) > 1:
        return raw[1:]
    return raw


def _s3_object_key(numero_processo: str, grau: str) -> str:
    return f"{numero_processo}_{_normalize_grau(grau)}.pdf"


def _s3_object_exists(client, bucket_name: str, object_name: str) -> bool:
    objects = client.list_objects(bucket_name, prefix=object_name, recursive=True)
    return any(getattr(item, "object_name", "") == object_name for item in objects)


def filtrar_processos_faltantes(
    dados_entrada: Sequence[dict],
) -> list[dict]:
    # Deduplica o lote por chave unica do modelo para evitar conflitos no mesmo request.
    # Em caso de repeticao da mesma chave, mantem o item mais recente.
    deduplicado_por_chave: dict[tuple[str, str, str], dict] = {}
    for item in dados_entrada:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )

        existente = deduplicado_por_chave.get(chave)
        if existente is None:
            deduplicado_por_chave[chave] = item
            continue

        data_nova = item.get("data_hora_ultima_atualizacao")
        data_existente = existente.get("data_hora_ultima_atualizacao")
        if data_nova and (data_existente is None or data_nova > data_existente):
            deduplicado_por_chave[chave] = item

    itens_deduplicados = list(deduplicado_por_chave.values())

    numeros_entrada: list[str] = [item["numero_processo"] for item in itens_deduplicados]

    if not numeros_entrada:
        return []

    processos_no_banco = Processo.objects.filter(numero_processo__in=numeros_entrada).values(
        "numero_processo",
        "tribunal",
        "grau",
    )

    chaves_banco: Mapping[tuple[str, str, str], bool] = {
        (item["numero_processo"], item["tribunal"], item["grau"]): True
        for item in processos_no_banco
    }

    def precisa_de_processamento(item: dict) -> bool:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )
        return chave not in chaves_banco

    return [item for item in itens_deduplicados if precisa_de_processamento(item)]


def listar_processos_nao_possuem_pdf() -> list[Processo]:
    client = get_s3_client()
    candidatos = Processo.objects.filter(Q(pdf_url__isnull=True) | Q(pdf_url="")).only(
        "numero_processo",
        "grau",
        "pdf_url",
    )

    pendentes: list[Processo] = []
    for processo in candidatos:
        object_name = _s3_object_key(processo.numero_processo, processo.grau)
        try:
            exists = _s3_object_exists(client, PDF_BUCKET_NAME, object_name)
        except Exception as exc:
            raise ProcessoSemPdfLookupError("Falha ao consultar objetos PDF no S3.") from exc

        if not exists:
            pendentes.append(processo)

    return pendentes


def listar_processos_com_analise() -> list[Processo]:
    return list(
        Processo.objects.filter(analise__isnull=False).only(
            "numero_processo",
            "grau",
            "analise",
        )
    )


def listar_processos_nao_possuem_analise() -> list[Processo]:
    return list(
        Processo.objects.filter(analise__isnull=True).only(
            "numero_processo",
            "grau",
            "analise",
        )
    )


def _normalize_grau_for_query(grau: str) -> set[str]:
    normalized = _normalize_grau(grau)
    if not normalized:
        return {""}
    return {normalized, f"G{normalized}"}


def _sanitize_palavras_chave(values: list[str]) -> list[str]:
    output: list[str] = []
    for raw in values:
        normalized = (raw or "").strip()
        if normalized:
            output.append(normalized)
    return output


def montar_texto_indexacao(processo: Processo) -> str:
    """Consolida os campos do processo e sua análise em uma string canônica formatada."""
    classe_nome = processo.classe.nome if processo.classe else ""
    orgao_julgador_nome = processo.orgao_julgador.nome if processo.orgao_julgador else ""

    # Concatena assuntos com ponto e vírgula
    assuntos_list = [assunto.nome for assunto in processo.assuntos.all() if assunto.nome]
    assuntos_str = "; ".join(assuntos_list)

    analise = processo.analise
    if not analise:
        return ""

    resumo = analise.resumo or ""
    decisao = analise.decisao or ""

    # Concatena palavras-chave com ponto e vírgula
    palavras_list = [pc.nome for pc in analise.palavras_chave.all() if pc.nome]
    palavras_str = "; ".join(palavras_list)

    desfecho = analise.desfecho or ""
    resultado_reclamante = analise.resultado_reclamante or ""

    texto_canonico = (
        f"classe: {classe_nome}\n"
        f"orgao_julgador: {orgao_julgador_nome}\n"
        f"assuntos: {assuntos_str}\n"
        f"resumo: {resumo}\n"
        f"decisao: {decisao}\n"
        f"palavras_chave: {palavras_str}\n"
        f"desfecho: {desfecho}\n"
        f"resultado_reclamante: {resultado_reclamante}"
    )
    return texto_canonico


def adicionar_analise_ao_processo(numero_processo: str, grau: str, analise_data: dict) -> Processo:
    graus = _normalize_grau_for_query(grau)
    processo = Processo.objects.filter(
        numero_processo=numero_processo,
    ).filter(
        Q(grau__in=graus)
    ).first()

    if processo is None:
        raise ProcessoNotFoundError("Processo nao encontrado para numero e grau informados.")

    palavras_chave = _sanitize_palavras_chave(analise_data.pop("palavras_chave", []))

    if processo.analise is None:
        processo.analise = Analise.objects.create(**analise_data)
    else:
        for attr, value in analise_data.items():
            setattr(processo.analise, attr, value)
        processo.analise.save()

    processo.analise.palavras_chave.clear()
    for palavra in palavras_chave:
        palavra_obj, _ = PalavraChave.objects.get_or_create(nome=palavra)
        processo.analise.palavras_chave.add(palavra_obj)

    processo.save(update_fields=["analise"])

    # Pipeline Síncrona de Geração de Embeddings
    try:
        from shared.embeddings import embed_text
        texto = montar_texto_indexacao(processo)
        if texto:
            logger.info(f"Gerando embedding síncrono para processo_id={processo.id}...")
            embedding = embed_text(texto)
            processo.analise.embedding = embedding
            processo.analise.save(update_fields=["embedding"])
            logger.info(f"Embedding síncrono salvo com sucesso para processo_id={processo.id}.")
    except Exception as exc:
        logger.exception(f"Erro ao gerar ou salvar embedding para o processo {processo.id}: {exc}")

    return processo


def obter_processo_por_numero_grau(numero_processo: str, grau: str) -> Processo | None:
    graus = _normalize_grau_for_query(grau)
    return (
        Processo.objects.select_related("classe", "orgao_julgador", "analise")
        .prefetch_related("assuntos", "analise__palavras_chave")
        .filter(numero_processo=numero_processo)
        .filter(Q(grau__in=graus))
        .first()
    )


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def buscar_processos_semanticos(consulta: str, top_k: int = 5, metrica: str = "cosseno") -> list[Processo]:
    """Realiza a busca vetorial por similaridade ou texto (Cosseno, Euclidiana, Manhattan, Jaccard, Levenshtein)."""
    from pgvector.django import CosineDistance, L1Distance, L2Distance
    from shared.embeddings import embed_text

    logger.info(f"Iniciando busca semântica para consulta: '{consulta}' | top_k={top_k} | metrica={metrica}")

    if metrica in ["cosseno", "euclidiana", "manhattan"]:
        query_embedding = embed_text(consulta)
        qs = Processo.objects.filter(analise__embedding__isnull=False) \
            .select_related("classe", "orgao_julgador", "analise") \
            .prefetch_related("assuntos", "analise__palavras_chave")

        if metrica == "cosseno":
            qs = qs.annotate(similaridade=1 - CosineDistance("analise__embedding", query_embedding)).order_by("-similaridade")
        elif metrica == "euclidiana":
            qs = qs.annotate(distancia=L2Distance("analise__embedding", query_embedding)) \
                   .annotate(similaridade=1.0 / (1.0 + L2Distance("analise__embedding", query_embedding))) \
                   .order_by("distancia")
        elif metrica == "manhattan":
            qs = qs.annotate(distancia=L1Distance("analise__embedding", query_embedding)) \
                   .annotate(similaridade=1.0 / (1.0 + L1Distance("analise__embedding", query_embedding))) \
                   .order_by("distancia")

        return list(qs[:top_k])

    elif metrica in ["jaccard", "levenshtein"]:
        qs = Processo.objects.filter(analise__isnull=False) \
            .select_related("classe", "orgao_julgador", "analise") \
            .prefetch_related("assuntos", "analise__palavras_chave")

        resultados = []
        for p in qs:
            texto_p = p.analise.resumo or ""
            if not texto_p:
                p.similaridade = 0.0
                resultados.append(p)
                continue

            if metrica == "jaccard":
                set1 = set(consulta.lower().split())
                set2 = set(texto_p.lower().split())
                if not set1 and not set2:
                    sim = 1.0
                else:
                    sim = len(set1.intersection(set2)) / len(set1.union(set2))
            else: # levenshtein
                dist = levenshtein_distance(consulta.lower(), texto_p.lower())
                max_len = max(len(consulta), len(texto_p))
                sim = 1.0 - (dist / max_len) if max_len > 0 else 1.0

            p.similaridade = sim
            resultados.append(p)

        resultados.sort(key=lambda x: getattr(x, 'similaridade', 0.0), reverse=True)
        return resultados[:top_k]

    return []


def reindexar_processos_sem_embedding() -> int:
    """Calcula e persiste o embedding para todos os processos que possuem análise mas não possuem embedding calculado."""
    # Filtra processos que possuem análise, mas cujo embedding na análise é nulo
    processos = Processo.objects.filter(
        analise__isnull=False,
        analise__embedding__isnull=True
    ).select_related("classe", "orgao_julgador", "analise").prefetch_related("assuntos")

    total = processos.count()
    if total == 0:
        logger.info("Nenhum processo pendente de indexação vetorial.")
        return 0

    logger.info(f"Encontrados {total} processos pendentes de indexação vetorial. Iniciando processamento...")

    from shared.embeddings import embed_text

    count = 0
    for processo in processos:
        try:
            texto = montar_texto_indexacao(processo)
            if texto:
                embedding = embed_text(texto)
                processo.analise.embedding = embedding
                processo.analise.save(update_fields=["embedding"])
                count += 1
                if count % 10 == 0 or count == total:
                    logger.info(f"Progresso: {count}/{total} processos indexados.")
        except Exception as exc:
            logger.exception(f"Falha ao gerar embedding para processo_id={processo.id}: {exc}")

    return count


def sincronizar_processos_minio(
    modo: str,
    dry_run: bool = False,
    no_trigger: bool = False,
    stdout_writer = None,
) -> dict:
    import re

    from dateutil.parser import parse as parse_date
    from shared.celery_client import app as celery_app
    from shared.constants import PDF_BUCKET, WORKER_LLM_TASK_NAME
    from shared.s3_client import get_s3_client

    from core.serializers.processo_serializer import ProcessoSerializer

    def log(msg, style=None):
        if stdout_writer:
            if style:
                stdout_writer(msg, style)
            else:
                stdout_writer(msg)
        else:
            if style == "error":
                logger.error(msg)
            elif style == "warning":
                logger.warning(msg)
            else:
                logger.info(msg)

    client = get_s3_client()

    log("Consultando objetos no bucket S3 'pje-documents'...")
    try:
        objects = client.list_objects(PDF_BUCKET, recursive=True)
    except Exception as exc:
        log(f"Falha ao listar objetos no S3: {exc}", "error")
        return {"sucesso": False, "erro": str(exc)}

    log(f"Encontrados {len(objects)} objetos no S3.")

    db_processos = Processo.objects.all().prefetch_related('analise')
    db_processos_map = {}
    for p in db_processos:
        db_processos_map[(p.numero_processo, _normalize_grau(p.grau))] = p

    log(f"Encontrados {len(db_processos_map)} processos no banco de dados.")

    matched_objects = []
    orphaned_objects = []

    pattern = re.compile(r"^(\d+)(?:_(\d+))?\.pdf$")

    for obj in objects:
        filename = obj.object_name
        match = pattern.match(filename)
        if not match:
            orphaned_objects.append((filename, None, None))
            continue

        numero_processo = match.group(1)
        grau_suff = match.group(2)

        grau_val = grau_suff if grau_suff else "1"
        grau_normalized = _normalize_grau(grau_val)

        key = (numero_processo, grau_normalized)
        if key in db_processos_map:
            matched_objects.append((filename, numero_processo, grau_normalized))
        else:
            orphaned_objects.append((filename, numero_processo, grau_normalized))

    log(f"  -> Objetos correspondidos no banco: {len(matched_objects)}")
    log(f"  -> Objetos órfãos (apenas no S3): {len(orphaned_objects)}")

    resultado = {
        "total_s3": len(objects),
        "total_db": len(db_processos_map),
        "matched": len(matched_objects),
        "orphaned": len(orphaned_objects),
    }

    if modo == "status":
        return resultado

    if modo == "import":
        importados = 0
        tasks_disparadas = 0

        orphaned_nums = list({item[1] for item in orphaned_objects if item[1]})
        log(f"Iniciando busca em lotes na API DataJud para {len(orphaned_nums)} processos órfãos...")

        datajud_metadata = {}
        batch_size = 100
        for i in range(0, len(orphaned_nums), batch_size):
            batch = orphaned_nums[i : i + batch_size]
            log(f"  -> Buscando lote {i // batch_size + 1} de {(len(orphaned_nums) - 1) // batch_size + 1} (Tamanho: {len(batch)})...")

            import requests
            api_url = 'https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search'
            public_key = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
            headers = {'Authorization': f'APIKey {public_key}', 'Content-Type': 'application/json'}
            query = {
                'size': len(batch) * 2,
                'query': {
                    'terms': {
                        'numeroProcesso.keyword': batch
                    }
                }
            }
            try:
                response = requests.post(api_url, headers=headers, json=query, timeout=20)
                if response.ok:
                    hits = response.json().get('hits', {}).get('hits', [])
                    for h in hits:
                        source = h.get('_source', {})
                        num = source.get('numeroProcesso')
                        if num:
                            datajud_metadata.setdefault(num, []).append(source)
            except Exception as e:
                log(f"Erro ao buscar lote no DataJud: {e}", "warning")

        log(f"Metadados recuperados do DataJud para {len(datajud_metadata)} processos.")
        log(f"Iniciando importação de processos órfãos (Total: {len(orphaned_objects)})...")

        for filename, num_processo, grau_norm in orphaned_objects:
            if not num_processo:
                continue

            grau_db = f"G{grau_norm}" if grau_norm in {"1", "2"} else "G1"

            matched_sources = datajud_metadata.get(num_processo, [])
            source_meta = None
            for s in matched_sources:
                if _normalize_grau(s.get("grau")) == grau_norm:
                    source_meta = s
                    break
            if not source_meta and matched_sources:
                source_meta = matched_sources[0]

            if source_meta:
                log(f"Importando processo rico {num_processo} grau {grau_db} (do arquivo {filename})...")
                classe_data = None
                if c_raw := source_meta.get("classe"):
                    classe_data = {"codigo": c_raw.get("codigo"), "nome": c_raw.get("nome")}

                orgao_data = None
                if o_raw := source_meta.get("orgaoJulgador"):
                    orgao_data = {
                        "codigo": o_raw.get("codigo"),
                        "nome": o_raw.get("nome"),
                        "codigo_municipio_ibge": o_raw.get("codigoMunicipioIBGE"),
                    }

                assuntos_data = []
                for a_raw in source_meta.get("assuntos", []):
                    if a_raw:
                        assuntos_data.append({"codigo": a_raw.get("codigo"), "nome": a_raw.get("nome")})

                data_ajuizamento = None
                if date_ajuiz_raw := source_meta.get("dataAjuizamento"):
                    try:
                        data_ajuizamento = parse_date(date_ajuiz_raw).date().isoformat()
                    except Exception:
                        pass

                data_att = None
                if date_att_raw := source_meta.get("dataHoraUltimaAtualizacao"):
                    try:
                        data_att = parse_date(date_att_raw).date().isoformat()
                    except Exception:
                        pass

                mapped_dict = {
                    "numero_processo": num_processo,
                    "grau": grau_db,
                    "tribunal": source_meta.get("tribunal", "TRT6"),
                    "data_ajuizamento": data_ajuizamento,
                    "data_hora_ultima_atualizacao": data_att,
                    "classe": classe_data,
                    "orgao_julgador": orgao_data,
                    "assuntos": assuntos_data,
                }
            else:
                log(f"Importando processo esqueleto {num_processo} grau {grau_db} (do arquivo {filename}) - Sem metadados no DataJud...")
                mapped_dict = {
                    "numero_processo": num_processo,
                    "grau": grau_db,
                    "tribunal": "TRT6",
                    "data_ajuizamento": None,
                    "data_hora_ultima_atualizacao": None,
                    "classe": None,
                    "orgao_julgador": None,
                    "assuntos": [],
                }

            if not dry_run:
                try:
                    Processo.objects.filter(numero_processo=num_processo, grau=grau_db).delete()

                    serializer = ProcessoSerializer()
                    processo = serializer.create(mapped_dict)
                    importados += 1
                except Exception as e:
                    log(f"Erro ao criar processo rico {num_processo} no banco: {e}", "error")
                    continue
            else:
                importados += 1

            if not no_trigger:
                log(f"  -> Disparando task worker-llm para {num_processo} grau {grau_db}...")
                if not dry_run:
                    try:
                        celery_app.send_task(
                            WORKER_LLM_TASK_NAME,
                            kwargs={
                                "numero_processo": num_processo,
                                "grau": grau_db,
                                "bucket_name": PDF_BUCKET,
                                "object_name": filename,
                            },
                        )
                        tasks_disparadas += 1
                    except Exception as e:
                        log(f"Erro ao disparar task para {num_processo}: {e}", "error")
                else:
                    tasks_disparadas += 1

        log(f"Sincronização concluída (import): {importados} processos criados, {tasks_disparadas} tasks de LLM disparadas.")
        resultado["importados"] = importados
        resultado["tasks_disparadas"] = tasks_disparadas

    elif modo == "trigger":
        tasks_disparadas = 0
        pendentes_analise = []
        for key, processo in db_processos_map.items():
            if processo.analise is None:
                num_processo, grau_norm = key
                object_name = _s3_object_key(num_processo, grau_norm)
                exists = any(obj.object_name == object_name for obj in objects)
                if exists:
                    pendentes_analise.append((processo, object_name))

        log(f"Encontrados {len(pendentes_analise)} processos no banco com PDF no S3 mas sem análise.")

        for processo, object_name in pendentes_analise:
            log(f"Disparando task worker-llm para {processo.numero_processo} grau {processo.grau}...")
            if not dry_run:
                try:
                    celery_app.send_task(
                        WORKER_LLM_TASK_NAME,
                        kwargs={
                            "numero_processo": processo.numero_processo,
                            "grau": processo.grau,
                            "bucket_name": PDF_BUCKET,
                            "object_name": object_name,
                        },
                    )
                    tasks_disparadas += 1
                except Exception as e:
                    log(f"Erro ao disparar task para {processo.numero_processo}: {e}", "error")
            else:
                tasks_disparadas += 1

        log(f"Sincronização concluída (trigger): {tasks_disparadas} tasks de LLM disparadas.")
        resultado["tasks_disparadas"] = tasks_disparadas

    elif modo == "cleanup":
        removidos = 0
        log(f"Iniciando remoção de {len(orphaned_objects)} objetos órfãos no S3...")
        for filename, _, _ in orphaned_objects:
            log(f"Removendo objeto {filename} do S3...")
            if not dry_run:
                try:
                    client.delete_object(PDF_BUCKET, filename)
                    removidos += 1
                except Exception as e:
                    log(f"Erro ao remover objeto {filename}: {e}", "error")
            else:
                removidos += 1

        log(f"Sincronização concluída (cleanup): {removidos} objetos removidos do S3.")
        resultado["removidos"] = removidos

    return resultado


def atualizar_movimentos_processos(stdout_writer=None) -> dict:
    """
    Queries all processes in the database, batches their process numbers,
    fetches their movements from the DataJud API (TRT6), normalizes the payload,
    and updates each process's movimientos field (which automatically compresses it using zlib).
    """
    def log(msg, style=None):
        if stdout_writer:
            stdout_writer(msg, style)
        else:
            if style == "error":
                logger.error(msg)
            elif style == "warning":
                logger.warning(msg)
            else:
                logger.info(msg)

    log("=== Iniciando atualização de movimentos dos processos ===")

    # 1. Obter todos os processos do banco de dados
    processos = Processo.objects.all()
    total_processos = processos.count()
    log(f"Encontrados {total_processos} processos no banco de dados.")

    if total_processos == 0:
        return {"total": 0, "atualizados": 0, "erros": 0}

    # Agrupa os processos por numero para buscar em lotes no DataJud
    processos_por_numero = {}
    for p in processos:
        processos_por_numero.setdefault(p.numero_processo, []).append(p)

    numeros_processos = list(processos_por_numero.keys())

    atualizados = 0
    erros = 0

    batch_size = 100
    for i in range(0, len(numeros_processos), batch_size):
        batch = numeros_processos[i : i + batch_size]
        log(f"Buscando movimentos para lote {i // batch_size + 1} de {(len(numeros_processos) - 1) // batch_size + 1} (tamanho do lote: {len(batch)})...")

        import requests
        api_url = 'https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search'
        public_key = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
        headers = {'Authorization': f'APIKey {public_key}', 'Content-Type': 'application/json'}
        query = {
            'size': len(batch) * 2,
            'query': {
                'terms': {
                    'numeroProcesso.keyword': batch
                }
            }
        }

        datajud_hits = []
        try:
            response = requests.post(api_url, headers=headers, json=query, timeout=20)
            if response.ok:
                datajud_hits = response.json().get('hits', {}).get('hits', [])
            else:
                log(f"Erro na resposta da API DataJud para o lote: status_code={response.status_code}, body={response.text}", "warning")
                erros += len(batch)
                continue
        except Exception as e:
            log(f"Erro ao consultar a API DataJud: {e}", "error")
            erros += len(batch)
            continue

        # Cria um mapeamento de (numeroProcesso, grau_norm) -> movimentos do DataJud
        movimentos_map = {}
        for h in datajud_hits:
            source = h.get('_source', {})
            num = source.get('numeroProcesso')
            grau_raw = source.get('grau')
            movs = source.get('movimentos', [])
            if num:
                grau_norm = _normalize_grau(grau_raw)
                movimentos_map[(num, grau_norm)] = movs

        # Atualiza os processos do lote no banco de dados
        for num_processo in batch:
            db_processos = processos_por_numero.get(num_processo, [])
            for p in db_processos:
                grau_norm = _normalize_grau(p.grau)

                # Procura os movimentos correspondentes ao numero e grau
                movs_datajud = movimentos_map.get((num_processo, grau_norm))

                # Se não achou com o grau exato, mas existe apenas uma entrada para o processo no DataJud, podemos tentar usar como fallback
                if movs_datajud is None:
                    fallback_movs = [movs for (num, gr), movs in movimentos_map.items() if num == num_processo]
                    if len(fallback_movs) == 1:
                        movs_datajud = fallback_movs[0]

                if movs_datajud is not None:
                    # Mapeia os movimentos para o formato esperado pelo front
                    mapped_movs = []
                    for m in movs_datajud:
                        orgao_raw = m.get("orgaoJulgador") or m.get("orgao_julgador")
                        orgao = None
                        if orgao_raw:
                            orgao = {
                                "codigo": orgao_raw.get("codigo"),
                                "nome": orgao_raw.get("nome"),
                            }
                        mapped_movs.append({
                            "codigo": m.get("codigo"),
                            "nome": m.get("nome"),
                            "data_hora": m.get("dataHora") or m.get("data_hora"),
                            "orgao_julgador": orgao,
                        })

                    p.movimentos = mapped_movs
                    p.save(update_fields=["movimentos"])
                    atualizados += 1
                else:
                    log(f"Movimentos não encontrados no DataJud para o processo {num_processo} grau {p.grau}", "warning")
                    erros += 1

    log(f"=== Sincronização concluída: {atualizados} processos atualizados, {erros} erros/não encontrados ===", "success")
    return {"total": total_processos, "atualizados": atualizados, "erros": erros}



