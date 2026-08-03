"""
RAG (Retrieval-Augmented Generation) Engine
"""


import os
import json
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Use absolute import
from utils.logger import get_logger

logger = get_logger(__name__)





class RAGEngine:
    """Retrieval-Augmented Generation engine for local documentation."""
    
    def __init__(self, docs_path: str, config):
        """Initialize the RAG engine."""
        self.config = config
        self.docs_path = Path(docs_path)
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.is_ready = False
        
        # Embedding model - using smaller model for memory efficiency
        self.model_name = config.get('rag.embedding_model', 'all-MiniLM-L6-v2')
        self.chunk_size = config.get('rag.chunk_size', 512)
        self.overlap = config.get('rag.overlap', 50)
        
        # Initialize
        self.setup()
    
    def setup(self):
        """Setup the RAG engine."""
        try:
            # Load embedding model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded")
            
            # Load or build index
            index_path = self.docs_path / "rag_index.pkl"
            docs_path = self.docs_path / "documents.pkl"
            
            if index_path.exists() and docs_path.exists():
                self.load_index(index_path, docs_path)
            else:
                self.build_index()
            
            self.is_ready = True
            logger.info("RAG engine ready")
            
        except Exception as e:
            logger.error(f"RAG setup failed: {e}")
            self.is_ready = False
    
    def build_index(self):
        """Build the RAG index from documentation."""
        if not self.docs_path.exists():
            logger.warning("Documents path not found")
            return
        
        documents = []
        
        # Load all text files
        for file_path in self.docs_path.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents.append({
                    'id': file_path.stem,
                    'content': content,
                    'source': file_path.name
                })
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        if not documents:
            logger.warning("No documents found")
            return
        
        # Chunk documents
        chunks = []
        for doc in documents:
            doc_chunks = self._chunk_text(doc['content'])
            for chunk in doc_chunks:
                chunks.append({
                    'content': chunk,
                    'source': doc['source'],
                    'id': doc['id']
                })
        
        if not chunks:
            logger.warning("No chunks created")
            return
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype(np.float32))
        self.documents = chunks
        
        # Save index
        self.save_index()
        
        logger.info(f"Index built with {len(chunks)} chunks")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = ' '.join(chunk_words)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def query(self, query: str, top_k: int = 3) -> Optional[str]:
        """Query the RAG engine."""
        if not self.is_ready or self.index is None:
            return None
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search index
            distances, indices = self.index.search(
                query_embedding.astype(np.float32),
                min(top_k, len(self.documents))
            )
            
            # Get relevant documents
            results = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    results.append(self.documents[idx])
            
            if not results:
                return None
            
            # Combine results
            context = "\n\n".join([r['content'] for r in results[:top_k]])
            return context
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return None
    
    def save_index(self):
        """Save the index and documents."""
        if self.index is None:
            return
        
        index_path = self.docs_path / "rag_index.pkl"
        docs_path = self.docs_path / "documents.pkl"
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(index_path).replace('.pkl', '.faiss'))
            
            # Save documents
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info("RAG index saved")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self, index_path: Path, docs_path: Path):
        """Load the index and documents."""
        try:
            # Load FAISS index
            faiss_path = str(index_path).replace('.pkl', '.faiss')
            if os.path.exists(faiss_path):
                self.index = faiss.read_index(faiss_path)
            else:
                self.build_index()
                return
            
            # Load documents
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            logger.info(f"RAG index loaded: {len(self.documents)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self.build_index()
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_ready = False
        self.index = None
        self.documents = []
        self.embedding_model = None
        logger.info("RAG engine cleaned up")