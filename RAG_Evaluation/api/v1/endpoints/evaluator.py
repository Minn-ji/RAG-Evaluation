from typing import List
from schema import EvaluationRequest, GraphSchema, RetrievalModel, GenerationModel, UserConfig
from langchain_core.documents import Document
from ..SHARED_PROCESS import SHARED_PROCESS
from graphs import create_main_graph
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
# import asyncio

## STEP 3. EVALUATE !!


router = APIRouter()

def to_document(chunks: RetrievalModel | GenerationModel) -> List[Document]:
    return [
        Document(
            page_content = chunk.get("text",""),
            file_name = chunk.get("file_name", ""),
            metadata={k: v for k, v in chunk.items() if k != "text"},
        )
        for chunk in chunks
    ]
    
    
def create_input_payload(session_id):
    config = SHARED_PROCESS[session_id]["config"]
    benchmark_dataset = SHARED_PROCESS[session_id]["benchmark_dataset"]
    if not config or not benchmark_dataset:
        raise ValueError("Configuration or benchmark_dataset is missing.")
    config = UserConfig(**config)
    retrieval_dataset = None 
    generation_dataset = None

    if config.evaluation_mode == 'full':
    # if isinstance(RetrievalModel(**benchmark_dataset), RetrievalModel):
        print("Dataset type is 'RetrievalModel'. Populating retrieval payload.")
        retrieval_dataset = {
            "query": benchmark_dataset['query'],
            "predicted_documents": [to_document(doc) for doc in benchmark_dataset['predicted_documents']],
            "ground_truth_documents": [to_document(doc) for doc in benchmark_dataset['ground_truth_documents']],# List[List of text]
            "model": config.model,
            "k": config.top_k,
        }
     
    # if isinstance(GenerationModel(**benchmark_dataset), GenerationModel):
        print("Dataset type is 'GenerationModel'. Populating generation payload.")
        generation_dataset = {
            "query": benchmark_dataset['query'],
            "ground_truth_answer": [to_document(ans) for ans in benchmark_dataset['ground_truth_answer']],
            "retrieved_contexts": [to_document(con) for con in benchmark_dataset['retrieved_contexts']],
            "generated_answer": benchmark_dataset['generated_answer'],
            "model": config.model
        }
    elif config.evaluation_mode == 'generation_only':
        generation_dataset = {
            "query": benchmark_dataset['query'],
            "ground_truth_answer": [to_document(ans) for ans in benchmark_dataset['ground_truth_answer']],
            "retrieved_contexts": [to_document(con) for con in benchmark_dataset['retrieved_contexts']],
            "generated_answer": benchmark_dataset['generated_answer'],
            "model": config.model
        }
        retrieval_dataset = None

    elif config.evaluation_mode == 'retrieval_only':
        retrieval_dataset = {
            "query": benchmark_dataset['query'],
            "predicted_documents": [to_document(doc) for doc in benchmark_dataset['predicted_documents']],
            "ground_truth_documents": [to_document(doc) for doc in benchmark_dataset['ground_truth_documents']],# List[List of text]
            "model": config.model,
            "k": config.top_k,
        }

        generation_dataset = None
    else:
        raise TypeError(f"Unsupported dataset type: {type(benchmark_dataset)}")

    final_payload = {
        "retrieve_metrics": config.retrieval_metrics.retrieval_metrics,
        "generate_metrics": config.generation_metrics.generation_metrics,
        "dataset": {
            "Retrieval": retrieval_dataset,
            "Generation": generation_dataset,
        },
        "evaluation_mode": config.evaluation_mode,
    }

    return final_payload


@router.post("/", status_code=202)
async def evaluator(evaluation_request: EvaluationRequest):

    if not (evaluation_request.session_id or evaluation_request.user_id):
        raise HTTPException(status_code=404, detail="Evaluation request Invalid!")

    graph_input = create_input_payload(evaluation_request.session_id)

    main_graph = create_main_graph()
    response = await main_graph.ainvoke(input=graph_input)
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")

    # set result to redis
    key = evaluation_request.session_id
    value = {"retrieval_evaluation_result": retrieval_evaluation_result, "generator_evaluation_result": generator_evaluation_result}
    redis_set_url = f"http://localhost:8001/set/{key}/{value}"
    requests.post(redis_set_url)

    # get value
    redis_get_url = f"http://localhost:8001/get/{key}"
    response = requests.get(redis_get_url)
    return JSONResponse(
        status_code=200,
        content={
            "status": "OK",
            "evaluate_result": response.json()
        }
    )