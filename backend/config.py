"""
Shared configuration for the TaskFlow support agent.

Initializes LLM, embedding model, and Pinecone index.
All nodes import from here — single source of truth for clients.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone

load_dotenv()

# -------------------
# LLM
# -------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# -------------------
# Embeddings
# -------------------
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# -------------------
# Pinecone
# -------------------
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index("taskflow-support")

PINECONE_NAMESPACE = "taskflow-kb"

# -------------------
# Agent settings
# -------------------
CONFIDENCE_THRESHOLD = 0.65  # below this, escalate instead of responding
