from fastapi import APIRouter
from pathlib import Path
from pydantic import BaseModel
from ..SHARED_PROCESS import SHARED_PROCESS
from schema import UserConfig
import uuid

router = APIRouter()

data_path = str(Path(".").resolve())


## STEP 1. CONFIG FIRST !!


@router.post("")
async def store_config(config: UserConfig):
    session_id = str(uuid.uuid4())
    if session_id not in SHARED_PROCESS.keys():
        SHARED_PROCESS[session_id] = {}
        SHARED_PROCESS[session_id]["config"] = {}
        SHARED_PROCESS[session_id]["config"]["user_id"] = config.user_id
        SHARED_PROCESS[session_id]["config"]["retrieval_metrics"] = config.retrieval_metrics
        SHARED_PROCESS[session_id]["config"]["generation_metrics"] = config.generation_metrics
        SHARED_PROCESS[session_id]["config"]["top_k"] = config.top_k
        SHARED_PROCESS[session_id]["config"]["model"] = config.model
        SHARED_PROCESS[session_id]["config"]["evaluation_mode"] = config.evaluation_mode    
    
    return {"session_id": session_id, "message": "Session Configuration set successfully."}




