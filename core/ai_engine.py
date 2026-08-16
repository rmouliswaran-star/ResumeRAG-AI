from langchain_ollama import ChatOllama


def create_llm():
    return ChatOllama(
        model="qwen3:4b-instruct",
        temperature=0,
        base_url="http://localhost:11434",
        keep_alive="30m"
    )


def ask_ai(vector_db, question):
    llm = create_llm()

    docs = vector_db.max_marginal_relevance_search(
        question,
        k=4,
        fetch_k=20
    )

    context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    prompt = f"""
You are ResumeRAG AI.

Answer the user's question naturally and professionally using only the uploaded resume information.

If the information is not available in the resumes, say:
"No matching information found in uploaded resumes."

Resume Data:

{context}

User Question:

{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content