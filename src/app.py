import streamlit as st
import os
from query_engine import DinoGraphRAG

# Page Configuration
st.set_page_config(page_title="Graphosaurus Explorer", page_icon="🦖", layout="wide")

# Initialize the RAG Engine
@st.cache_resource
def get_rag_system():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Please set the GROQ_API_KEY environment variable.")
        st.stop()
    return DinoGraphRAG(api_key)

rag = get_rag_system()

# Sidebar: Project Info & Schema
with st.sidebar:
    st.title("🦖 Graphosaurus")
    st.markdown("---")
    st.subheader("Graph Schema")
    st.info("""
    **Nodes:** Dinosaur, Period, Clade, Continent  
    **Links:** LIVED_IN, BELONGS_TO, FOUND_IN
    """)
    st.markdown("---")
    st.caption("Powered by FalkorDB & Groq (Llama 3.3)")

# Main Chat Interface
st.title("Grounded Paleontology Assistant")
st.markdown("Ask natural language questions about dinosaurs. Answers are mathematically verified against the Knowledge Graph.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ex: Which herbivores lived in Asia during the Late Cretaceous?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Traversing the Graph..."):
            # We get the raw response from our engine
            full_response = rag.ask(prompt)
            st.markdown(full_response)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})