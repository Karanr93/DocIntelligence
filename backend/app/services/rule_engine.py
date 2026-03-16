"""Rule-based keyword classifier for clause detection."""
from typing import List, Dict
import re


class RuleEngine:
    """
    First pass: fast keyword-based classification.
    Returns high/medium/low confidence based on keyword density.
    """

    HIGH_CONFIDENCE_THRESHOLD = 3
    MEDIUM_CONFIDENCE_THRESHOLD = 1

    def classify_text(
        self, text: str, keywords: List[str], category_name: str
    ) -> Dict:
        """
        Classify a page's text against a category's keywords.
        Returns {matched, confidence, matched_keywords, matched_spans}.
        """
        text_lower = text.lower()
        matched_keywords = []
        matched_spans = []

        for keyword in keywords:
            kw_lower = keyword.lower()
            pattern = re.compile(r'\b' + re.escape(kw_lower) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                matched_keywords.append(keyword)
                matched_spans.append({
                    "start": match.start(),
                    "end": match.end(),
                    "keyword": keyword
                })

        unique_keywords = list(set(matched_keywords))
        total_matches = len(matched_spans)

        if total_matches >= self.HIGH_CONFIDENCE_THRESHOLD:
            confidence = min(0.95, 0.70 + (total_matches * 0.05))
        elif total_matches >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            confidence = 0.40 + (total_matches * 0.10)
        else:
            confidence = 0.0

        return {
            "matched": total_matches > 0,
            "confidence": round(confidence, 2),
            "total_matches": total_matches,
            "unique_keywords": unique_keywords,
            "matched_spans": matched_spans,
            "source": "rule"
        }

    def find_keyword_bboxes(
        self, word_bboxes: List[Dict], keywords: List[str]
    ) -> List[Dict]:
        """Find bounding boxes of words that match any keyword."""
        matched_bboxes = []
        kw_set = {kw.lower() for kw in keywords}

        for wb in word_bboxes:
            word_lower = wb["word"].lower().strip(".,;:!?\"'()[]")
            if word_lower in kw_set:
                matched_bboxes.append({
                    "x0": wb["x0"],
                    "y0": wb["y0"],
                    "x1": wb["x1"],
                    "y1": wb["y1"],
                    "word": wb["word"]
                })

        return matched_bboxes


rule_engine = RuleEngine()
