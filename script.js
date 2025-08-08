document.getElementById('queryForm').addEventListener('submit', async (event) => {
    // Prevent the default form submission behavior (page reload)
    event.preventDefault();

    const form = event.target;
    const documentUrl = form.documentInput.value;
    const questionsString = form.questionInput.value;
    const questions = questionsString.split('\n').filter(q => q.trim() !== '');

    const loadingMessage = document.getElementById('loadingMessage');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Clear previous results and show loading message
    resultsContainer.innerHTML = '<h2>Answers</h2>';
    loadingMessage.classList.remove('hidden');

    // Your API endpoint and key
    const API_ENDPOINT = 'http://127.0.0.1:8000/hackrx/run';
    const API_KEY = 'my_super_secret_key_12345'; // <-- Use the key from your .env file

    const payload = {
        documents: documentUrl,
        questions: questions
    };

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(payload)
        });

        // Hide loading message
        loadingMessage.classList.add('hidden');

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API request failed.');
        }

        const data = await response.json();
        
        // Display the answers
        data.answers.forEach((answer) => {
            const p = document.createElement('p');
            p.textContent = answer;
            resultsContainer.appendChild(p);
        });

    } catch (error) {
        // Display error message to the user
        const p = document.createElement('p');
        p.textContent = `Error: ${error.message}`;
        p.style.backgroundColor = '#ffe9e9';
        p.style.borderLeftColor = '#e94e4e';
        resultsContainer.appendChild(p);
        loadingMessage.classList.add('hidden');
    }
});