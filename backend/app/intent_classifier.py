from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

intents = {
    "object_detection": "detect objects in the image/video",
    "general_inquiry": "ask any general question in the image/video"
}

intent_embeddings = {k: model.encode(v) for k, v in intents.items()}

def classify_intent(text):
    text_emb = model.encode(text)
    scores = {k: util.cos_sim(text_emb, emb).item() for k, emb in intent_embeddings.items()}
    return max(scores, key=scores.get)
