def llm_answer_question(image, question):
    """Use a language model to answer a general question about the image."""
    response = llm_api.ask(image=image, prompt=question)
    return response