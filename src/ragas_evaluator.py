"""
RAGAS evaluation module for calculating RAG quality metrics.
"""
import time
from typing import Any

from langchain.callbacks.manager import CallbackManager
from ragas import evaluate
from ragas.evaluation import RunConfig
from ragas.metrics import answer_relevancy, context_precision, faithfulness

from src import config


class RAGASEvaluator:
    """Class for evaluating RAG pipeline using RAGAS metrics."""

    def __init__(
        self, 
        enable_evaluation: bool | None = None,
        callback_manager: CallbackManager | None = None,
    ):
        """
        Initialize the RAGAS evaluator.

        Args:
            enable_evaluation: Whether to enable evaluation. Defaults to config.ENABLE_RAGAS_EVAL.
            callback_manager: Callback manager for LangSmith tracing.
        """
        self.enable_evaluation = (
            enable_evaluation if enable_evaluation is not None else config.ENABLE_RAGAS_EVAL
        )
        self.callback_manager = callback_manager
        
        # Define metrics to evaluate
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
        ]

    def prepare_dataset(
        self, query: str, answer: str, contexts: list[str]
    ) -> dict[str, Any]:
        """
        Prepare the dataset in the format expected by RAGAS.

        Args:
            query: The user query.
            answer: The generated answer.
            contexts: List of retrieved context strings.

        Returns:
            Dictionary with format required by RAGAS evaluation.
        """
        return {
            "questions": [query],
            "answers": [answer],
            "contexts": [contexts],
        }

    def evaluate(
        self, query: str, answer: str, contexts: list[str]
    ) -> dict[str, float] | None:
        """
        Evaluate the RAG response using RAGAS metrics.

        Args:
            query: The user query.
            answer: The generated answer.
            contexts: List of retrieved context strings.

        Returns:
            Dictionary of metric scores or None if evaluation is disabled.
        """
        if not self.enable_evaluation:
            return None

        try:
            start_time = time.time()
            
            # Prepare the dataset
            dataset = self.prepare_dataset(query, answer, contexts)
            
            # Configure the evaluation run
            # Note: RunConfig may not accept 'callbacks' directly
            # Use it without callbacks or check RAGAS documentation for proper usage
            run_config = None
            if self.callback_manager:
                try:
                    # Try to use RunConfig with the callback manager
                    # This may need adjustment based on RAGAS version
                    run_config = RunConfig()
                    # Some versions might use different parameter names
                except Exception:
                    # If RunConfig doesn't support callbacks, proceed without
                    run_config = None
            
            # Run evaluation
            result = evaluate(
                dataset=dataset,
                metrics=self.metrics,
                run_config=run_config,
            )
            
            # Extract metric scores
            scores = {}
            for metric in self.metrics:
                metric_name = metric.name
                scores[metric_name] = float(result.scores[metric_name])
            
            elapsed_time = time.time() - start_time
            scores["evaluation_time"] = elapsed_time
            
            return scores
            
        except Exception as e:
            print(f"Warning: RAGAS evaluation failed: {e}")
            return None

    def format_scores(self, scores: dict[str, float] | None) -> str:
        """
        Format metric scores for display.

        Args:
            scores: Dictionary of metric scores.

        Returns:
            Formatted string for display.
        """
        # Handle None case
        if scores is None:
            return "No evaluation metrics available."
        
        # Handle empty dictionary case
        if not scores:
            return ""
        
        output = []
        for metric_name, score in scores.items():
            if metric_name == "evaluation_time":
                output.append(f"  Evaluation Time: {score:.2f}s")
            else:
                output.append(f"  {metric_name}: {score:.4f}")
        
        return "\n".join(output)
