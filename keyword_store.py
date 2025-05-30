import os
import ast

# Whoosh for exact match retrival
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup
from whoosh.analysis import StemmingAnalyzer

# For generating unique code
from uuid import uuid4;

# For testing purpose
from backend.data_processing.data_loader import load_and_chunk_documents

# Config values
from config import INDEX_DIR, TOP_K_KEYWORD

# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

KEYWORD_INDEX_DIR=os.path.join(INDEX_DIR,"keyword_index")

# Defining Schema for indexing
schema=Schema(
    id=ID(unique=True, stored=True),
    text=TEXT(analyzer=StemmingAnalyzer(),stored=True),
    metadata=TEXT(stored=True)
)


# Creating a whoosh index if it dosen't exists, return  index
def create_index():
    if not os.path.exists(KEYWORD_INDEX_DIR):
        os.makedirs(KEYWORD_INDEX_DIR)
    idx=create_in(KEYWORD_INDEX_DIR,schema)
    logger.info(f"Keyword index created in: {KEYWORD_INDEX_DIR}")
    return idx


# Used to open the whoosh index
def open_index():
    if not exists_in(KEYWORD_INDEX_DIR):
        logger.warning("There is no keyword index. Creating new one.")
        return create_index()
    idx=open_dir(KEYWORD_INDEX_DIR)
    logger.info(f"Opened Keyword index: {KEYWORD_INDEX_DIR}")
    return idx


# Function takse chunks and then store them to keyword index
def add_documents(chunks:list[dict]):
    idx=open_index()
    write=idx.writer()
    for chunk in chunks:
        try:
            meta=str(chunk['metadata'])
            write.add_document(
                id=chunk['metadata']['id'],
                text=chunk['text'],
                metadata=meta
            )
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    write.commit()
    logger.info(f"Added {len(chunks)} chunks in keyword index")


# Function used to search index for given query
def search_keywords(query: str, top_k: int=TOP_K_KEYWORD)->list[dict]:
    idx=open_index()
    with idx.searcher() as searcher:
        parser=QueryParser("text", schema=idx.schema, group=OrGroup)
        try:
            parsed_query=parser.parse(query)
            results=searcher.search(parsed_query,limit=top_k)
            results_list=[]
            for result in results:
                metadata_dict={}
                metadata_str=result.get('metadata')
                if metadata_str:
                    try:
                        metadata_dict=ast.literal_eval(metadata_str)
                        if not isinstance(metadata_dict, dict):
                            logger.warning(f"Metadata for id:{result['id']} is not a dict")
                            metadata_dict={'raw_metadata':metadata_str}
                    except (ValueError,SyntaxError,TypeError) as e:
                        logger.exception(f"Not parse metadata string for id:{result['id']}. Error:{e}")
                        metadata_dict={'raw_metadata':metadata_str}
                else:
                    logger.warning(f"Metadata field missing for id:{result['id']}")
                results_list.append({
                    "id":result['id'],
                    "document":result.get('text',''),
                    "metadata":metadata_dict,
                    "score":result.score
                })
            logger.info(f"Query {query} provided {len(results_list)} results")
            return results_list
        except Exception as e:
            logger.error(f"Error occured: {e}")
            return []