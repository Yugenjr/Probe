# Retrieval and Evidence Rules
Every recommendation, decision, or factual claim must reference evidence.

Example Evidence Sources:
- Uploaded JSON
- Workspace History
- Retrieved Documentation
- Research
- Model Card

## Resource Grounding Priority
When analyzing data, prefer sources in this order:
1. Uploaded files
2. Workspace history
3. Retrieved documentation
4. System knowledge

Never hallucinate documentation.
Never cite nonexistent URLs.
If no evidence exists, explicitly state: "Insufficient Evidence".
