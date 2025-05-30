# To extract form pdf
import fitz
# To extract form docx file
from docx import Document
# To remove Special characters and white spaces
import re
# So that logs can be seen
import logging
# OS for file searching
import os

# To Show logs
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


try:
    from config import CHUNK_SIZE,CHUNK_OVERLAP,DATA_DIR
except ImportError:
    # This block should ideally not be hit if config.py is present and sys.path is correct
    CHUNK_SIZE=1000
    CHUNK_OVERLAP=100
    DATA_DIR="data"
    logger.warning("Failed to import from config.py, using default values. Check sys.path and config.py.")


# Function to load text file form path loaction
def _load_txt(file_path: str) -> str:
    try:
        with open(file_path,'r',encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error opening text file: {file_path} \nERROR:{e}")
        return ""

# Function to load pdf from path location
def _load_pdf(file_path: str) -> list[str]:
    try:
        file=fitz.open(file_path)
        pages=[page.get_text() for page in file]
        file.close()
        return pages
    except Exception as e:
        logger.error(f"Error opening pdf: {file_path} \nERROR:{e}")
        return []

#Function to load docx file
def _load_docx(file_path: str) -> str:
    try:
        file=Document(file_path)
        data='\n'.join([para.text for para in file.paragraphs])
        return data
    except Exception as e:
        logger.error(f"Error opening docx: {file_path} \nERROR:{e}")
        return ""

# Function for data cleaning
def _clean_text(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9\s.,?!'-]",' ',text)
    text=re.sub(r'\s+',' ',text)
    text = text.strip()
    return text

# To create chunk of the data and stored in a dictionary for fast access
def _chunk_text(text:str,file_name:str,file_type:str,page_no:int=0) -> list[dict]:
    all_chunk=[]
    start=0
    chunk_index=0
    while(start<len(text)):
        end=start+CHUNK_SIZE
        chunk=_clean_text(text[start:end])
        metadata={
            "id":f"{file_name}::{chunk_index}",
            "type":file_type,
            "page":page_no,
            "chunk_index":chunk_index
        }
        all_chunk.append({"text":chunk,"metadata":metadata})
        chunk_index+=1
        start=end-CHUNK_OVERLAP
    return all_chunk

# Function where the data will be stoed in
# The function will walk the DATA_DIR and extract the files from there and create the chunk for processing
def load_and_chunk_documents() -> list[dict]:
    all_chunks=[]
    for dirpath,dirnames,filenames in os.walk(DATA_DIR):
        for file in filenames:
            file_path=os.path.join(dirpath,file)
            file_ext=os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".txt" or file_ext==".md":
                logger.info(f"Loading TXT file: {file_path}")
                data=_load_txt(file_path)
                chunk=_chunk_text(data,file_path,file_ext)
                all_chunks.extend(chunk)
                logger.info(f"Generated {len(chunk)} chunks from {file_path}")

            elif file_ext == ".pdf":
                logger.info(f"Loading PDF file: {file_path}")
                data=_load_pdf(file_path)
                page_no=1
                for page in data:
                    chunk=_chunk_text(page,file_path,file_ext,page_no)
                    all_chunks.extend(chunk)
                    logger.info(f"Generated {len(chunk)} chunks from {file_path}")
                    page_no+=1
            
            elif file_ext == ".docx":
                logger.info(f"Loading DOCX file: {file_path}")
                data=_load_docx(file_path)
                chunk=_chunk_text(data,file_path,file_ext)
                all_chunks.extend(chunk)
                logger.info(f"Generated {len(chunk)} chunks from {file_path}")

            else:
                logger.warning(f"FILE TYPE NOT SUPPORTED: {file_path}")
    
    return all_chunks