from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

# Keyword guards handle common voice commands that should always map to detection.
DETECTION_KEYWORDS = {
    "detect", "find", "locate", "spot", "identify", "track", "search", "where",
    "show", "recognize", "recognise", "count"
}

GENERAL_KEYWORDS = {
    "what", "why", "how", "describe", "explain", "tell", "summary", "summarize",
    "analyse", "analyze", "question", "about"
}

# Use several intent examples and score against the best-matching example.
INTENT_EXAMPLES = {
    "object_detection": [
        "detect person in this image",
        "find a car and a bicycle",
        "locate the bottle",
        "spot all objects in this frame",
        "identify the cat in this video",
        "where is the dog",
        "count people in the image",
    ],
    "general_inquiry": [
        "what is happening in this image",
        "describe this scene",
        "explain what you see",
        "tell me about this video",
        "summarize the content",
        "analyze this frame",
        "answer a general question about this media",
    ],
}

INTENT_EMBEDDINGS = {
    label: model.encode(examples) for label, examples in INTENT_EXAMPLES.items()
}


def _tokenize(text: str) -> set[str]:
    normalized = ''.join(ch.lower() if ch.isalnum() else ' ' for ch in text)
    return set(normalized.split())


def classify_intent(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "object_detection"

    tokens = _tokenize(text)
    if tokens & DETECTION_KEYWORDS:
        return "object_detection"

    if tokens & GENERAL_KEYWORDS and "object" not in tokens:
        return "general_inquiry"

    text_emb = model.encode(text)
    scores = {}

    for label, embeddings in INTENT_EMBEDDINGS.items():
        similarities = util.cos_sim(text_emb, embeddings)[0]
        scores[label] = float(similarities.max())

    best_intent = max(scores, key=scores.get)

    # For low-confidence/near-tie cases, prefer detection so voice commands
    # like "cycle please" do not incorrectly route to general inquiry.
    if abs(scores["object_detection"] - scores["general_inquiry"]) < 0.03:
        return "object_detection"

    return best_intent
