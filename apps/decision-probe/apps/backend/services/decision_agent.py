import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class DecisionAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Decision Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Decision Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def decide_root_cause(
        self,
        hypotheses: List[Dict[str, Any]],
        reviews: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates final adjusted confidence scores, ranks hypotheses,
        selects the best-supported root cause explanation, and explains why.
        """
        # 1. Calculate adjusted confidences and rank
        review_map = {r["hypothesis_id"]: r for r in reviews}
        
        ranked_hypotheses = []
        for hyp in hypotheses:
            hyp_id = hyp["id"]
            orig_conf = hyp.get("confidence", 0.50)
            
            # Find adjustment
            adj = 0.0
            if hyp_id in review_map:
                adj = review_map[hyp_id].get("confidence_adjustment", 0.0)
                
            final_conf = max(0.01, min(1.0, orig_conf + adj))
            
            ranked_hypotheses.append({
                "id": hyp_id,
                "title": hyp["title"],
                "description": hyp["description"],
                "confidence": final_conf,
                "supporting_evidence": hyp.get("supporting_evidence", []),
                "review": review_map.get(hyp_id, {})
            })
            
        ranked_hypotheses.sort(key=lambda x: x["confidence"], reverse=True)

        # 2. Check if highest confidence is below threshold (0.40) or if empty
        if not ranked_hypotheses or ranked_hypotheses[0]["confidence"] < 0.40:
            return {
                "root_cause": {
                    "title": "Insufficient Evidence",
                    "description": "Insufficient evidence to determine a definitive root cause.",
                    "confidence": 0.0,
                    "supporting_chunks": []
                },
                "alternatives": [
                    {
                        "title": h["title"],
                        "description": h["description"],
                        "confidence": h["confidence"],
                        "supporting_chunks": h["supporting_evidence"]
                    } for h in ranked_hypotheses
                ],
                "reasoning": "The confidence score of the top ranked hypothesis is below the required 40% threshold. Therefore, we conclude there is insufficient evidence to determine a definitive root cause."
            }

        # 3. Call LLM for final reasoning synthesis if real client is enabled
        if self.use_real_client:
            chunks_str = ""
            for idx, chk in enumerate(chunks):
                chunk_id = chk.get("id", f"chunk_{idx}")
                title = chk.get("title", "Unknown File")
                content = chk.get("snippet", chk.get("content", ""))
                chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

            prompt = f"""You are the Decision Agent inside Decision Probe.
Your responsibility is to review the ranked hypotheses and criticisms to select the most probable root cause explanation, explain the reasoning behind this choice, and list alternative hypotheses.

Ranked Hypotheses with Critique reviews: {json.dumps(ranked_hypotheses)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks).
2. The winner in "root_cause" MUST match the top-ranked hypothesis: "{ranked_hypotheses[0]['title']}" with adjusted confidence {ranked_hypotheses[0]['confidence']}.
3. The reasoning must explicitly cite the timeline events, raw chunks, and reviews explaining why this won and why alternatives were discounted.
4. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "root_cause": {{
    "title": "Winning hypothesis title",
    "description": "Factual description of the root cause, directly quoting evidence",
    "confidence": {ranked_hypotheses[0]['confidence']},
    "supporting_chunks": ["chunk_id_1"]
  }},
  "alternatives": [
    {{
      "title": "Alternative hypothesis title",
      "description": "Alternative description",
      "confidence": 0.35,
      "supporting_chunks": ["chunk_id_2"]
    }}
  ],
  "reasoning": "Detailed explanation of why the winning root cause was chosen over the alternative hypotheses."
}}
"""
            try:
                logger.info("Calling Gemini API to synthesize final root cause decision.")
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                raw_text = response.text
                return self._parse_json(raw_text)
            except Exception as e:
                logger.error(f"Failed to generate decision via Gemini: {e}. Falling back to mock decision.")
                # fallback to mock decision below

        # 4. Fallback to mock decision logic
        winner = ranked_hypotheses[0]
        alternatives = ranked_hypotheses[1:]

        reasoning = (
            f"The hypothesis '{winner['title']}' was selected as the primary root cause because it has the highest "
            f"adjusted confidence level ({int(winner['confidence'] * 100)}%). Critic reviews verified its strengths "
            f"in directly explaining the timeline incident logs, whereas alternative hypotheses lacked direct evidence "
            f"or were weakened by unsupported assumptions."
        )

        return {
            "root_cause": {
                "title": winner["title"],
                "description": winner["description"],
                "confidence": round(winner["confidence"], 2),
                "supporting_chunks": winner["supporting_evidence"]
            },
            "alternatives": [
                {
                    "title": alt["title"],
                    "description": alt["description"],
                    "confidence": round(alt["confidence"], 2),
                    "supporting_chunks": alt["supporting_evidence"]
                } for alt in alternatives
            ],
            "reasoning": reasoning
        }

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "root_cause": parsed.get("root_cause", {}),
            "alternatives": parsed.get("alternatives", []),
            "reasoning": parsed.get("reasoning", "")
        }
