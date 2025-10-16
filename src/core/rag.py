"""
RAG (Retrieval-Augmented Generation) implementation for wardrobe knowledge.

This module implements a vector store and retriever for style/wardrobe advice.
"""

import os
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def load_wardrobe_knowledge(file_path: str = None) -> List[Document]:
    """
    Load wardrobe rules from the knowledge base file.
    
    Args:
        file_path: Path to the wardrobe rules file
        
    Returns:
        List of Document objects containing wardrobe knowledge
    """
    if file_path is None:
        # Default to data/wardrobe_rules.txt
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(base_dir, "data", "wardrobe_rules.txt")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split into logical sections
    sections = content.split('\n\n')
    
    documents = []
    current_section = ""
    current_content = []
    
    for section in sections:
        if section.strip():
            # Check if this is a header (all caps or has ====)
            if section.isupper() or '====' in section:
                # Save previous section if exists
                if current_content:
                    doc = Document(
                        page_content='\n\n'.join(current_content),
                        metadata={"section": current_section}
                    )
                    documents.append(doc)
                    current_content = []
                
                # Start new section
                current_section = section.replace('=', '').strip()
            else:
                current_content.append(section)
    
    # Add final section
    if current_content:
        doc = Document(
            page_content='\n\n'.join(current_content),
            metadata={"section": current_section}
        )
        documents.append(doc)
    
    return documents


def create_wardrobe_vectorstore(
    documents: List[Document] = None,
    embeddings_model: str = "text-embedding-3-small"
) -> FAISS:
    """
    Create a FAISS vector store from wardrobe documents.
    
    Args:
        documents: List of Document objects (if None, loads default)
        embeddings_model: The OpenAI embeddings model to use
        
    Returns:
        A FAISS vector store
    """
    if documents is None:
        documents = load_wardrobe_knowledge()
    
    embeddings = OpenAIEmbeddings(
        model=embeddings_model,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore


def create_wardrobe_rag_chain(
    vectorstore: FAISS = None,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.7,
    k: int = 4
):
    """
    Create a RAG chain for wardrobe recommendations.
    
    Args:
        vectorstore: The FAISS vector store (if None, creates default)
        model_name: The OpenAI model to use
        temperature: The temperature for LLM responses
        k: Number of documents to retrieve
        
    Returns:
        A runnable RAG chain
    """
    if vectorstore is None:
        vectorstore = create_wardrobe_vectorstore()
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    template = """You are a wardrobe and packing expert. Use the following wardrobe knowledge to provide specific, actionable recommendations.

Weather Information:
{weather_info}

Relevant Wardrobe Guidelines:
{context}

User Query: {question}

Provide a detailed, practical packing list and wardrobe recommendations based on the weather and the wardrobe guidelines. Be specific about clothing items, accessories, and quantities."""

    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def create_rag_input(input_data):
        """Helper function to create the input for the RAG chain."""
        query = input_data["question"]
        weather_info = input_data["weather_info"]
        
        # Get relevant documents
        docs = retriever.invoke(query)
        context = format_docs(docs)
        
        return {
            "context": context,
            "question": query,
            "weather_info": weather_info
        }
    
    rag_chain = (
        create_rag_input
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain


class WardrobeRAG:
    """
    A wrapper class for the wardrobe RAG system.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        k: int = 4
    ):
        """
        Initialize the wardrobe RAG system.
        
        Args:
            model_name: The OpenAI model to use
            temperature: The temperature for LLM responses
            k: Number of documents to retrieve
        """
        self.vectorstore = create_wardrobe_vectorstore()
        self.chain = create_wardrobe_rag_chain(
            vectorstore=self.vectorstore,
            model_name=model_name,
            temperature=temperature,
            k=k
        )
    
    def get_recommendations(
        self,
        query: str,
        weather_info: Dict[str, Any]
    ) -> str:
        """
        Get wardrobe recommendations based on query and weather.
        
        Args:
            query: The user's question or request
            weather_info: Dictionary containing weather information
            
        Returns:
            Wardrobe recommendations as a string
        """
        # Format weather info for the prompt
        weather_text = self._format_weather_info(weather_info)
        
        # Run the RAG chain with properly formatted input
        input_data = {
            "question": query,
            "weather_info": weather_text
        }
        
        return self.chain.invoke(input_data)
    
    def _format_weather_info(self, weather_info: Dict[str, Any]) -> str:
        """
        Format weather information into a readable string.
        
        Args:
            weather_info: Dictionary containing weather data
            
        Returns:
            Formatted weather string
        """
        if isinstance(weather_info, str):
            return weather_info
        
        # Extract relevant weather data
        formatted = "Weather Forecast:\n"
        
        if "properties" in weather_info:
            periods = weather_info["properties"].get("periods", [])
            for period in periods[:7]:  # Show up to 7 periods (roughly a week)
                name = period.get("name", "Unknown")
                temp = period.get("temperature", "N/A")
                unit = period.get("temperatureUnit", "F")
                forecast = period.get("shortForecast", "N/A")
                wind = period.get("windSpeed", "N/A")
                
                formatted += f"\n{name}:\n"
                formatted += f"  Temperature: {temp}°{unit}\n"
                formatted += f"  Conditions: {forecast}\n"
                formatted += f"  Wind: {wind}\n"
        else:
            formatted += str(weather_info)
        
        return formatted
    
    def search_knowledge(self, query: str, k: int = 4) -> List[Document]:
        """
        Search the wardrobe knowledge base.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)

