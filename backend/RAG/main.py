"""This file is for testing the over all RAG Function"""

# Imports for tasks
from rag_pipeline import initialize_rag,answer_query


# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == "__main__":
    try:
        initialize_rag()
        while True:
            user_input=input("Enter your query(or type 'quit' to exit): ")
            if user_input.lower()=='quit':
                logger.info("Exiting the Conversation")
                break
            try:
                response = answer_query(user_input)
                print(f"\nAssistant: {response}\n")
            except Exception as query_error:
                logger.error(f"Error processing query '{user_input}': {query_error}", exc_info=False) # Log less critical error
                print("\nAssistant: Sorry, I encountered an error processing that query. Please try again.\n")
        
        logger.info("Closing the program")
    except Exception as e:
        logger.critical(f"Failed to create RAG Link. Error:{e}",exc_info=True)
        print("Assistant Unavalible")
        exit(1)