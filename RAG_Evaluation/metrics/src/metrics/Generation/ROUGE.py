from ragas.metrics import RougeScore
from ragas import SingleTurnSample
from typing import List, Dict
from tqdm.asyncio import tqdm

import numpy as np


async def rouge(
        response: List,
        reference: List,
        rouge_type: str | None = "rouge1", 
        mode: str | None = "recall",
        )-> Dict[str, float]:
    """
    DOCUMENTATION
    
    You can change the rouge_type to rouge1 or rougeL 
    to calculate the ROUGE score based on unigrams or longest common subsequence respectively.
    
    You can change the mode to precision, recall, or fmeasure 
    to calculate the ROUGE score based on precision, recall, or F1 score respectively.
    
    """
    scorer = RougeScore(rouge_type=rouge_type)
    results = []

    def normalize_text(item):
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            return item.get("text") or item.get("page_content", "")
        elif hasattr(item, "page_content"): 
            return item.page_content
        elif isinstance(item, list):
            return " ".join([normalize_text(sub) for sub in item])