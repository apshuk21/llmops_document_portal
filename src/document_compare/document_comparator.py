import sys
import pandas as pd
from dotenv import load_dotenv
from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from model.models import SummaryResponse
from prompt.prompt_library import PROMPT_REGISTRY
from exception.custom_exception import DocumentPortalException


class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        self.logger = CustomLogger().get_logger(name=__name__)
        self.llm = ModelLoader().load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(
            parser=self.parser, llm=self.llm
        )
        self.prompt = PROMPT_REGISTRY.get("document_comparison", "")

        self.chain = self.prompt | self.llm | self.parser

    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        """
        Compares two documents and returns a structured response
        """
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions(),
            }

            self.logger.info("Invoking document comparison LLM chain")
            response = self.chain.invoke(inputs)
            self.logger.info(
                "Chain invoked successfully", response_preview=str(response)[:200]
            )
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"Error in compare documents: {e}")
            raise DocumentPortalException(
                "An error occured while comparing documents.", sys
            )

    def _format_response(self, response_parsed: list[dict]) -> pd.DataFrame:
        """
        Formats the response from the LLM into a structured format
        """
        try:
            df = pd.DataFrame(response_parsed)
            return df
        except Exception as e:
            self.logger.error(f"Error formatting response into DataFrame: {e}")
            raise DocumentPortalException("Error formatting response.", sys)
