#### 1. CONFIG
curl -X POST http://localhost:8000/v1/config \
-H "Content-Type: application/json" \
-d '{
    "user_id": "jjy714",
    "retrieve_metrics": ["precision", "map", "ndcg"],
    "generate_metrics": ["bleu"],
    "top_k": 10,
    "model": "None",
    "evaluation_mode": "full"
}'

#### 2. DATASET

curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d '{
    "session_id":"bf6a7de5-4007-49db-9d02-24e544896f8f",
    "user_id" : "jjy714",
    "dataset_name": "response_merged_output.csv"
}'

#### 3. EVALUATE

curl -X POST http://localhost:8000/v1/evaluate/ \
-H "Content-Type: application/json" \
-d '{
    "session_id": "70194e51-4166-43e3-ab22-af10faf9163b",
    "user_id": "jjy714"
}'



### 0. Insert Data

curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/response_merged_output.csv" \
    "http://localhost:8001/v1/insert?user_id=jjy714"