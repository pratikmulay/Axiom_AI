# NLP/Text Agent — Microservice 06

Production-ready FastAPI microservice for unstructured text analysis.
Part of the **GEMRSLIZE** multi-agent data analysis platform.

## Quick Start

```bash
# Local development
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8005

# Docker
docker-compose up --build
```

## API Endpoints

| Method | Path         | Description                          |
|--------|--------------|--------------------------------------|
| POST   | `/sentiment` | Batch sentiment analysis             |
| POST   | `/entities`  | Named entity recognition (spaCy)     |
| POST   | `/topics`    | Topic modeling (BERTopic)            |
| POST   | `/classify`  | Zero-shot text classification        |
| POST   | `/embed`     | Generate embeddings                  |
| POST   | `/summarize` | Summarize document or text column    |
| GET    | `/health`    | Service health check                 |

## Configuration

- **Free mode**: Copy `.env.free` → `.env` (uses Ollama + small models)
- **Paid mode**: Copy `.env.paid` → `.env` (uses Groq + large models + pgvector)

## Testing

```bash
python -m pytest tests/ -v
```

## Architecture

```
app/
├── main.py              # FastAPI app + startup model loading
├── config.py            # pydantic-settings configuration
├── llm/
│   └── provider.py      # LLM abstraction (Ollama/Groq/OpenAI)
├── pipelines/
│   ├── sentiment.py     # HuggingFace sentiment (cardiffnlp)
│   ├── ner.py           # spaCy NER
│   ├── topics.py        # BERTopic
│   ├── classifier.py    # Zero-shot via LLM
│   ├── embeddings.py    # SentenceTransformers
│   └── summarizer.py    # Map-reduce summarization
├── routes/              # API endpoint handlers
├── schemas/             # Pydantic request/response models
└── utils/
    ├── text_cleaner.py  # HTML strip, normalize, truncate
    └── batch_processor.py # Async batched processing
```
