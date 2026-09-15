from abc import ABC, abstractmethod

from shared.logger import get_logger
from shared.schemas.data_jud import SearchResponse

from ingestion.utils import DATA_FOLDER, normalize_topic

logger = get_logger("providers")


class DataProvider(ABC):
    @abstractmethod
    def get_data(self, topic: str) -> SearchResponse | None:
        """Retrieve SearchResponse for a given topic from the source (file, API, etc)."""
        pass

    def get_data_and_persist(self, topic: str) -> SearchResponse | None:
        import os
        data = self.get_data(topic)
        if data:
            os.makedirs(DATA_FOLDER, exist_ok=True)
            with open(DATA_FOLDER / f"processos_{normalize_topic(topic)}.json", "w", encoding="utf-8") as f:
                f.write(data.model_dump_json(ensure_ascii=False, indent=2))

                logger.info(f"Resposta para '{topic}' salva em 'processos_{normalize_topic(topic)}.json'")

        return data

    def __init__(self, file_path: str):
        self.file_path = file_path

class FileDataProvider(DataProvider):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self, topic: str) -> SearchResponse | None:
        import json
        import os
        path = self.file_path

        if not os.path.exists(path):
            return None

        if os.path.isdir(path):
            path = os.path.join(path, f"processos_{normalize_topic(topic)}.json")

        if not os.path.exists(path):
            logger.warning(f"File not found for topic '{topic}': {path}")
            return None

        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            try:
                return SearchResponse.model_validate(data)
            except Exception as e:
                logger.error(f"Failed to parse file as SearchResponse: {e}")
                return None


class APIDataProvider(DataProvider):
    def __init__(self, api_url: str, public_key: str = None):
        self.api_url = api_url
        self.public_key = public_key or "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

    def get_data(self, topic: str) -> SearchResponse | None:
        import requests

        headers = {"Authorization": f"APIKey {self.public_key}"}
        query = {
            "size": 10,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"assuntos.nome": topic}}
                    ]
                }
            }
        }
        try:
            response = requests.get(
                url=self.api_url,
                headers=headers,
                json=query,
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch topic '{topic}' from DataJud API: {exc}")
            return None

        logger.error(f"API response: {response.content} - {response.text}")
        if not response.ok:
            return None

        try:
            data = response.json()
            return SearchResponse.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse API response as SearchResponse: {e}")
            return None
