// GUARANTEED PAUSE APPROACH
// This script completely separates the bot response from the question display
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInputContainer = document.getElementById('user-input-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const optionsContainer = document.getElementById('options-container');
    
    // Global storage for the next question
    let savedQuestionData = null;
    
    // Very long pause (7 seconds) to ensure visibility
    const PAUSE_DURATION = 7000;

    // Start the survey
    startSurvey();

    function startSurvey() {
        fetch('/start_survey', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // For the first question, just display it
            displayQuestion(data.question);
        })
        .catch(error => {
            console.error('Error starting survey:', error);
            addMessageToChat('System', 'Error starting the survey. Please refresh the page.');
        });
    }

    function displayQuestion(question) {
        // Add the question to the chat
        addMessageToChat('Bot', question.text);
        
        // Handle different question types
        if (question.type === 'multiple_choice') {
            // Hide text input and show options
            userInputContainer.style.display = 'none';
            optionsContainer.innerHTML = '';
            optionsContainer.style.display = 'flex';
            
            question.options.forEach(option => {
                const button = document.createElement('button');
                button.classList.add('option-button');
                button.textContent = option;
                button.addEventListener('click', function() {
                    handleUserResponse(option);
                    optionsContainer.style.display = 'none';
                });
                optionsContainer.appendChild(button);
            });
        } else {
            // Show text input and hide options
            userInputContainer.style.display = 'flex';
            optionsContainer.style.display = 'none';
            
            // Add prompt text if available
            if (question.prompt) {
                userInput.placeholder = question.prompt;
            } else {
                userInput.placeholder = 'Type your response here...';
            }
            
            // Focus on the input
            userInput.focus();
        }
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function handleUserResponse(response) {
        // Display user's response
        addMessageToChat('You', response);
        
        // Clear input field
        userInput.value = '';
        
        // Disable all inputs
        disableAllInputs();
        
        // Send to server
        fetch('/process_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: response
            })
        })
        .then(response => response.json())
        .then(data => {
            // CRITICAL: Save the question data for later
            if (!data.survey_complete) {
                savedQuestionData = data.question;
            }
            
            // Only show the bot's response for now
            if (data.bot_response) {
                addMessageToChat('Bot', data.bot_response);
            }
            
            // If survey is complete, handle completion
            if (data.survey_complete) {
                handleSurveyComplete(data);
            } else {
                // GUARANTEED PAUSE APPROACH: Two-step process
                // 1. First, show a clear pause indicator
                showPauseIndicator();
                
                // 2. After the pause, show the question (second half of the process happens in the timeout)
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('System', 'Error processing your response. Please try again.');
            enableAllInputs();
        });
    }
    
    function showPauseIndicator() {
        // Create a very clear pause indicator
        const pauseIndicator = document.createElement('div');
        pauseIndicator.id = 'pause-indicator';
        pauseIndicator.className = 'pause-indicator';
        
        pauseIndicator.innerHTML = `
            <div class="pause-animation">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="pause-text">Next question in 7 seconds...</div>
            <div class="pause-progress"></div>
        `;
        
        // Add to chat
        chatContainer.appendChild(pauseIndicator);
        
        // Scroll to make visible
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Start the progress bar animation
        const progressBar = pauseIndicator.querySelector('.pause-progress');
        progressBar.style.animation = `progress ${PAUSE_DURATION/1000}s linear forwards`;
        
        // Set the timeout to remove the indicator and show the question
        setTimeout(() => {
            // Remove the pause indicator
            if (document.getElementById('pause-indicator')) {
                chatContainer.removeChild(document.getElementById('pause-indicator'));
            }
            
            // Now display the saved question
            if (savedQuestionData) {
                displayQuestion(savedQuestionData);
                savedQuestionData = null; // Clear the saved data
            }
            
            // Re-enable inputs
            enableAllInputs();
        }, PAUSE_DURATION);
    }
    
    function disableAllInputs() {
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Disable all option buttons
        const optionButtons = optionsContainer.querySelectorAll('.option-button');
        optionButtons.forEach(button => {
            button.disabled = true;
        });
    }
    
    function enableAllInputs() {
        userInput.disabled = false;
        sendButton.disabled = false;
        
        // Enable all option buttons
        const optionButtons = optionsContainer.querySelectorAll('.option-button');
        optionButtons.forEach(button => {
            button.disabled = false;
        });
    }

    function handleSurveyComplete(data) {
        // Hide input elements
        userInputContainer.style.display = 'none';
        optionsContainer.style.display = 'none';
        
        // Show completion message
        addMessageToChat('Bot', 'Thank you for completing the survey!');
        
        // Add download link if available
        if (data.log_file) {
            const downloadContainer = document.createElement('div');
            downloadContainer.classList.add('download-container');
            
            const downloadLink = document.createElement('a');
            downloadLink.href = `/download_log/${data.log_file}`;
            downloadLink.textContent = 'Download Conversation Log';
            downloadLink.classList.add('download-button');
            
            downloadContainer.appendChild(downloadLink);
            chatContainer.appendChild(downloadContainer);
        }
        
        // Add return button
        const returnButton = document.createElement('button');
        returnButton.textContent = 'Return to Main Screen';
        returnButton.classList.add('return-button');
        returnButton.addEventListener('click', () => {
            window.location.href = '/';
        });
        
        const returnContainer = document.createElement('div');
        returnContainer.classList.add('return-container');
        returnContainer.appendChild(returnButton);
        chatContainer.appendChild(returnContainer);
        
        // Auto-redirect
        const redirectMessage = document.createElement('div');
        redirectMessage.classList.add('redirect-message');
        redirectMessage.textContent = 'Redirecting to main screen in 5 seconds...';
        chatContainer.appendChild(redirectMessage);
        
        setTimeout(() => {
            window.location.href = '/';
        }, 5000);
    }

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        
        // Use 'bot-message' class for TRISHA, otherwise use sender's name
        if (sender === 'TRISHA') {
            messageElement.classList.add('bot-message');
        } else {
            messageElement.classList.add(sender.toLowerCase() + '-message');
        }
        
        const senderElement = document.createElement('div');
        senderElement.classList.add('message-sender');
        senderElement.textContent = sender;
        
        const contentElement = document.createElement('div');
        contentElement.classList.add('message-content');
        contentElement.textContent = message;
        
        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);
        
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Event listener for the send button
    sendButton.addEventListener('click', function() {
        const response = userInput.value.trim();
        if (response) {
            handleUserResponse(response);
        }
    });

    // Event listener for pressing Enter
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const response = userInput.value.trim();
            if (response) {
                handleUserResponse(response);
            }
        }
    });
});
