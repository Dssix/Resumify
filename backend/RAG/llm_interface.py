# For Open AI api call
from openai import OpenAI,RateLimitError, APIError, OpenAIError
# For api key and other things
from config import OPENAI_API_KEY

# For logging
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# OpenAI response window
try:
    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=OPENAI_API_KEY,
    )
except Exception as e:
    logger.exception(f"Error loading client. ERROR: {e}")
    client=None


# This function generates the response using prompt and kwargs(it contains data like temp, top_p) and return the response
def generate(prompt:str,model:str="openai/gpt-4.1",**kwargs)->str|None:
    if not client:
        logger.error(f"Client Not Avalible. Returning from Generate.")
        return None
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            **kwargs
        )
        if response.choices and len(response.choices)>0:
            text=response.choices[0].message.content.strip()
            logger.info(f"A response is generate to the provided query: {text[:50]}...")
            return text
        else:
            logger.warning("Recived Empty response or no choices from API")
            return None
    except RateLimitError as e:
        logger.error(f"Open AI Rate Limit Exceed: {e}")
        return None
    except APIError as e:
        logger.error(f"Open AI API error generated: {e}")
        return None
    except OpenAIError as e:
        logger.error(f"OpenAI Liberary error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexcepted error occured: {e}",exc_info=True)
        return None