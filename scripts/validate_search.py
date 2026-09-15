import os
# Configura o cache antes de qualquer outro import
os.makedirs(".cache/huggingface", exist_ok=True)
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".cache/huggingface")
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(os.getcwd(), ".cache/huggingface")

import time
import mlflow
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

# Configurações do Banco
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "database": os.getenv("POSTGRES_DB", "trt6"),
    "user": os.getenv("POSTGRES_USER", "trt6"),
    "password": os.getenv("POSTGRES_PASSWORD", "trt6"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

# Modelo de Embedding (mesmo usado no projeto)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Golden Set: Queries e Processo ID esperado no Top 3
GOLDEN_SET = [
    {"query": "diferenças salariais e previdência complementar CHESF", "expected_id_hint": "Albertino Laureano"},
    {"query": "acordo homologado quitação integral contrato trabalho", "expected_id_hint": "William Styvenny"},
    {"query": "manutenção plano de saúde auxílio-doença danos morais", "expected_id_hint": "HAPVIDA"},
    {"query": "responsabilidade solidária subsidiária prescrição intercorrente", "expected_id_hint": "solidária"},
    {"query": "empregada doméstica anotação CTPS rescisão acordo", "expected_id_hint": "doméstica"}
]

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_benchmark():
    print(f"--- Iniciando Benchmark JusTRT6 Search ---")
    # Tenta carregar o modelo localmente (CPU)
    model = SentenceTransformer(MODEL_NAME)
    
    mlflow.set_experiment("JusTRT6-Semantic-Search")
    
    with mlflow.start_run(run_name=f"Search Evaluation {time.strftime('%Y-%m-%d %H:%M')}"):
        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("embedding_dimension", 384)
        mlflow.log_param("vector_db", "pgvector")

        latencies = []
        hits = 0
        
        try:
            conn = get_connection()
            cur = conn.cursor()

            for test_case in GOLDEN_SET:
                query_text = test_case["query"]
                print(f"Testando query: {query_text}")
                
                # 1. Gerar Embedding
                start_embed = time.time()
                query_embedding = model.encode(query_text).tolist()
                
                # 2. Buscar no pgvector
                start_search = time.time()
                # Convertendo lista para formato pgvector string
                embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
                
                sql = """
                    SELECT a.id, a.resumo, (1 - (a.embedding <=> %s::vector)) as similarity
                    FROM core_analise a
                    WHERE a.embedding IS NOT NULL
                    ORDER BY a.embedding <=> %s::vector
                    LIMIT 3
                """
                cur.execute(sql, (embedding_str, embedding_str))
                
                results = cur.fetchall()
                latency = (time.time() - start_search) * 1000
                latencies.append(latency)
                
                if results:
                    # Validação qualitativa simples (se o resumo contém o hint esperado)
                    found_hit = any(test_case["expected_id_hint"].lower() in r[1].lower() for r in results)
                    if found_hit:
                        hits += 1
                    print(f"  -> Latência: {latency:.2f}ms | Top 1 Similarity: {results[0][2]:.4f} | Hit: {found_hit}")
                else:
                    print(f"  -> Nenhum resultado retornado.")

            avg_latency = np.mean(latencies)
            precision_at_3 = hits / len(GOLDEN_SET)
            
            mlflow.log_metric("avg_latency_ms", avg_latency)
            mlflow.log_metric("precision_at_3", precision_at_3)
            
            print(f"\nResultados Finais:")
            print(f"  Latência Média: {avg_latency:.2f}ms")
            print(f"  Precision@3: {precision_at_3 * 100:.1f}%")
            print(f"Run registrada com sucesso no MLflow.")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Erro durante benchmark: {e}")

if __name__ == "__main__":
    run_benchmark()
