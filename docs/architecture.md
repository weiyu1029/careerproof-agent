# Architecture

## Current architecture

```text
User JSON input
  ↓
CareerProof Agent
  ↓
privacy redaction
  ↓
job signal extraction
  ↓
industry matching
  ↓
evidence prompt construction
  ↓
Gemini reasoning
  ↓
structured career intelligence report
```

## Data assets

- `app/data/industries.json`: 25 industry interview knowledge packs
- `app/tools/privacy.py`: personal information redaction
- `app/tools/job_signals.py`: deterministic role signal extraction
- `app/tools/industry_map.py`: industry matching
- `app/tools/evidence_mapper.py`: candidate proof hints

## Output structure

1. Role Problem Map
2. Industry Context
3. Hiring Evidence Matrix
4. Candidate Proof Mapping
5. Interview Story Bank
6. Likely Interview Questions
7. Gap Analysis
8. 7-Day Prep Plan
9. Questions to Ask Interviewer
