const loadingOverlay = document.getElementById('loading-overlay');
let questionsFromServer = [];
let resumeJsonData = null;
let resumeTextData = null;

document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const resumeFile = document.getElementById('resume-file').files[0];
    const formData = new FormData();
    formData.append('resume', resumeFile);

    if (resumeFile) {
        loadingOverlay.classList.remove('hidden');
        fetch('/upload_resume', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                console.error('Upload error:', data.error);
            } else {
                console.log('Resume processed:', data);
                resumeJsonData = data.resume_json; // Store for later use
                resumeTextData = data.resume_text; // Store for later use
                // Now fetch questions
                return fetch('/generate_questions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        resume_json: resumeJsonData, 
                        resume_text: resumeTextData 
                    })
                });
            }
        })
        .then(response => response.json())
        .then(questionData => {
            if (questionData.error) {
                alert('Error generating questions: ' + questionData.error);
                console.error('Question generation error:', questionData.error);
            } else if (!questionData.questions) { // Check if questions string is null, undefined, or empty
                alert('Error: No questions were generated. The response from the server was empty or invalid.');
                console.error('Question generation error: questions field is null, undefined, or empty in response', questionData);
            } else {
                // Assuming questions are returned as a single string with numbered list
                // We need to parse this string into an array of questions.
                // Example: "1. Question one.\n2. Question two."
                questionsFromServer = questionData.questions.split(/\n\d+\.\s*/).filter(q => q.trim() !== '');
                if (questionsFromServer.length > 0 && questionsFromServer[0].startsWith('1. ')) {
                    questionsFromServer[0] = questionsFromServer[0].substring(3);
                }
                console.log('Generated questions:', questionsFromServer);
                displayQuestions(questionsFromServer);
                document.getElementById('upload-section').style.display = 'none';
                const interviewSection = document.getElementById('interview-section');
                interviewSection.style.display = 'block';
                interviewSection.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An unexpected error occurred. Please try again.');
        }).finally(() => {
            loadingOverlay.classList.add('hidden');
        });
    }
});


let currentQuestionIndex = 0;
let userAnswers = {};

function displayQuestions(questions) {
    const questionContainer = document.getElementById('question-container');
    const answerInput = document.getElementById('answer-input');
    const nextButton = document.getElementById('next-question');
    const submitAnswersButton = document.getElementById('submit-answers');

    questionContainer.innerHTML = ''; // Clear previous questions
    answerInput.value = '';

    if (currentQuestionIndex < questions.length) {
        const questionText = questions[currentQuestionIndex];
        const questionElement = document.createElement('p');
        questionElement.textContent = questionText;
        questionContainer.appendChild(questionElement);
        speakQuestion(questionText);
        nextButton.style.display = 'inline-block';
        submitAnswersButton.style.display = 'none';
    } else {
        nextButton.style.display = 'none';
        submitAnswersButton.style.display = 'inline-block';
        submitAnswersButton.classList.remove('hidden'); // Ensure button is visible
        questionContainer.textContent = "All questions answered. Click 'Submit Answers' to see your report.";
    }
}

document.getElementById('next-question').addEventListener('click', function() {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel(); // Stop any ongoing speech
    }
    const answerInput = document.getElementById('answer-input');
    const currentQuestionText = questionsFromServer[currentQuestionIndex]; 
    userAnswers[`Question ${currentQuestionIndex + 1}`] = currentQuestionText;
    userAnswers[`Answer ${currentQuestionIndex + 1}`] = answerInput.value;
    currentQuestionIndex++;
    displayQuestions(questionsFromServer); 
});

document.getElementById('submit-answers').addEventListener('click', function() {
    console.log('User answers submitted:', userAnswers);
    // Call backend to generate report
    loadingOverlay.classList.remove('hidden');
    fetch('/generate_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userAnswers) // Send all answers
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error generating report: ' + data.error);
            console.error('Report generation error:', data.error);
        } else {
            const feedbackSection = document.getElementById('feedback-section');
            const interviewSection = document.getElementById('interview-section');

            requestAnimationFrame(() => {
                interviewSection.style.display = 'none';
                feedbackSection.classList.remove('hidden'); // Ensure it's not hidden by class
                feedbackSection.style.display = 'block'; // Make section visible
                displayReport(data.report); // Then set its content
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred while generating the report.');
    }).finally(() => {
        loadingOverlay.classList.add('hidden');
    });
});


function displayReport(reportText) { // reportText is now a string
    const reportContent = document.getElementById('feedback-content');
    // Display the raw Markdown report directly, or parse and format if needed
    // For simplicity, let's display it directly in a preformatted tag
    reportContent.innerHTML = `<pre>${reportText}</pre>`; 
}

document.getElementById('start-over-button').addEventListener('click', function() {
    document.getElementById('feedback-section').style.display = 'none';
    document.getElementById('upload-section').style.display = 'block';
    // Reset states
    questionsFromServer = [];
    resumeJsonData = null;
    resumeTextData = null;
    currentQuestionIndex = 0;
    userAnswers = {};
    document.getElementById('upload-form').reset(); // Reset the file input
    document.getElementById('question-container').innerHTML = '';
    document.getElementById('answer-input').value = '';
    document.getElementById('next-question').style.display = 'inline-block';
    document.getElementById('submit-answers').style.display = 'none';
    document.getElementById('submit-answers').classList.add('hidden');
});

function speakQuestion(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        speechSynthesis.speak(utterance);
    } else {
        console.warn('Speech synthesis not supported in this browser.');
    }
}