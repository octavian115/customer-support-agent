"""
FastAPI application for the TaskFlow support agent.

Endpoints:
    POST /chat              — Customer sends a message
    GET  /pending           — Get threads waiting for human review
    POST /review            — Human approves/rejects a pending action
    GET  /threads           — List all conversation threads
    GET  /thread/{id}/messages — Get full conversation history for a thread
"""

# TODO: Implement after graph is tested in notebook
