"""
Vector Database Module - ChromaDB Integration
Initializes and manages vector embeddings for the customer support knowledge base.
"""

import chromadb
import json
import os
from typing import List, Dict, Optional


class VectorDB:
    """ChromaDB Vector Database for semantic search."""
    
    def __init__(self, persist_dir: str = "./chroma_data"):
        """
        Initialize ChromaDB with persistence.
        
        Args:
            persist_dir: Directory to store vector database files
        """
        # Create persist directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with new API (v0.4+)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.persist_dir = persist_dir
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="customer_support_kb",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for embeddings
        )
        
        print(f"✓ Vector DB initialized at {persist_dir}")
        print(f"✓ Collection: {self.collection.name}")
        print(f"✓ Current documents in collection: {self.collection.count()}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector database with embeddings.
        ChromaDB automatically generates embeddings using OpenAI API.
        
        Args:
            documents: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        
        if not documents:
            print("⚠ No documents provided")
            return
        
        # Generate metadata if not provided
        if metadatas is None:
            metadatas = [{"source": f"kb_doc_{i}", "index": i} for i in range(len(documents))]
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}_{hash(doc)%10000}" for i, doc in enumerate(documents)]
        
        try:
            # Add documents with ChromaDB (auto-generates embeddings)
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"\n✓ Successfully added {len(documents)} documents to vector database")
            for i, doc in enumerate(documents):
                preview = doc[:60] + "..." if len(doc) > 60 else doc
                print(f"  [{i+1}] {preview}")
        
        except Exception as e:
            print(f"✗ Error adding documents: {e}")
    
    def search(self, query: str, top_k: int = 3) -> Dict:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            Dict with keys:
                - documents: List of similar documents
                - distances: List of distances (lower = more similar)
                - similarities: List of similarity scores (higher = more similar)
                - metadatas: List of document metadata
        """
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Convert distance to similarity (for user clarity)
            distances = results.get("distances", [[]])[0]
            similarities = [1 - d for d in distances]  # Inverse of distance
            
            return {
                "documents": results["documents"][0],
                "distances": distances,
                "similarities": similarities,
                "metadatas": results["metadatas"][0],
                "query": query
            }
        
        except Exception as e:
            print(f"✗ Error searching: {e}")
            return {
                "documents": [],
                "distances": [],
                "similarities": [],
                "metadatas": [],
                "query": query
            }
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector collection."""
        
        count = self.collection.count()
        
        return {
            "total_documents": count,
            "collection_name": self.collection.name,
            "persist_directory": self.persist_dir
        }
    
    def persist(self) -> None:
        """Explicitly persist (save) the database to disk."""
        try:
            # With PersistentClient, data is automatically persisted
            # This method is kept for compatibility
            print("✓ Vector database is automatically persisted with PersistentClient")
        except Exception as e:
            print(f"✗ Error with persistence: {e}")
    
    def reset(self) -> None:
        """Delete all documents from the collection (but keep collection)."""
        try:
            self.client.delete_collection(name="customer_support_kb")
            self.collection = self.client.get_or_create_collection(
                name="customer_support_kb",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Vector database reset (all documents deleted)")
        except Exception as e:
            print(f"✗ Error resetting database: {e}")
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a specific document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            print(f"✓ Document {doc_id} deleted")
        except Exception as e:
            print(f"✗ Error deleting document: {e}")


def initialize_sample_database():
    """
    Initialize vector database with sample customer support knowledge base.
    This is a demo function - customize with your actual KB.
    """
    
    print("\n" + "="*70)
    print("INITIALIZING VECTOR DATABASE FOR CUSTOMER SUPPORT")
    print("="*70 + "\n")
    
    # Initialize database
    db = VectorDB(persist_dir="./chroma_data")
    
    # Load knowledge base from the shared JSON file
    _kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    with open(_kb_path, "r", encoding="utf-8") as _f:
        knowledge_base = json.load(_f)
    
    # Add documents to vector database
    db.add_documents(knowledge_base)
    
    # Persist to disk
    db.persist()
    
    # Display stats
    stats = db.get_collection_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total Documents: {stats['total_documents']}")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Storage: {stats['persist_directory']}")
    
    # Test search functionality
    print("\n" + "-"*70)
    print("TESTING VECTOR SEARCH")
    print("-"*70 + "\n")
    
    test_queries = [
        "How do I reset my password?",
        "What payment methods do you accept?",
        "How long does shipping take?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = db.search(query, top_k=2)
        
        for i, (doc, sim) in enumerate(zip(results["documents"], results["similarities"]), 1):
            print(f"\n   [{i}] Similarity: {sim:.4f}")
            print(f"       {doc[:80]}...")
    
    print("\n" + "="*70)
    print("✓ VECTOR DATABASE INITIALIZATION COMPLETE")
    print("="*70 + "\n")
    
    return db


if __name__ == "__main__":
    # Initialize database with sample data
    db = initialize_sample_database()
