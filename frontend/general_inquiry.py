import requests

BACKEND_ASK_GENERAL_QUERY_URL = "http://localhost:8000/ask-general-query"

def ask_general_query(content, question, isImage=True) -> str:
    """Use a language model to answer a general question about the image."""
    response = requests.post(
        BACKEND_ASK_GENERAL_QUERY_URL,
        files={"file": ("image.jpg" if isImage else "video.mp4", 
                        content, 
                        "image/jpeg" if isImage else "video/mp4")},
        data={"question": question, "isImage": str(isImage)}
    )
    if response.status_code == 200:
        return response.json().get("response", "No response from LLM.")
    else:
        return f"Error querying LLM: {response.status_code}"