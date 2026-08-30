import abc

class BaseRetriever(abc.ABC):
    """
    Interface for context retrieval systems (e.g., Wikipedia Search, 
    Vector Database Retrieval) to be integrated in Phase 3.
    """
    
    @abc.abstractmethod
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves relevant reference passages for a given query.
        
        Args:
            query (str): The search query or question.
            top_k (int): Number of passages to retrieve.
            
        Returns:
            str: Concatenated reference context text.
        """
        pass


class BaseNLIVerifier(abc.ABC):
    """
    Interface for Natural Language Inference (NLI) systems to perform 
    sentence-level entailment checking to be integrated in Phase 3.
    """
    
    @abc.abstractmethod
    def verify_fact(self, premise: str, hypothesis: str) -> str:
        """
        Verifies if a premise (source context) entails a hypothesis (atomic fact).
        
        Args:
            premise (str): The reference source context.
            hypothesis (str): The atomic fact statement to verify.
            
        Returns:
            str: Verification label, typically one of: "entailment", "contradiction", or "neutral".
        """
        pass
