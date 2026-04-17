# Customer Support Agent — Evaluation Suite

## Why This Exists

Evaluating an agent is fundamentally different from evaluating a single LLM call. An agent makes multiple decisions — which route to take, whether to escalate, whether to interrupt for human review — and each decision compounds. A correct final answer via the wrong path is still a bug waiting to surface in production.

This eval suite tests the agent at three layers:

1. **Component-level**: Does the classifier route correctly across all 7 categories?
2. **Trajectory-level**: Does the agent follow the expected path through the graph?
3. **Response-level**: Is the final output actually good?

## Golden Dataset Design

32 test cases across three difficulty tiers:

| Category | Count | Purpose |
|----------|-------|---------|
| `happy_path` | 20 | Core functionality — 2-4 per route across all 7 categories |
| `edge_case` | 7 | Ambiguous inputs, multi-intent, low confidence, boundary cases |
| `adversarial` | 5 | Prompt injections, empty input, rage, non-English |

### Why These Specific Cases?

**Happy path cases** validate all 7 routing paths: greeting, faq, technical, billing, escalation, off_topic, and closing. Billing cases all expect `expected_hitl: true` because the billing node uses `interrupt()` for human approval. Escalation cases expect `expected_hitl: false` because escalation is a handoff, not an interrupt.

**Edge cases** target the boundaries where the classifier breaks:
- `edge_ambiguous_01` has billing + technical signals — tests which intent wins
- `edge_confidence_01` is a nonsense technical question that should trigger confidence-based escalation (RAG returns < 0.60)
- `edge_greeting_vs_faq` tests whether "Hi, how do I create a project?" classifies as greeting or FAQ

**Adversarial cases** test safety and robustness:
- `adversarial_01` and `adversarial_02` are prompt injections
- `adversarial_03` is empty input
- `adversarial_05` is Hindi — tests non-English handling

## Eval Metrics

### Classification Accuracy
Does `state.intent` match the expected route? Uses the classifier's structured Pydantic output directly — no trajectory parsing needed for this metric.

### Trajectory Accuracy
Does the agent visit the correct sequence of nodes? Each route has defined valid trajectories:
- `faq` → `classify → rag_node → response_node` (or `→ escalation_node` if confidence < 0.60)
- `billing` → `classify → rag_node → billing_node` (then HITL interrupt)
- `escalation` → `classify → escalation_node` (generates summary, no interrupt)

### HITL Accuracy
Did the agent interrupt when it should have (billing) and NOT interrupt when it shouldn't (everything else)? False positives waste reviewer time; false negatives let unauthorized billing actions through.

### Confidence-Based Escalation
For faq/technical routes only: did low RAG confidence (< 0.60) correctly redirect to escalation instead of generating a potentially hallucinated response?

### LLM-as-Judge (GPT-4o)
Scores on four dimensions (1-5): relevance, faithfulness, safety, tone.

### Confusion Matrix
Shows misrouting patterns across all 7 categories.

## How to Use

### 1. Place Files

Drop the `evals/` directory into your project root:
```
customer-support-agent/
├── backend/
├── evals/           ← here
│   ├── golden_dataset.json
│   ├── run_evals.py
│   └── README.md
├── frontend/
└── ...
```

### 2. Verify Imports

The harness imports from your existing code:
```python
from backend.graph import build_graph
from backend.state import SupportState
```

If `build_graph` takes different arguments, adjust line ~165 in `run_evals.py`.

### 3. Check State Field Names

The harness reads these fields from `SupportState`:
- `intent` — the classifier's output category
- `confidence` — RAG retrieval confidence score
- `escalation_reason` — why escalation was triggered
- `messages` — conversation history

If your field names differ, update the `run_agent()` function.

### 4. Run

```bash
# Full suite, no LLM judge (fast, free)
python -m evals.run_evals --skip-llm-judge

# Happy path only
python -m evals.run_evals --category happy_path --skip-llm-judge

# Single case for debugging
python -m evals.run_evals --id billing_01 --skip-llm-judge

# Full suite with LLM judge (costs ~$0.10-0.20 in API calls)
python -m evals.run_evals
```

### 5. Read Results

- `eval_report.md` — formatted report with metrics, confusion matrix, failure details
- `eval_results.json` — raw data for programmatic analysis

## Iterating on Results

1. Run evals → get baseline metrics
2. Look at failures → identify patterns (prompt issue? threshold issue? category overlap?)
3. Fix the root cause, not the symptom
4. Re-run evals → confirm the fix didn't break other cases
5. Add new test cases for the failure mode you just fixed

**Example**: If `edge_greeting_vs_faq` fails because "Hi, how do I create a project?" classifies as greeting, the fix is in the classifier prompt — add guidance that questions with actionable intent override greetings. After fixing, add 2-3 more greeting+question combos to ensure it generalizes.

## What Comes Next

- **Retrieval evals**: Capture chunks from `rag_node` and score context precision/recall separately
- **Multi-turn evals**: Test conversation flows across multiple messages
- **Regression testing**: Run evals in CI on every prompt change
- **Ragas integration**: Add standardized RAG metrics once the custom harness is stable
- **Latency tracking**: Measure per-node and end-to-end execution time
