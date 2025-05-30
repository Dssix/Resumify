
from backend.data_processing.Convert_Pdf import text as data_from_pdf
from backend.RAG.rag_pipeline import initialize_rag
from backend.Question_Display import get_answer
from backend.call import generate_question,generate_report


def start(path):
    json,data=data_from_pdf(path)
    initialize_rag(force_reindex=True)
    ques=generate_question(json,data)
    user_answers=get_answer(ques)
    generate_report(user_answers)


if __name__ == "__main__":
    start("Test.pdf")