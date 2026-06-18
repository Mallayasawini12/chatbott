document.addEventListener('DOMContentLoaded', () => {
    // --- STATE VARIABLES ---
    let currentQuestionIndex = 0;
    let answers = {}; // Maps question ID (string) to selected option index (int)

    // --- DOM ELEMENTS ---
    const introCard = document.getElementById('quiz-intro-card');
    const questionsCard = document.getElementById('quiz-questions-card');
    const resultsCard = document.getElementById('quiz-results-card');

    const startQuizBtn = document.getElementById('start-quiz-btn');
    const prevBtn = document.getElementById('quiz-prev-btn');
    const nextBtn = document.getElementById('quiz-next-btn');
    const restartQuizBtn = document.getElementById('restart-quiz-btn');

    const currentQNum = document.getElementById('current-q-num');
    const progressFill = document.getElementById('q-progress-fill');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('question-options');

    const resultsCareerTitle = document.getElementById('results-career-title');
    const resultsChart = document.getElementById('results-bar-chart');
    const viewReportLink = document.getElementById('view-report-link');

    // --- BUTTON EVENT LISTENERS ---
    if (startQuizBtn) startQuizBtn.addEventListener('click', startQuiz);
    if (prevBtn) prevBtn.addEventListener('click', prevQuestion);
    if (nextBtn) nextBtn.addEventListener('click', nextQuestion);
    if (restartQuizBtn) restartQuizBtn.addEventListener('click', restartQuiz);

    // --- FUNCTIONS ---
    function startQuiz() {
        currentQuestionIndex = 0;
        answers = {};
        
        introCard.classList.add('hidden');
        resultsCard.classList.add('hidden');
        questionsCard.classList.remove('hidden');
        
        renderQuestion();
    }

    function renderQuestion() {
        if (!quizQuestionsData || quizQuestionsData.length === 0) {
            questionText.innerText = "Error: Quiz questions data is missing.";
            return;
        }

        const question = quizQuestionsData[currentQuestionIndex];
        const totalQuestions = quizQuestionsData.length;

        // Update Progress UI
        currentQNum.innerText = currentQuestionIndex + 1;
        const progressPercent = ((currentQuestionIndex + 1) / totalQuestions) * 100;
        progressFill.style.width = `${progressPercent}%`;

        // Render Question Text
        questionText.innerText = question.question;

        // Render Options
        optionsContainer.innerHTML = '';
        
        // Check if there is already a saved answer for this question
        const savedAnswerIdx = answers[question.id];
        
        // Disable Next button by default unless an option is already selected
        if (savedAnswerIdx === undefined) {
            nextBtn.disabled = true;
        } else {
            nextBtn.disabled = false;
        }

        question.options.forEach((option, index) => {
            const isSelected = savedAnswerIdx === index;
            const optionCard = document.createElement('div');
            optionCard.className = `option-card ${isSelected ? 'selected' : ''}`;
            
            optionCard.innerHTML = `
                <div class="radio-circle"></div>
                <div class="option-text">${option.text}</div>
            `;
            
            optionCard.addEventListener('click', () => {
                // Remove selected state from other options
                const allCards = optionsContainer.querySelectorAll('.option-card');
                allCards.forEach(card => card.classList.remove('selected'));
                
                // Set selected state on clicked option
                optionCard.classList.add('selected');
                
                // Store response
                answers[question.id] = index;
                
                // Enable Next button
                nextBtn.disabled = false;
            });
            
            optionsContainer.appendChild(optionCard);
        });

        // Update Prev Button disabled state
        prevBtn.disabled = currentQuestionIndex === 0;

        // Update Next Button Text
        if (currentQuestionIndex === totalQuestions - 1) {
            nextBtn.innerHTML = 'Submit Quiz <i class="fa-solid fa-square-check"></i>';
        } else {
            nextBtn.innerHTML = 'Next <i class="fa-solid fa-chevron-right"></i>';
        }
    }

    function prevQuestion() {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            renderQuestion();
        }
    }

    function nextQuestion() {
        const question = quizQuestionsData[currentQuestionIndex];
        
        // Validation check
        if (answers[question.id] === undefined) {
            alert("Please select an option before moving to the next question.");
            return;
        }

        const totalQuestions = quizQuestionsData.length;
        
        if (currentQuestionIndex === totalQuestions - 1) {
            // Last question, submit!
            submitQuiz();
        } else {
            // Go to next question
            currentQuestionIndex++;
            renderQuestion();
        }
    }

    async function submitQuiz() {
        // Show loading state on next button
        nextBtn.disabled = true;
        nextBtn.innerHTML = 'Submitting... <i class="fa-solid fa-spinner animate-spin"></i>';

        try {
            const response = await fetch('/api/quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answers: answers })
            });

            const data = await response.json();

            if (data.status === 'success') {
                showResults(data);
            } else {
                alert(data.message || "An error occurred while evaluating your quiz.");
                renderQuestion(); // Reset buttons
            }
        } catch (error) {
            alert("Network error occurred. Please verify your connection.");
            renderQuestion();
            console.error("Quiz submission error:", error);
        }
    }

    function showResults(data) {
        questionsCard.classList.add('hidden');
        resultsCard.classList.remove('hidden');

        // Set Recommended Career
        resultsCareerTitle.innerText = data.recommended_career;
        
        // Update PDF report download link
        viewReportLink.href = `/report/${data.result_id}`;

        // Populate Score Charts
        resultsChart.innerHTML = '';
        
        // Define maps to friendly titles
        const careerTitles = {
            "software_developer": "Software Developer",
            "data_scientist": "Data Scientist",
            "cybersecurity_analyst": "Cybersecurity Analyst",
            "ai_ml_engineer": "AI / ML Engineer",
            "web_developer": "Web Developer"
        };

        // Determine max score to calculate proper percentages
        const scores = data.scores;
        let maxScore = 1;
        for (const c in scores) {
            if (scores[c] > maxScore) maxScore = scores[c];
        }
        
        // Render horizontal progress bar for each career
        for (const careerKey in scores) {
            const score = scores[careerKey];
            // Normalize score mapping (max out at 100%)
            const percent = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
            const displayTitle = careerTitles[careerKey] || careerKey;

            resultsChart.innerHTML += `
                <div class="chart-bar-item">
                    <div class="chart-bar-labels">
                        <span>${displayTitle}</span>
                        <span>${percent}% Match</span>
                    </div>
                    <div class="chart-bar-outer">
                        <div class="chart-bar-fill" style="width: ${percent}%;"></div>
                    </div>
                </div>
            `;
        }
    }

    function restartQuiz() {
        startQuiz();
    }
});
