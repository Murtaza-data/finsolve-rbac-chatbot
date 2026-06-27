
import os
import streamlit as st
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DEPARTMENT_FILES = {
    "engineering": ["data/engineering/engineering_master_doc.md"],
    "finance": ["data/finance/financial_summary.md", "data/finance/quarterly_financial_report.md"],
    "hr_dept": ["data/hr/employee_handbook.md", "data/hr/hr_data.csv"],
    "marketing": [
        "data/marketing/marketing_report_2024.md",
        "data/marketing/marketing_report_q1_2024.md",
        "data/marketing/marketing_report_q2_2024.md",
        "data/marketing/marketing_report_q3_2024.md",
        "data/marketing/market_report_q4_2024.md"
    ],
    "general": ["data/general/employee_handbook.md"]
}

ROLE_COLLECTIONS = {
    "Finance Team":      ["finance"],
    "HR Team":           ["hr_dept"],
    "Marketing Team":    ["marketing"],
    "Engineering Team":  ["engineering"],
    "C-Level Executive": ["engineering", "finance", "hr_dept", "marketing", "general"],
    "Employee":          ["general"]
}

@st.cache_resource
def load_vectorstores():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    vectorstores = {}
    for department, files in DEPARTMENT_FILES.items():
        all_docs = []
        for filepath in files:
            if filepath.endswith(".csv"):
                loader = CSVLoader(filepath)
            else:
                loader = TextLoader(filepath, encoding="utf-8")
            all_docs.extend(loader.load())
        chunks = splitter.split_documents(all_docs)
        vectorstores[department] = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=department
        )
    return vectorstores

def get_answer(question, role, vectorstores, api_key):
    collections = ROLE_COLLECTIONS[role]
    all_docs = []
    for col in collections:
        retriever = vectorstores[col].as_retriever(search_kwargs={"k": 3})
        all_docs.extend(retriever.invoke(question))
    context = "\n\n".join([doc.page_content for doc in all_docs])
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    prompt = ChatPromptTemplate.from_template("""
You are an internal assistant for FinSolve Technologies.
Answer the question using only the context provided below.
If the answer is not in the context, say: "I don't have information about that in your accessible documents."

Context:
{context}

Question: {question}

Answer:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})

# --- Page Config ---
st.set_page_config(page_title="FinSolve Chatbot", page_icon="🏦", layout="wide")

# --- Sidebar ---
st.sidebar.title("🏦 FinSolve Technologies")
st.sidebar.markdown("Internal Knowledge Assistant")
st.sidebar.markdown("---")
groq_api_key = st.sidebar.text_input(
    "🔑 Enter Groq API Key",
    type="password",
    help="Get your free key at console.groq.com"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### How it works")
st.sidebar.markdown("""
- Enter your Groq API key above
- Select your role to login
- Ask questions about your department
- Only your allowed data is searched
""")
st.sidebar.markdown("---")
st.sidebar.markdown("### Tech Stack")
st.sidebar.markdown("""
- 🦙 LLaMA 3.1 (Groq)
- 🔗 Langchain
- 🗄️ ChromaDB
- 🤗 HuggingFace Embeddings
- 🎨 Streamlit
""")
st.sidebar.markdown("---")
st.sidebar.markdown("[GitHub Profile](https://github.com/Murtaza-data)")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Login Screen ---
if not st.session_state.logged_in:
    st.title("🏦 FinSolve Technologies")
    st.subheader("Internal Knowledge Assistant")
    st.markdown("### RAG + RBAC + LLaMA + Langchain")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔐 Role-based access control")
    with col2:
        st.info("🗄️ Department-specific data")
    with col3:
        st.info("🤖 AI-powered answers")

    st.markdown("---")
    st.markdown("### Select Your Role to Login")
    role = st.selectbox("", list(ROLE_COLLECTIONS.keys()))
    if st.button("🔐 Login", type="primary", use_container_width=True):
        if not groq_api_key:
            st.warning("⚠️ Please enter your Groq API key in the sidebar first.")
        else:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.messages = []
            st.rerun()

# --- Chat Screen ---
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🏦 FinSolve Chatbot")
        st.markdown(f"Logged in as: **{st.session_state.role}**")
    with col2:
        st.markdown("###")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    vectorstores = load_vectorstores()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask a question about your department..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_answer(prompt, st.session_state.role, vectorstores, groq_api_key)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    st.markdown("---")
    st.markdown(
        "Powered by RAG + RBAC + LLaMA + Langchain | "
        "[GitHub](https://github.com/Murtaza-data)"
    )
