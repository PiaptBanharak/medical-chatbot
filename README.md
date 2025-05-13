# medical-chatbot
Thai medical chatbot using RAG (Retrieval-Augmented Generation) with Llama3 and patient records. Provides accurate and safe health advice in Thai via a Streamlit web interface. Demonstrates skills in AI, NLP, and full-stack development.


Testing Guidelines for Medical Chatbot Application

🧱 1. Environment Setup
Make sure the following components are installed and properly configured:

Python Dependencies

"pip install streamlit requests psycopg2-binary sentence-transformers
Ollama API"

Ensure the Ollama server is running at http://localhost:11434

Test via: curl http://localhost:11434 or access in a browser

PostgreSQL Database

Ensure the database mydb is running and accessible

Confirm the documents table exists with:

content (text)

embedding (vector type)

🧪 2. Function-level Testing
2.1 get_conn()
Test the connection manually in a Python shell:

conn = get_conn()
print(conn)
✅ Expected: Connection object with no exceptions

2.2 query_postgresql(query_text)
Run a test query:


results = query_postgresql("diabetes")
print(results)
✅ Expected: A list of tuples, e.g.


[("Patient has high blood sugar levels...", 0.12), ...]
2.3 generate_response(query_text)
Test the full response pipeline:

print(generate_response("What should a patient with high blood pressure eat?"))
✅ Expected: A meaningful answer in Thai using retrieved documents
❌ If no documents found: Return "Sorry, I couldn't find relevant information in the database."
❌ If Ollama fails: Return status code or exception details

2.4 Streamlit UI
Run the app:

streamlit run app.py
Check the following:

Chat input box appears and accepts input

Responses appear under the assistant's name

Previous messages are shown in the session

When errors occur, they are clearly shown (e.g. "เกิดข้อผิดพลาด: ...")
