""" After the pdf is impoted, text function from this file is called, which will extract all the data form
the pdf and returned in a JSON formated structure """

import fitz
import re
import json


# Function used to extract text from the pdf in the given path
def extract(file_path):
    try:
        file=fitz.open(file_path)
        pages=[page.get_text() for page in file]
        file.close()
        return pages
    except Exception as e:
        print(f"Error opening pdf: {file_path} \nERROR:{e}")
        return []


# Function to detect headings in the text
def detect_headings(text):
    # Regular expression to match lines that start with uppercase letters or are in bold
    heading_pattern = re.compile(r'^[A-Z][A-Za-z\s]*$', re.MULTILINE)
    headings = heading_pattern.findall(text)
    return headings


# Format the document in a structured form which contains title and data corresponding to it
def format(text):
    temp=""
    for word in text:
        temp= temp+word
    text=temp
    headings = detect_headings(text)
    
    # It used find the headings properly while also handling white spaces
    pattern = r"(?=\n\s*(" + "|".join(headings) + r")\s*\n)"

    sections = {}
    # This will split the text according to pattern and ignore text size and if the heading is in multiple lines
    parts = re.split(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    
    if parts:
        # Assume the first part is general information (e.g., name, contact info)
        sections["Personal Details"] = parts[0].strip()
    
    item = sections["Personal Details"]


    # A function to filter the content
    def filter_content(text):
        if item:
            text = text.replace(item, "")
        # Remove email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
        # Remove phone numbers (matches numbers with optional '+' and separators)
        text = re.sub(r'\+?\d[\d\s\-]+', '', text)
        # Remove white spaces
        return re.sub(r'\s+', ' ', text).strip()


    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = filter_content(parts[i + 1].strip())
    
    # Return the dictionary
    return sections


# To prepare for API by converting it to JSON format
def prepare_for_API(structured_Data):
    json_resume = json.dumps(structured_Data, indent=4)
    return json_resume


# just to check this file only
if __name__== "__main__":
    # cleaned_resume=format(extract("Test.pdf"))
    # for section, content in cleaned_resume.items():
    #     print(f"--- {section} ---")
    #     print(content)
    #     print()
    # print(prepare_for_API(format(extract("Test.pdf"))))
    print(format(extract("Test.pdf")))


# The function which is called in other files, used to take file path and then 
def text(file):
    data=format(extract(file))
    return prepare_for_API(data),data