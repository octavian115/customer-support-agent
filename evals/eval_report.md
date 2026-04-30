# Customer Support Agent — Eval Report

**Run date:** 2026-04-30 18:39:44
**Total cases:** 32

## Overall Metrics

| Metric | Score |
|--------|-------|
| Classification Accuracy | 100% |
| Trajectory Accuracy | 100% |
| HITL Accuracy | 100% |
| Overall Pass Rate (class + HITL) | 100% |

## Per-Route Classification Accuracy

| Route | Cases | Accuracy |
|-------|-------|----------|
| billing | 7 | 100% |
| closing | 2 | 100% |
| escalation | 7 | 100% |
| faq | 7 | 100% |
| greeting | 4 | 100% |
| off_topic | 2 | 100% |
| technical | 3 | 100% |

## Per-Category Breakdown

| Category | Cases | Classification | HITL |
|----------|-------|---------------|------|
| adversarial | 5 | 100% | 100% |
| edge_case | 7 | 100% | 100% |
| happy_path | 20 | 100% | 100% |

## Confidence-Based Escalation

Applicable cases (faq/technical): 10
Correct routing: 10/10 (100%)

## Routing Confusion Matrix

| Expected → Actual | Count |
|-------------------|-------|
| billing → billing ✓ | 7 |
| closing → closing ✓ | 2 |
| escalation → escalation ✓ | 7 |
| faq → faq ✓ | 7 |
| greeting → greeting ✓ | 4 |
| off_topic → off_topic ✓ | 2 |
| technical → technical ✓ | 3 |
