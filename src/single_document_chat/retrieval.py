import sys
from pathlib import Path
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
from utils.model_loader import ModelLoader


class ConversationalRAG:

    def __init__(self, session_id: str, retriever):
        self.logger = CustomLogger().get_logger(__name__)
        self.session_id = session_id
        self.retriever = retriever

        try:
            self.llm = self._load__llm()
            self.contextualize_prompt = PROMPT_REGISTRY[
                PromptType.CONTEXTUALIZE_QUESTION.value
            ]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.logger.info("Created history-aware retriever", session_id=session_id)

            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(
                self.history_aware_retriever, self.qa_chain
            )
            self.logger.info("Created RAG chain", session_id=session_id)

            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
            self.logger.info(
                "Wrapped chain with message history", session_id=session_id
            )

        except Exception as e:
            self.logger.error(f"Error initializing ConversationalRAG: {e}")
            raise DocumentPortalException("Error initializing ConversationalRAG", sys)

    def _load__llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.logger.info(
                "LLM loaded successfully", class_name=llm.__class__.__name__
            )
            return llm
        except Exception as e:
            self.logger.error(f"Error loading LLM in ConversationalRAG: {e}")
            raise DocumentPortalException("Error loading LLM in ConversationalRAG", sys)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        try:
            return InMemoryChatMessageHistory()
        except Exception as e:
            self.logger.error(
                "Failed to access session history in ConversationalRAG.",
                session_id=session_id,
                error=str(e),
            )
            raise DocumentPortalException(
                "Failed to access session history in ConversationalRAG", sys
            )

    def load_retriever_from_faiss(self, index_path: str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not Path(index_path).is_dir():
                raise FileNotFoundError(
                    f"FAISS index directory not found: {index_path}"
                )
            vectorstore = FAISS.load_local(index_path, embeddings=embeddings)
            self.logger.info("Loaded retriever from FAISS index", index_path=index_path)
            return vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
        except Exception as e:
            self.logger.error(
                "Error loading faiss retriever in ConversationalRAG:", error=str(e)
            )
            raise DocumentPortalException(
                "Error loading faiss retriever in ConversationalRAG", sys
            )

    def invoke(self, user_input: str):
        try:
            response = self.chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}},
            )
            answer = response.get("answer", "No answer.")

            if not answer:
                self.logger.warning("Empty answer received", session_id=self.session_id)

            self.logger.info(
                "Chain invoked successfully",
                session_id=self.session_id,
                user_input=user_input,
                answer_preview=answer[:150],
            )
            return answer

        except Exception as e:
            self.logger.error("Failed to invoke ConversationalRAG:", error=str(e))
            raise DocumentPortalException("Failed to invoke ConversationalRAG", sys)
