import os
import sys
from dotenv import load_dotenv
from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model

logger = CustomLogger().get_logger(name=__name__)


# class ModelLoader:
#     """
#     A utility class to load embedding models and LLM models
#     """
#     def __init__(self):
#         load_dotenv()
#         self._validate_env()
#         self.config = load_config()
#         logger.info("Configuration loader successfully", config_keys=list(self.config.keys()))

#     def _validate_env(self):
#         """
#         validate necessary environment variables.
#         Ensure API keys
#         """
#         required_vars = ['OPENAI_API_KEY']
#         self.api_keys = {key: os.getenv(key) for key in required_vars}
#         missing = [k for k, v in self.api_keys.items() if not v]

#         if missing:
#             logger.error("Missing environment variables", missing_vars=missing)
#             raise DocumentPortalException("Missing environment variables", sys)
#         logger.info("Encironment variables validated", available_keys=[k for k in self.api_keys if self.api_keys[k]])

#     def load_embeddings(self):
#         """
#         Load and return the embedding model
#         """
#         try:
#             logger.info("Loading embedding model...")
#             model_name = self.config['embedding_model']['model_name']
#             return OpenAIEmbeddings(model=model_name)
#         except Exception as e:
#             logger.error("Error loading embedding model", error=str(e))
#             raise DocumentPortalException("Error loading embedding model", sys)

#     def load_llm(self):
#         """
#         Load and return the LLM model.
#         Load LLM dynamically based on provider in config.
#         """
#         llm_block = self.config['llm']

#         ## Get the provider key
#         provider_key = os.getenv('LLM_PROVIDER', 'openai')

#         if provider_key not in llm_block:
#             logger.error("LLM Provider not found in config", provider_key=provider_key)
#             raise ValueError(f"Provider '{provider_key}' not found in config")

#         llm_config = llm_block[provider_key]
#         provider = llm_config.get('provider')
#         model_name = llm_config.get('model_name')
#         temperature = llm_config.get('temperature', 0.2)
#         max_tokens = llm_config.get('max_output_tokens', 2048)

#         logger.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

#         llm = init_chat_model(model=model_name, model_provider=provider)

#         return llm


class ModelLoader:
    """
    A utility class to load embedding models and LLM models
    """

    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        logger.info(
            f"Configuration loader successfully. Keys: {list(self.config.keys())}"
        )

    def _validate_env(self):
        """
        Validate necessary environment variables.
        Ensure API keys are present.
        """
        required_vars = ["OPENAI_API_KEY"]
        self.api_keys = {key: os.getenv(key) for key in required_vars}
        missing = [k for k, v in self.api_keys.items() if not v]

        if missing:
            logger.error(f"Missing environment variables: {missing}")
            raise DocumentPortalException("Missing environment variables", sys)

        available_keys = [k for k in self.api_keys if self.api_keys[k]]
        logger.info(
            f"Environment variables validated. Available keys: {available_keys}"
        )

    def load_embeddings(self):
        """
        Load and return the embedding model
        """
        try:
            logger.info("Loading embedding model...")
            model_name = self.config["embedding_model"]["model_name"]
            return OpenAIEmbeddings(model=model_name)
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise DocumentPortalException("Error loading embedding model", sys)

    def load_llm(self):
        """
        Load and return the LLM model.
        Load LLM dynamically based on provider in config.
        """
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER", "openai")

        if provider_key not in llm_block:
            logger.error(f"LLM Provider '{provider_key}' not found in config.")
            raise ValueError(f"Provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        logger.info(
            f"Loading LLM - Provider: {provider}, Model: {model_name}, "
            f"Temperature: {temperature}, Max Tokens: {max_tokens}"
        )

        llm = init_chat_model(
            model_name,
            model_provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return llm


if __name__ == "__main__":
    loader = ModelLoader()

    # Test the loading of embedding model
    embeddings = loader.load_embeddings()
    print(f"Embedding model loaded: {embeddings}")
    print("**************" * 4)

    vectors = embeddings.embed_query("Do you know about IPL?")
    print(f"Vectors: {vectors}")
    print("**************" * 4)

    # Test the loading of LLM model
    llm = loader.load_llm()
    print(f"LLM loaded: {llm}")
    print("**************" * 4)

    # Test the ModelLoader
    result = llm.invoke("Do you know about IPL?")
    print(f"LLM result: {result}")
    print("**************" * 4)
