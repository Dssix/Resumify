# To move between folders
import os
# To embed the data
from sentence_transformers import SentenceTransformer
# To use chromadb
from chromadb import PersistentClient,Client
# To load and chunk documents
from backend.data_processing.data_loader import load_and_chunk_documents
# For unique id for each chunk
from uuid import uuid4
# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# To use config data
try:
    from config import(
        INDEX_DIR,
        CHROMA_COLLECTION_NAME,
        EMBEDDING_MODEL_NAME,
        OPENAI_API_KEY
    )
except ImportError:
    INDEX_DIR="index"
    CHROMA_COLLECTION_NAME="my_collections"
    EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
    OPENAI_API_KEY=None
    logger.warning("Config.py not found. Using default values!")


# Returns a chroma client copy on disk at INDEX_DIR address and returns collections
def get_chroma_collection(collection_name:str=CHROMA_COLLECTION_NAME):
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        logger.info(f"Created index directory: {INDEX_DIR}")
    client=PersistentClient(path=INDEX_DIR)
    collection=client.get_or_create_collection(collection_name)
    logger.info(f"Connected to Chromadb collection: {collection_name}")
    return collection


# Embedding function for openai
def embed_texts(texts: list[str]) -> list[list[float]]:
    model=SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model.encode(texts).tolist()


# Generate embeddings and add to collection documents
def add_documents(chunks: list[dict],collections):
    if not chunks:
        logger.warning("No chunks to add.")
        return
    ids=[str(uuid4()) for _ in range(len(chunks))]
    text=[chunk["text"] for chunk in chunks]
    embedding=embed_texts(text)
    metadata=[chunk["metadata"] for chunk in chunks]
    try:
        collections.add(
            ids=ids,
            embeddings=embedding,
            metadatas=metadata,
            documents=text
        )
        logger.info(f"Added {len(chunks)} to Chromadb")
    except Exception as e:
        logger.error(f"Error adding Documents to chromadb.\nError:{e}")


# Search for the similar text in the database and return top k results
def search(query: str, top_k: int,collections) -> list[dict]:
    query_embedding=embed_texts([query])[0]
    data=collections.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    results=[]
    if 'ids' in data and 'distances' in data and 'documents' in data and 'metadatas' in data:
        for i in range(len(data['ids'][0])):
            results.append({
                "id":data['ids'][0][i],
                "score":data['distances'][0][i],
                "document":data['documents'][0][i],
                "metadata":data['metadatas'][0][i]
            })
        logger.info(f"Search query: {query}, returned {len(results)} results")
    else:
        logger.error("Required data is not present in database")
    return results


# Function to clear the collections after using
def clear_collection(collection_name):
    logger.info(f"Attempting to clear collection: {collection_name}")
    try:
        if not os.path.exists(INDEX_DIR):
            logger.warning(f"Directory {INDEX_DIR} not found")
            return
        client=PersistentClient(INDEX_DIR)
        client.delete_collection(collection_name)
        logger.info(f"Collection {collection_name} cleared!")
    except Exception as e:
        logger.error(f"Error Occured during clearing collection: {e}")


# Initilize chromadb
def initializer(collection_name:str=CHROMA_COLLECTION_NAME):
    clear_collection(collection_name)
    logger.info(f"Getting Collection: {collection_name}")
    collection=get_chroma_collection(collection_name)
    all_chunks=load_and_chunk_documents()
    logger.info(f"Adding {len(all_chunks)} chunks in collection")
    add_documents(all_chunks,collection)
    logger.info(f"Collection {collection_name} Initialized")