import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config
from logger_config import shifu_logger
from security import SecurityValidator

GROQ_MODEL = config.groq_model
KNOWLEDGE_BASE_FILE = config.knowledge_base_file
VECTOR_DB_PATH = config.vector_db_path

def load_llm(max_tokens: int = 4096):
    """Load LLM with secure configuration"""
    try:
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=config.groq_api_key,
            temperature=0.3,
            max_tokens=max_tokens
        )
        shifu_logger.info("LLM initialized successfully")
        return llm
    except Exception as e:
        shifu_logger.error("Failed to initialize Groq LLM", exception=e)
        st.error(f"Error initializing LLM: {str(e)}")
        return None

def initialize_vector_store():
    """Initialize vector store with proper error handling and logging"""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        shifu_logger.info("Embeddings model loaded")
        
        if not os.path.exists(KNOWLEDGE_BASE_FILE):
            shifu_logger.critical(f"Knowledge base file '{KNOWLEDGE_BASE_FILE}' not found")
            st.error(f"Knowledge base file '{KNOWLEDGE_BASE_FILE}' not found!")
            return None
        
        kb_modified_time = os.path.getmtime(KNOWLEDGE_BASE_FILE)
        rebuild_needed = False
        
        if os.path.exists(VECTOR_DB_PATH):
            try:
                timestamp_file = os.path.join(VECTOR_DB_PATH, "last_build.txt")
                
                if os.path.exists(timestamp_file):
                    with open(timestamp_file, 'r') as f:
                        last_build_time = float(f.read())
                    
                    if kb_modified_time > last_build_time:
                        shifu_logger.info("Knowledge base updated, rebuilding vector store")
                        st.info("Knowledge base has been updated. Rebuilding vector database...")
                        rebuild_needed = True
                    else:
                        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
                        shifu_logger.info("Vector store loaded from cache")
                        return vector_store
                else:
                    rebuild_needed = True
            except Exception as e:
                shifu_logger.error("Failed to load existing vector store", exception=e)
                st.warning(f"Failed to load existing index: {str(e)}. Rebuilding...")
                rebuild_needed = True
        else:
            rebuild_needed = True
        
        if rebuild_needed:
            return _build_vector_store(embeddings, kb_modified_time)
        
    except Exception as e:
        shifu_logger.critical("Failed to initialize vector store", exception=e)
        st.error(f"Error initializing vector store: {str(e)}")
        return None

def _build_vector_store(embeddings, kb_modified_time):
    """Build vector store from scratch"""
    try:
        loader = TextLoader(KNOWLEDGE_BASE_FILE, encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        shifu_logger.info(f"Processing {len(chunks)} document chunks")
        
        with st.spinner("Creating Vector Store (this may take a moment)..."):
            vector_store = FAISS.from_documents(chunks, embeddings)
            vector_store.save_local(VECTOR_DB_PATH)
            
            # Save timestamp
            timestamp_file = os.path.join(VECTOR_DB_PATH, "last_build.txt")
            with open(timestamp_file, 'w') as f:
                f.write(str(kb_modified_time))
            
            shifu_logger.info("Vector store built and saved successfully")
            st.success("Vector database updated successfully!")
        
        return vector_store
    except Exception as e:
        shifu_logger.error("Failed to build vector store", exception=e)
        st.error(f"Error creating vector store: {str(e)}")
        return None

def get_rag_chain(llm, vector_store):
    """Creates the RAG chain."""
    
    template = """You are Shifu, the AI Knowledge Agent for SetuSchool. 
    Use the following pieces of context to answer the user's question. 
    If the answer is not in the context, say "I don't have that information based on the public setuschool.com data." 
    Provide accurate, focused, and actionable guidance.
    
    Context:
    {context}
    
    User: {question}
    Shifu:"""
    
    prompt = PromptTemplate(
        template=template, 
        input_variables=["context", "question"]
    )
    
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return chain
