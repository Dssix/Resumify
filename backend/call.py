""" Before calling this function, make sure that you've already initialized the database 
This function is for preparing the data, seraching using rag_pipline , and returning the response which
is recived from rag_pipline call"""

import re
from backend.RAG.rag_pipeline import get_Handle
from backend.RAG.hybrid_retriever import hybrid_search
from backend.RAG.llm_interface import generate
from uuid import uuid4
import os
import traceback # Add for detailed traceback printing


# Prompt for question generation
def ques_prompt(json,data):
    prompt=f""" You are a seasoned technical interviewer. Your task is to generate a numbered list of 10 interview questions based strictly on the provided Candidate Resume (JSON) and Retrieved Context Data (JSON) below.

Instructions:

Analyze the candidate's technical skills, project experience, education, and certifications from the Resume JSON.

Utilize the Retrieved Context Data carefully:

If the metadata indicates the context is from user's previous data, prioritize making questions personalized to their past projects, experiences, or challenges.

If the metadata indicates the context is from the general dataset, use it as additional inspiration to generate industry-relevant or technically deep questions.

DO NOT reference or include any personal details (e.g., name, email, phone number, social media links) in the questions.

Craft questions that are:

Clear, direct, and job-relevant.

A mix of technical, behavioral, and project-specific queries.

Encouraging the candidate to explain their work, problem-solving strategies, and technical decision-making.

Replace any placeholder text with specific details from the Resume JSON and Retrieved Context Data. Do not leave generic placeholders such as "[specific certification from JSON]" or "[insert project name]".

Ensure the set of questions covers:

Deep dives into projects

Application of technical skills

Problem-solving approaches

Decision-making rationale

Behavioral attributes (teamwork, leadership, adaptability)

Format your output as a numbered list of questions, with no extra commentary.

Candidate Resume (JSON): {json}

Retrieved Context Data (JSON with Metadata): {data}

Example Output:

Can you explain the technical challenges you encountered during the Web Vulnerability Scanner project and how you addressed them?

How did your experience with the Phone Price Prediction project influence your understanding of machine learning techniques?

Which programming language listed in your skills do you prefer for developing scalable applications, and why?

What methodologies did you employ in your projects to ensure effective debugging and testing?

How has your education prepared you for tackling complex technical problems in real-world scenarios? ... """
    return prompt


# Prompt for report generation
def rep_prompt(data):
    prompt = f"""You are a seasoned technical interviewer tasked with evaluating a candidate's performance based on their responses during an interview. The candidate's responses are provided in a JSON variable named "data" that includes key-value pairs for "Question 1", "Answer 1", "Question 2", "Answer 2", … through "Question 10" and "Answer 10".

    Instructions:
    1. Analyze each question and its corresponding answer thoroughly.
    2. Provide an overall review of the candidate's performance, focusing on clarity, technical depth, and communication effectiveness.
    3. Assign an overall score to the candidate's performance on a scale from 1 to 10.
    4. For each question, offer specific and constructive feedback, outlining what the candidate did well and what could have been improved. Suggest alternative approaches or answers where applicable. Also, provide a score for each response.
    5. Ensure that your report is clear, structured, and professional.
    6. Format your output as a numbered list with the following structure:

    Overall Review:
    Feedback for each question:
        Question 1:
                Answer: [Candidate's Answer]
                Evaluation: [Detailed evaluation of the answer]
                Area of Improvement: [Suggestions for better response]
                Score: [Score for Question 1]
        Question 2:
                Answer: [Candidate's Answer]
                Evaluation: [Detailed evaluation of the answer]
                Area of Improvement: [Suggestions for better response]
                Score: [Score for Question 2]
        ...
    Overall Score:
    Final Thoughts:

    Candidate Interview Data:
    {data}

    Example Output:
    1. Overall Review: The candidate demonstrated a good understanding of technical concepts and problem-solving skills, though some answers lacked depth in explaining their thought process.
    2. Feedback for each question:
        Question 1:
                Answer: "I hold a degree in Computer Science and have over 5 years of experience in software development..."
                Evaluation: The response provides a clear background but lacks specific examples of technical challenges.
                Area of Improvement: Include more detailed examples of technical challenges and the strategies used to overcome them.
                Score: 7/10
        Question 2:
                Answer: "I am most proficient in Python, JavaScript, and C++..."
                Evaluation: The answer is concise and to the point but could benefit from explaining why the candidate prefers a specific language.
                Area of Improvement: Elaborate on the reasons behind the language preference.
                Score: 8/10
        ...
    3. Overall Score: 7/10
    4. Final Thoughts: The candidate shows a solid technical foundation and effective communication skills; however, deeper insights into problem-solving strategies would enhance their responses.
    """
    return prompt



# Function for extracting projects from the data
def extract_project_titles(projects_text):
    # Find all topics between • and :
    titles = re.findall(r'•(.?)\s:', projects_text)
    # Clean and strip extra spaces
    titles = [title.strip() for title in titles if title.strip()]
    return titles



# Here the parameter 'json' is a JSON formated data of user and 'data' is in dictionary format
# Helper function to extract relevant text snippets from the resume dictionary
def extract_snippets_from_resume(data_dict, search_terms, context_window=150):
    """Extracts text snippets around search terms from resume sections."""
    snippets = []
    # Primarily search within PROJECTS and EXPERIENCE sections if they exist
    searchable_text = ""
    if "PROJECTS" in data_dict and isinstance(data_dict["PROJECTS"], str):
        searchable_text += data_dict["PROJECTS"] + "\n\n"
    if "EXPERIENCE" in data_dict and isinstance(data_dict["EXPERIENCE"], str):
        searchable_text += data_dict["EXPERIENCE"] + "\n\n"
    # Fallback to other string sections if specific ones are not fruitful
    if not searchable_text:
        for section_content in data_dict.values():
            if isinstance(section_content, str):
                searchable_text += section_content + "\n\n"

    if not searchable_text.strip():
        return snippets

    for term in search_terms:
        try:
            # Case-insensitive search for the term
            for match in re.finditer(re.escape(term), searchable_text, re.IGNORECASE):
                start, end = match.span()
                # Define a window around the match
                snippet_start = max(0, start - context_window // 2)
                snippet_end = min(len(searchable_text), end + context_window // 2)
                snippet_text = searchable_text[snippet_start:snippet_end]
                
                # Add ellipsis if the snippet is truncated
                if snippet_start > 0:
                    snippet_text = "..." + snippet_text
                if snippet_end < len(searchable_text):
                    snippet_text = snippet_text + "..."
                
                snippets.append({
                    "document": snippet_text.strip(),
                    "metadata": {"source": "uploaded_resume", "term_matched": term, "id": f"resume_snippet_{uuid4()}"}
                })
                break # Take the first match for simplicity, or collect all
        except Exception as e:
            print(f"Error extracting snippet for term '{term}': {e}")
            continue # Continue with other terms
    return snippets


# This function is for question generation
def generate_question(json_str_param, data_dict_param)->str: # 'json_str_param' is resume_json (string), 'data_dict_param' is resume_text (dictionary)
    try:
        print(f"[backend/call.py generate_question] Received json_str_param type: {type(json_str_param)}, data_dict_param type: {type(data_dict_param)}")
        
        handle=get_Handle()
        general_searched_context=[] # Context from general RAG
        resume_specific_snippets=[] # Context directly from uploaded resume
        query_terms = [] # Terms to search for in both general RAG and resume

        # Extract query terms (project titles and skills) from the resume dictionary
        if "PROJECTS" in data_dict_param and isinstance(data_dict_param["PROJECTS"], str):
            titles = extract_project_titles(data_dict_param["PROJECTS"])
            query_terms.extend(titles)
        
        if "TECHNICAL SKILLS" in data_dict_param and isinstance(data_dict_param["TECHNICAL SKILLS"], str):
            skills = [s.strip() for s in data_dict_param["TECHNICAL SKILLS"].split(',') if s.strip()] # Assuming skills are comma-separated
            # If not comma-separated, might need to adjust splitting logic (e.g., .split() for space separation)
            # For now, let's also try splitting by space if comma split yields few results or common case is space
            if not skills and data_dict_param["TECHNICAL SKILLS"].strip(): # if comma split failed but there's content
                skills = [s.strip() for s in data_dict_param["TECHNICAL SKILLS"].split() if s.strip() and len(s) > 1]
            query_terms.extend(skills)
        
        # Deduplicate query terms
        query_terms = list(set(term for term in query_terms if term and len(term) > 1))
        print(f"[backend/call.py generate_question] Extracted query terms: {query_terms}")

        # 1. Perform hybrid search on the general RAG database using extracted terms
        for term in query_terms:
            general_searched_context.extend(hybrid_search(term, vector_collection=handle))
        print(f"[backend/call.py generate_question] Found {len(general_searched_context)} items from general RAG.")

        # 2. Extract relevant snippets directly from the uploaded resume content
        resume_specific_snippets = extract_snippets_from_resume(data_dict_param, query_terms)
        print(f"[backend/call.py generate_question] Extracted {len(resume_specific_snippets)} snippets from uploaded resume.")

        # Combine both sources of context
        # Prioritize resume-specific snippets by adding them first, or interleave, or let LLM decide based on metadata.
        # For now, let's just combine. The prompt already instructs to prioritize based on metadata.
        combined_context = resume_specific_snippets + general_searched_context
        
        # Limit the number of combined context items to avoid overly long prompts (e.g., top 10-15)
        # This needs a proper ranking/scoring if we combine; RRF in hybrid_search does this for general_searched_context.
        # For now, let's take a slice. A more sophisticated approach would re-rank combined_context.
        MAX_CONTEXT_ITEMS = 15
        if len(combined_context) > MAX_CONTEXT_ITEMS:
            print(f"[backend/call.py generate_question] Truncating combined context from {len(combined_context)} to {MAX_CONTEXT_ITEMS} items.")
            # A simple strategy: take some from resume, some from general. Or sort by a score if available.
            # For now, just slicing. Ideally, we'd have a combined score.
            combined_context = combined_context[:MAX_CONTEXT_ITEMS] 

        print(f"[backend/call.py generate_question] Total combined context items for prompt: {len(combined_context)}")

        prompt_text = ques_prompt(json_str_param, combined_context) 
        response = generate(prompt=prompt_text,
                            temperature=0.7,
                            top_p=0.7,
                            max_tokens=3000
                          )
        return response
    except Exception as e:
        print(f"Error in backend/call.py generate_question: {str(e)}")
        traceback.print_exc() # Print full traceback to console
        raise # Re-raise the exception to be caught by app.py


# This function is for report generation
def generate_report(data):
    response=generate(prompt=rep_prompt(data),
                        temperature=0.7,
                        top_p=0.7,
                        max_tokens=3000
                      )
    filename = str(uuid4()) + ".md"
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'User')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    report_file_path = os.path.join(reports_dir, filename)
    with open(report_file_path, "w") as file:
        file.write(response)
    user_data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'user.txt')
    with open(user_data_file_path, "a") as file:
        file.write(response)
    return response