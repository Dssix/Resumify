import sys
sys.path.append('d:\\Projects\\Resumify')
from speech import speak
from input_voice import takecommand

A = []

rep = []


def ask_question(i):
    if not A:
        print("No more questions left.")
        return
    B = {}

    # Get question from the list
    question = A.pop(0)
    print(f"\n[Interviewer] {question}")
    speak(question)

    # Get answer from the user
    answer = takecommand().strip()

    # Store Q&A in the dictionary
    B[f"Question {i}"] = question
    B[f"Answer {i}"] = answer
    rep.extend(B)



def get_answer(ques):
    global A
    A = ques.split("\n\n")
    i=1
    for a in A:
        ask_question(i)
        i=i+1
    return rep





# if __name__ == "__main__":
#     sample_resume = "Test.pdf"
#     generate_questions_from_resume(sample_resume)
    
#     while A:
#         ask_question()
    
    # print(convert_json())