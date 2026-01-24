import requests

def pull_model(model_name: str):
    """Pull a model from Ollama. The API returns streaming responses."""
    response = requests.post(
        "http://localhost:11434/api/pull",
        json={"name": model_name},
        stream=True
    )
    # Process streaming response
    for line in response.iter_lines():
        if line:
            # Each line is a JSON object with status updates
            pass  # You could log progress here if needed
    return response.status_code == 200

def query_llm(content: bytes, question: str, isImage: bool) -> str:
    """Query the LLM model with an image/ video and a question."""
    files = {
        ("image" if isImage else "video"): 
            ("image.jpg" if isImage else "video.mp4", content, 
             "image/jpeg" if isImage else "video/mp4"),
    }
    print(isImage)
    print(question)
    data = {
        "query": question
    }
    response = requests.post(
        "http://localhost:11434/api/ollama/query",
        files=files,
        data=data
    )
    if response.status_code == 200:
        return response.json().get("response", "No response from LLM.")
    else:
        return f"Error querying LLM: {response.status_code}"
