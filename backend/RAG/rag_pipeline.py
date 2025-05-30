# Imports for processing
from config import INDEX_DIR,DATA_DIR,CHROMA_COLLECTION_NAME,INDEX_DIR as KEYWORD_INDEX_DIR
from backend.data_processing.data_loader import load_and_chunk_documents # Adjusted to be more specific
from keyword_store import(
    create_index as create_keyword,
    open_index as open_keyword,
    add_documents as add_keyword
    )
from .vector_store import(
    get_chroma_collection as get_vector_collection,
    add_documents as add_vector,
    clear_collection
)
from .hybrid_retriever import hybrid_search
from .llm_interface import generate

import os
import shutil

# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# To create prompt
def create_prompt(query:str,context_chunks:list[dict])->str:
    chunk_texts=[chunk.get('document','') for chunk in context_chunks]
    separator = "\n\n---\n\n"
    context_string=separator.join(chunk_texts)
    prompt = f"""
You are a helpful assistant that answers questions using only the provided context document.

Context Document:
<context>
{context_string}
</context>

The query is {query}

Respond Based on the provided context document, """
    return prompt.strip()


# To hold the vector collection handle
vector_collection_handle=None


# Initilize rag and if checks if there is a need to create a new index for both vector and keyword serach
def initialize_rag(force_reindex:bool=False):
    global vector_collection_handle
    logger.info(f"Initializing RAG (Force Re-Index: {force_reindex})")

    # --- START: Directory Cleanup (Handle file locks by deleting FIRST) ---
    if force_reindex:
        logger.warning(f"Force re-index requested. Attempting to delete index directory: {INDEX_DIR}")
        try:
            # Delete the entire index directory which contains both Chroma and Keyword index
            if os.path.exists(INDEX_DIR):
                 shutil.rmtree(INDEX_DIR)
                 logger.info(f"Removed index directory: {INDEX_DIR}")
            else:
                 logger.info(f"Index directory {INDEX_DIR} does not exist, no need to delete.")
        except PermissionError as e:
             logger.error(f"Permission error deleting index directory {INDEX_DIR}: {e}. Ensure no other process is using files inside it.", exc_info=True)
             # Re-raising might stop execution if this is critical, or just log and let subsequent steps fail
             # For now, we log and continue, but the next steps will likely fail if cleanup failed.
        except OSError as e:
             logger.error(f"Error deleting index directory {INDEX_DIR}: {e}. Proceeding with re-index attempt.", exc_info=True)
        except Exception as e:
             logger.error(f"Unexpected error during index directory cleanup: {e}", exc_info=True)
    # --- END: Directory Cleanup ---


    # Get/Create Chroma Collection (will create dir if deleted or non-existent)
    vector_collection = get_vector_collection(CHROMA_COLLECTION_NAME)
    vector_count = vector_collection.count()
    logger.info(f"There are {vector_count} vectors in {CHROMA_COLLECTION_NAME}")

    # Check Keyword Index state (will create dir if deleted or non-existent)
    keyword_index_exists_and_populated = (
        os.path.exists(KEYWORD_INDEX_DIR) and
        len(os.listdir(KEYWORD_INDEX_DIR)) > 0 # Check if directory has files/subdirs
    )
    if keyword_index_exists_and_populated:
        logger.info(f"Keyword store directory found and populated at: {KEYWORD_INDEX_DIR}")
    else:
        logger.info(f"Keyword store index not found or empty at: {KEYWORD_INDEX_DIR}")


    # Determine if indexing is needed (if force_reindex was false, or if cleanup failed)
    vector_needs_indexing = (vector_count == 0)
    keyword_needs_indexing = (not keyword_index_exists_and_populated)

    if vector_needs_indexing or keyword_needs_indexing:
        logger.info("Indexing is needed. Loading and chunking documents from DATA_DIR")
        data=load_and_chunk_documents()
        if data:
            if vector_needs_indexing:
                logger.info("Adding documents to Vector store...")
                add_vector(data,vector_collection)
                logger.info("Vectors Added")
            if keyword_needs_indexing:
                logger.info("Adding documents to Keyword store...")
                # Ensure keyword index directory and schema exist before adding
                if not os.path.exists(KEYWORD_INDEX_DIR):
                    logger.info(f"Creating keyword index directory and schema before adding documents")
                    create_keyword() # create_keyword already handles dir creation
                add_keyword(data)
                logger.info("Keywords Added")
        else:
            logger.warning("No Documents found or loaded from DATA_DIR. Skipping Adding to stores")
    else:
        logger.info("Stores are up-to-date")

    # Store the handle for later use
    vector_collection_handle=vector_collection
    logger.info("RAG initialization complete.")



# Main orchestrate to RAG, takes user query as string and provide resutlt using data
def answer_query(query:str,prompt:str="")->str:
    if not query:
        logger.warning("Query is Empty. Returning Back to calling function.")
        return "Please provide a query."
    data=hybrid_search(query=query,vector_collection=vector_collection_handle)
    if not data:
        logger.warning("The Hybrid search returned no data. Returning to calling function.")
        return "Sorry, I couldn't find relevant information."
    # if state:
    #     prompt=create_prompt(query,data)
    # else:
    #     prompt=create_prompt2(query,data)
    response=generate(
        prompt=prompt,
        temperature=0.7,
        top_p=0.7,
        max_tokens=3000
        )
    if response is None:
        logger.error("LLM Generation Failed or returned None")
        return "Sorry, I encountered an error while generating the response."
    logger.info("Recieved Response form LLM")
    return response


def get_Handle():
    return vector_collection_handle