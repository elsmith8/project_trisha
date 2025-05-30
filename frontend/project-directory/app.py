from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
import json
from datetime import datetime
from survey_bot_20250304 import SurveyBot, load_config

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key for sessions

# Load the API key
api_key = load_config()
if not api_key:
    raise ValueError("Could not load API key from config file")

@app.route('/')
def index():
    """Render the landing page for the survey."""
    # Clear any existing session
    session.clear()
    return render_template('index.html')

@app.route('/setup')
def setup():
    """Render the setup page interface."""
    # Clear any existing session data
    session.clear()
    return render_template('setup.html')

@app.route('/survey')
def survey():
    """Render the survey chat interface."""
    # Check if setup is completed
    if not session.get('setup_complete'):
        # Redirect to setup if not completed
        return redirect(url_for('setup'))
    return render_template('survey.html')

@app.route('/start_setup', methods=['POST'])
def start_setup():
    """Initialize the setup phase and start with patient ID."""
    # Initialize the survey bot and store in session
    bot = SurveyBot(api_key)
    
    # Store the bot state in session
    session['current_question'] = bot.current_question  # Should be 'ptid'
    session['responses'] = {}
    session['conversation_log'] = []
    session['setup_complete'] = False
    
    # Get the first question (patient ID)
    question_data = {
        'text': bot.questions[bot.current_question]['text'],
        'type': bot.questions[bot.current_question]['type']
    }
    
    if 'prompt' in bot.questions[bot.current_question]:
        question_data['prompt'] = bot.questions[bot.current_question]['prompt']
    
    return jsonify({
        'question': question_data,
        'bot_response': None,
        'setup_complete': False
    })

@app.route('/process_setup_response', methods=['POST'])
def process_setup_response():
    """Process the setup phase responses (patient ID and setup instructions)."""
    # Get the user's response
    user_input = request.json.get('user_input')
    
    # Recreate the bot with the current state
    bot = SurveyBot(api_key)
    bot.current_question = session.get('current_question')
    bot.responses = session.get('responses', {})
    bot.conversation_log = session.get('conversation_log', [])
    
    # Get the current question text for logging
    current_question_text = bot.questions[bot.current_question]['text']
    
    # Handle the response based on current question
    if bot.current_question == 'ptid':
        # Store patient ID
        bot.responses['ptid'] = user_input
        
        # Log the interaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.conversation_log.append({
            'timestamp': timestamp,
            'question': current_question_text,
            'user_input': user_input,
            'bot_response': "Thank you for providing the patient ID, which helps ensure their privacy as we proceed with the survey."
        })
        
        # Move to setup question
        bot.current_question = 'setup'
        
        # Update session
        session['current_question'] = bot.current_question
        session['responses'] = bot.responses
        session['conversation_log'] = bot.conversation_log
        
        # Return the setup question
        setup_question = {
            'text': bot.questions['setup']['text'],
            'type': bot.questions['setup']['type'],
            'options': bot.questions['setup']['options']
        }
        
        return jsonify({
            'bot_response': "Thank you for providing the patient ID, which helps ensure their privacy as we proceed with the survey.",
            'setup_complete': False,
            'question': setup_question
        })
    
    elif bot.current_question == 'setup':
        # Store setup acknowledgment
        bot.responses['setup'] = 'OK'
        
        # Log the interaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.conversation_log.append({
            'timestamp': timestamp,
            'question': current_question_text,
            'user_input': user_input,
            'bot_response': "Thank you. Proceeding to the main questionnaire."
        })
        
        # Mark setup as complete and move to consent question for the main survey
        bot.current_question = 'consent'
        
        # Update session
        session['current_question'] = bot.current_question
        session['responses'] = bot.responses
        session['conversation_log'] = bot.conversation_log
        session['setup_complete'] = True
        
        return jsonify({
            'bot_response': "Thank you. Proceeding to the main questionnaire.",
            'setup_complete': True
        })
    
    # Shouldn't get here
    return jsonify({
        'error': 'Invalid setup state',
        'setup_complete': False
    })

@app.route('/start_survey', methods=['POST'])
def start_survey():
    """Start the main survey (after setup is complete)."""
    # Check if setup is completed
    if not session.get('setup_complete'):
        return jsonify({
            'error': 'Setup not completed',
            'redirect': url_for('setup')
        }), 400
    
    # Recreate the bot with the current state
    bot = SurveyBot(api_key)
    bot.current_question = session.get('current_question')  # Should be 'consent'
    bot.responses = session.get('responses', {})
    bot.conversation_log = session.get('conversation_log', [])
    
    # Get the consent question
    question_data = {
        'text': bot.questions[bot.current_question]['text'],
        'type': bot.questions[bot.current_question]['type']
    }
    
    if bot.questions[bot.current_question]['type'] == 'multiple_choice':
        question_data['options'] = bot.questions[bot.current_question]['options']
    elif 'prompt' in bot.questions[bot.current_question]:
        question_data['prompt'] = bot.questions[bot.current_question]['prompt']
    
    return jsonify({
        'question': question_data,
        'bot_response': None,
        'survey_complete': False
    })

@app.route('/process_response', methods=['POST'])
def process_response():
    """Process the user's response in the main survey."""
    # Get the user's response
    user_input = request.json.get('user_input')
    
    # Recreate the bot with the current state
    bot = SurveyBot(api_key)
    bot.current_question = session.get('current_question')
    bot.responses = session.get('responses', {})
    bot.conversation_log = session.get('conversation_log', [])
    
    # Get the current question text for logging
    current_question_text = bot.questions[bot.current_question]['text']
    
    # Process the response
    response, survey_complete = bot.process_response(user_input)
    
    # Log the interaction manually to ensure it's captured
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.conversation_log.append({
        'timestamp': timestamp,
        'question': current_question_text,
        'user_input': user_input,
        'bot_response': response
    })
    
    # Store the bot state back in session
    session['current_question'] = bot.current_question
    session['responses'] = bot.responses
    session['conversation_log'] = bot.conversation_log
    
    # Format the response for the frontend
    if survey_complete:
        # Generate a unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"survey_log_{timestamp}.txt"
        
        # Save the conversation log manually to ensure it's properly written
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write("SURVEY INTERACTION LOG\n")
            f.write("=====================\n\n")
            
            for entry in bot.conversation_log:
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Question: {entry['question']}\n")
                f.write(f"User Response: {entry['user_input']}\n")
                f.write(f"Bot Response: {entry['bot_response']}\n")
                f.write("-" * 50 + "\n\n")
        
        print(f"Log saved to {log_filename}")
        
        return jsonify({
            'bot_response': response,
            'survey_complete': True,
            'log_file': log_filename
        })
    else:
        # Extract the next question details
        next_question = {
            'text': bot.questions[bot.current_question]['text'],
            'type': bot.questions[bot.current_question]['type']
        }
        
        if bot.questions[bot.current_question]['type'] == 'multiple_choice':
            next_question['options'] = bot.questions[bot.current_question]['options']
        elif 'prompt' in bot.questions[bot.current_question]:
            next_question['prompt'] = bot.questions[bot.current_question]['prompt']
        
        # This is critical: Extract ONLY the bot's response and not include the next question text
        # The response might contain the next question embedded, so we need to clean it
        
        # First, try splitting by double newline which often separates response from question
        parts = response.split('\n\n')
        if len(parts) > 1:
            # Take only the first part as the response
            bot_response_text = parts[0]
        else:
            # If there's no clear separation, check if the question text appears in the response
            if next_question['text'] in response:
                # Remove the question text and any following text from the response
                bot_response_text = response.split(next_question['text'])[0].strip()
            else:
                # Just use the whole response if we can't identify the question part
                bot_response_text = response
        
        return jsonify({
            'question': next_question,
            'bot_response': bot_response_text,
            'survey_complete': False
        })

@app.route('/download_log/<filename>')
def download_log(filename):
    """Allow downloading of the conversation log."""
    from flask import send_from_directory
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)