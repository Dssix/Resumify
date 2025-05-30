# Some basic Imports
from .vector_store import search as search_vectors
from keyword_store import search_keywords
from config import TOP_K_KEYWORD, TOP_K_VECTOR


# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Hybrid Search function, searches for the query and then combine them so that it has only unique data
# Returns List contains all the similar data in form of dictionary
def hybrid_search(
    query: str,
    vector_collection,
    top_k_vector: int = TOP_K_VECTOR,
    top_k_keyword: int = TOP_K_KEYWORD,
    rrf_k: int = 60
) -> list[dict]:
    try:
        vector_results=search_vectors(query,top_k_vector,vector_collection)
        keyword_results=search_keywords(query,top_k_keyword)
        logger.info(f"Fetched {len(vector_results)} vectors and {len(keyword_results)} keywords based on query.")

        # Re-ranking the data for beter structure using Reciprocal Rank Fusion(RRF) method
        rrf_score={}
        result_by_id={}
        # Processing Vector results
        for rank,result in enumerate(vector_results):
            original_id=result.get('metadata',{}).get('id')
            if not original_id:
                logger.warning(f"Skipping vector with missing id: {result}")
                continue
            if original_id not in result_by_id:
                result_by_id[original_id]=result
            score=1.0/(rrf_k+rank+1)
            rrf_score[original_id]=rrf_score.get(original_id,0)+score
        # Processing Keyword results
        for rank,result in enumerate(keyword_results):
            original_id=result.get('id')
            if not original_id:
                logger.warning(f"Skipping keyword with missing id: {result}")
                continue
            if original_id not in result_by_id:
                result_by_id[original_id]=result
            score=1.0/(rrf_k+rank+1)
            rrf_score[original_id]=rrf_score.get(original_id,0)+score
        
        # Sort id's based on their RRF score
        sorted_ids=sorted(rrf_score.keys(),key=lambda doc_id: rrf_score[doc_id], reverse=True)

        final_result=[]
        for doc_id in sorted_ids:
            result_data=result_by_id[doc_id]
            # Storing rrf score as well
            result_data['combined_score']=rrf_score[doc_id]
            final_result.append(result_data)
        
        logger.info(f"Total results found: {len(final_result)}")
        return final_result
    
    except Exception as e:
        logger.exception(f"Exception occured during hybrid search : {e}")
        return []