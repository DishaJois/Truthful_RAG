# TruthfulRAG: Drug-Interaction Question Answering System

TruthfulRAG is an academic prototype implementing robust retrieval-augmented generation (RAG), knowledge graph integration, claim verification, and nine-state adjudication for biomedical drug-interaction queries.

## Setup Instructions
1. Clone the repository and navigate to the root directory.
2. Create and activate a Python virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place processed data files (`faiss.index`, `chunk_ids.json`, `chunks.jsonl`, `drugs_of.json`) in `data/processed/`.
5. Ensure `data/kg/triples.csv` is present.

## Running the Streamlit App
```bash
streamlit run app/streamlit_app.py
```

## Running Evaluation and Tests
```bash
pytest -q
python -m src.pipeline.smoke_text
python -m src.evaluation.run_eval A
```
