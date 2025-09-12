from ragas.metrics import BleuScore
from ragas import SingleTurnSample
import numpy as np
from typing import List
from tqdm.asyncio import tqdm
from ragas.dataset_schema import SingleTurnSample 
from typing import List, Dict
import numpy as np


async def bleu(response: List, reference:List) -> Dict[str, float]:
    """
    DOCUMENTATION

    BLEU score ranges from 0 to 1, 
    where 1 indicates a perfect match between the response and the reference. 
    This is a non LLM based metric.
    """
    scorer = BleuScore()
    results = []

    # Document → string 
    def normalize_text(item):
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            return item.get("text") or item.get("page_content", "")
        elif hasattr(item, "page_content"):
            return item.page_content
        elif isinstance(item, list):
            return " ".join([normalize_text(sub) for sub in item])
        else:
            return str(item)

    data_list = [
        SingleTurnSample(
            response=normalize_text(res),
            reference=normalize_text(ref)
        )
        for res, ref in zip(response, reference)
    ]

    for sample in tqdm(data_list):
        temp = await scorer.single_turn_ascore(sample)
        results.append(temp)

    if not results:
        result = 0.0
    else:
        result = float(np.mean(results))

    return result
