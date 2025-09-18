import redis
import json
import asyncio
import os
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Dict, Optional
from tqdm import tqdm

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv

from parasite_library.DataProcessor.RecieveData import DataReceiver

load_dotenv()
api_key = os.getenv("API_KEY")
REDIS_PORT = os.getenv("REDIS_PORT")

class GenerateReport:
    def __init__(self, embedding_model: Optional[Any | None], llm_model: Any, session_id:str, **kwargs):

        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.session_id = session_id
        self.kwargs = kwargs

    def load_eval_result(self):
        
        self.session_id
        r = redis.Redis(
                host='localhost',
                port=int(REDIS_PORT),
                decode_responses=True
                )
        try:
            r.ping()
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")

        stored_session_json = r.get(self.session_id)
        session_data = json.loads(stored_session_json)
        eval_result = session_data["eval_result"]
        false_value = session_data["false_value"] # {"mrr": [{"query","ground_truth_documents", "predicted_documents"}, {"query","ground_truth_documents", "predicted_documents"}]}
        return eval_result, false_value

    async def create_report(self, eval_result: str, false_value: dict):
        script_dir = Path(__file__).parent.parent.resolve()
        prompt_path = script_dir / "Prompts" / "REPORT_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")

        formatted_prompt = template_string.format(retrieval_final_scores=eval_result["retrieval_final_scores"], 
                                                  generator_final_scores = eval_result["generator_final_scores"], 
                                                  false_value=false_value)

        eval_report = await self.llm_model.ainvoke(
            [
                SystemMessage(content=formatted_prompt),
            ]
        )
        eval_report = eval_report.content

        return eval_report


## main
async def main(data):
    session_id = "abc"
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key)
    embeddings = None
    llm = ChatOpenAI(
        model="gemma-3-4b-it",
        api_key='token-123',
        base_url="http://localhost:8000/v1",
    )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

    solver = GenerateReport(llm_model=llm, embedding_model=embeddings, session_id=session_id)
    ## for test

    eval_report = await solver.load_eval_result()
    return {"eval_repot": eval_report}


if __name__ == "__main__":

    asyncio.run(main())
