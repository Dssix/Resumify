import re
from rag_pipeline import get_Handle,initialize_rag
from hybrid_retriever import hybrid_search
from Convert_Pdf import text

def extract_project_titles(projects_text):
    # Find all topics between • and :
    titles = re.findall(r'•(.?)\s:', projects_text)
    # Clean and strip extra spaces
    titles = [title.strip() for title in titles if title.strip()]
    return titles




def temp(data):
    handle=get_Handle()
    searched=[]
    for section_name, section_content in data.items():
        if section_name == "PROJECTS" and isinstance(section_content, str):
            titles=extract_project_titles(section_content)
            for title in titles:
                searched.extend(hybrid_search(title,vector_collection=handle))
        elif section_name == "TECHNICAL SKILLS" and isinstance(section_content, str):
             skills = section_content.split()
             for skill in skills:
                 if len(skill) > 1:
                    searched.extend(hybrid_search(skill,vector_collection=handle))
    print("\n\n"+str(searched))



if __name__ == "__main__":
    initialize_rag(True)
    json,data=text("Test.pdf")
    print(str(data))
    temp(data)
