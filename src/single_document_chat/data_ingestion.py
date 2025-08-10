import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class SingleDocIngester:

    def __init__(
        self,
        data_dir: str = "data/single_document_chat",
        faiss_dir: str = "faiss_index",
    ):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.logger.info(
                "SingleDocIngestor initialized",
                temp_path=str(self.data_dir),
                faiss_path=str(self.faiss_dir),
            )
        except Exception as e:
            self.logger.error(f"Error initializing SingleDocIngestor: {e}")
            raise DocumentPortalException("Error initializing SingleDocIngestor", sys)

    def ingest_files(self, uploaded_files):
        try:
            documents = []

            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f_out:
                    f_out.write(uploaded_file.read())
                self.logger.info("PDF saved for ingestion", filename=uploaded_file.name)

                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)

            self.logger.info("PDF files loaded", count=len(documents))
            return self._create_retriever(documents)
        except Exception as e:
            self.logger.error(f"Document ingestion failed in SingleDocIngestor: {e}")
            raise DocumentPortalException(
                "Document ingestion failed in SingleDocIngestor", sys
            )

    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=300
            )
            chunks = splitter.split_documents(documents)
            self.logger.info("Documents split into chunks", count=len(chunks))

            embeddings = self.model_loader.load_embeddings()

            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)

            # save FAISS index
            vectorstore.save_local(str(self.faiss_dir))
            self.logger.info(
                "FAISS index created and saved", faiss_path=str(self.faiss_dir)
            )

            retriever = vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
            self.logger.info(
                "Retriever created successfully", retriever_type=str(type(retriever))
            )
            return retriever
        except Exception as e:
            self.logger.error(f"Retriever creation failed in SingleDocIngestor: {e}")
            raise DocumentPortalException(
                "Retriever creation failed in SingleDocIngestor", sys
            )
