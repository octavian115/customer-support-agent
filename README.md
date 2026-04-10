# TaskFlow Support Agent

An AI-powered customer support agent for **TaskFlow**, a mock SaaS project management platform.

Built with **LangGraph** for agent orchestration, featuring intent classification, conditional routing, RAG-grounded responses, human-in-the-loop approval for billing actions, and automatic escalation for complex issues.

## Architecture

```mermaid
flowchart TD
    A[Customer Message] --> B[Classifier]
    B -->|faq / technical| C[RAG Node]
    B -->|billing| D[RAG Node]
    B -->|escalation| E[Escalation Node]

    C -->|confidence ≥ 0.65| F[Response Node]
    C -->|confidence < 0.65| E

    D --> G[Billing Node\nHITL: interrupt]

    F --> H[END]
    G --> H
    E --> H
```

## Key Features

- **Intent Classification**: LLM-based routing into faq, technical, billing, or escalation paths
- **RAG-Grounded Responses**: Answers grounded in TaskFlow's knowledge base (13 product docs)
- **Human-in-the-Loop**: Billing actions (refunds, plan changes) require human approval via `interrupt()`
- **Confidence-Based Escalation**: Low retrieval confidence automatically routes to human agent
- **Dual Interface**: Customer chat panel + human reviewer dashboard

## Tech Stack

- **Agent Framework**: LangGraph
- **LLM**: GPT-4o (via LangChain)
- **API Layer**: FastAPI
- **Frontend**: Streamlit (multi-page)
- **Vector Store**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Database**: PostgreSQL (LangGraph checkpointing)
- **Observability**: LangSmith

## Project Structure

```
taskflow-support-agent/
├── backend/
│   ├── nodes/
│   │   ├── classifier.py    # Intent classification
│   │   ├── rag.py           # Knowledge base retrieval
│   │   ├── response.py      # Response generation
│   │   ├── billing.py       # Billing actions + HITL
│   │   └── escalation.py    # Escalation + summary
│   ├── tools/
│   ├── app.py               # FastAPI endpoints
│   ├── graph.py             # LangGraph graph definition
│   ├── state.py             # State schema
│   ├── config.py            # LLM, Pinecone, settings
│   └── prompts.py           # All system prompts
├── frontend/
│   ├── customer_chat.py     # Customer-facing chat UI
│   └── agent_dashboard.py   # Human reviewer dashboard
├── knowledge_base/
│   └── docs/                # 13 TaskFlow product docs
├── scripts/
│   └── ingest.py            # Embed & upload docs to Pinecone
├── .env.example
└── README.md
```

## Setup

1. Clone the repo
2. Create `.env` from `.env.example` and add your API keys
3. Create a Pinecone index: name=`taskflow-support`, dimension=`1536`, metric=`cosine`
4. Ingest the knowledge base:
   ```bash
   python scripts/ingest.py
   ```
5. Run the API:
   ```bash
   uvicorn backend.app:app --reload
   ```
6. Run the frontend:
   ```bash
   streamlit run frontend/customer_chat.py
   ```
