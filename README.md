# FinSolve RBAC Chatbot

A role-based access control chatbot for FinSolve Technologies. Employees log in with their role and can only ask questions about their department's data. The AI generates answers strictly from allowed documents.

## Live Demo
[Try the app here]([PASTE_STREAMLIT_LINK_HERE](https://finsolve-rbac-chatbot-l6q2e5bgdvd8hen3x5etmu.streamlit.app/))

## What It Does
- Login with your role (Finance, HR, Marketing, Engineering, C-Level, Employee)
- Ask questions in natural language
- Get AI-generated answers from your department's documents only
- C-Level executives have access to all departments

## Tech Stack
- LLaMA 3.1 via Groq
- Langchain
- ChromaDB
- HuggingFace Embeddings
- Streamlit
