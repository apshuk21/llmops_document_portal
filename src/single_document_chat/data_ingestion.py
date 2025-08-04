import sys
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class SingleDocIngester:
    def __init__(self):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            pass
        except Exception as e:
            self.logger.error(f"Error initializing SingleDocIngestor: {e}")
            raise DocumentPortalException("Error initializing SingleDocIngestor", sys)

    def ingest_files(self):
        try:
            pass
        except Exception as e:
            self.logger.error(f"Document ingestion failed in SingleDocIngestor: {e}")
            raise DocumentPortalException(
                "Document ingestion failed in SingleDocIngestor", sys
            )

    def _create_retriever(self):
        try:
            pass
        except Exception as e:
            self.logger.error(f"Retriever creation failed in SingleDocIngestor: {e}")
            raise DocumentPortalException(
                "Retriever creation failed in SingleDocIngestor", sys
            )
