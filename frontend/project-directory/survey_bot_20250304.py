import random
import anthropic
import os
import json
from typing import Dict, List
from datetime import datetime

class SurveyBot:
    def __init__(self, api_key: str):
        # Initialize Anthropic client with API key from config
        self.client = anthropic.Anthropic(
            api_key=api_key
        )

        # Initialize conversation log
        self.conversation_log = []

        # Create timestamp for log filename
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Questions with their available options
        self.questions = {
            'ptid': {
                'text': '''To get started, please enter the patient's randomized ID provided by the study coordinator.''',
                'type': 'short_answer'
            },
            'setup': {
                'text': '''Instructions to set up the screening:

                - Bring this device to the patient.

                - Ensure they are in a quiet and comfortable space.

                - Explain that their provider would like them to complete a health-related social needs questionnaire.

                - Give the device to the patient and them time to complete the screening.

                - Once they are done, please return the device to the study coordinator.
                
                - Click OK to proceed.''',
                'type': 'multiple_choice',
                'options': {
                    '1': 'OK'
                    }
            },
            'consent': {
                'text': '''Hi! I'm TRISHA, an AI-enabled chatbot whose job is to ask some questions from your doctor to help them understand things you may need help with outside of the reason for your visit today. Would you like to participate today?''',
                'type': 'multiple_choice',
                'options': {
                    '1': 'Yes',
                    '2': 'No',
                    '3': 'I need more information.'
                }
            },
            'ptname': {
                'text': '''What name would you like me to use today?''',
                'type': 'short_answer'
            },
            'pronouns': {
                'text': "Which pronouns do you prefer to use?",
                'type': 'short_answer',
                'prompt': "Examples include she/her, he/him, they/them but you can enter any pronouns here. Or, you can skip this question by typing 'Skip'."
            },
            'conv_style': {
                'text': 'Which of the following conversation styles do you prefer?',
                'type': 'multiple_choice',
                'options': {
                    '1': 'Straightforward: I will provide you with the information you requested.',
                    '2': 'Helpful: It can be tough to find information; I will help get you what you need.',
                    '3': 'Easygoing: Sure thing! I would happy to grab that info for you; just bear with me for a moment.'
                }
            },
            'living_situation': {
                'text': "What is your living situation today?:",
                'options': {
                    '1': 'I have a steady place to live.',
                    '2': 'I have a place to live today but I am worried about losing it in the future.',
                    '3': 'I do not have a steady place to live (I am temporarily staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, abandoned building, bus or train station, or in a park.)',
                    '4': 'I prefer not to answer this question.'
                }
            },
            'hh_problems': {
                'text': "Think about the place you live. Do you have problems with any of the following? Choose all that apply:",
                'options': {
                    '1': 'Pests, such as bugs, ants, or mice',
                    '2': 'Mold',
                    '3': 'Lead paint or pipes',
                    '4': 'Lack of heat',
                    '5': 'Oven or stove not working',
                    '6': 'Smoke detectors missing or not working',
                    '7': 'Water leaks',
                    '8': 'None of the above',
                    '9': 'I prefer not to answer this question.'
                }
            },
            'utilities': {
                'text': "In the past 12 months, has the electric, gas, oil, or water company threatened to shut off services in your home?",
                'options': {
                    '1': 'Yes',
                    '2': 'No',
                    '3': 'Already shut off',
                    '4': 'I prefer not to answer this question.'
                }
            },
            'food_worry': {
                'text': "Within the past 12 months, have you worried that your food would run out before you got money to buy more?",
                'options': {
                    '1': 'Often true',
                    '2': 'Sometimes true',
                    '3': 'Never true',
                    '4': 'I prefer not to answer this question.'
                }
            },
            'food_ranout': {
                'text': "Within the past 12 months, did the food you bought just didn't last and you didn't have money to get more?",
                'options': {
                    '1': 'Often true',
                    '2': 'Sometimes true',
                    '3': 'Never true',
                    '4': 'I prefer not to answer this question.'
                }
            },
            'transportation': {
                'text': "In the past 12 months, has lack of reliable transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?",
                'options': {
                    '1': 'Yes',
                    '2': 'No',
                    '3': 'I prefer not to answer this question.'
                }
            },
            'help_job': {
                'text': "Do you want help finding or keeping work or a job?",
                'options': {
                    '1': 'Yes, help finding work',
                    '2': 'Yes, help keeping work',
                    '3': 'I do not need or want help',
                    '4': 'I prefer not to answer this question.'
                }
            },
            'help_school': {
                'text': "Do you want help with school or training? For example, starting or completing a job training or getting a high school diploma, GED, or equivalent?",
                'options': {
                    '1': 'Yes',
                    '2': 'No',
                    '3': 'I prefer not to answer this question.'
                }
            },
            'violence_physical': {
                'text': "Because violence and abuse happens to a lot of people and affects their health, we are asking the following questions.  How often does anyone, including family and friends, physically hurt you?",
                'options': {
                    '1': 'Never',
                    '2': 'Rarely',
                    '3': 'Sometimes',
                    '4': 'Fairly often',
                    '5': 'Frequently',
                    '6': 'I prefer not to answer this question.'
                }
            },
            'violence_insult': {
                'text': "How often does anyone, including family and friends, insult or talk down to you?",
                'options': {
                    '1': 'Never',
                    '2': 'Rarely',
                    '3': 'Sometimes',
                    '4': 'Fairly often',
                    '5': 'Frequently',
                    '6': 'I prefer not to answer this question.'
                }
            },
            'violence_threaten': {
                'text': "How often does anyone, including family and friends, threaten you with harm?",
                'options': {
                    '1': 'Never',
                    '2': 'Rarely',
                    '3': 'Sometimes',
                    '4': 'Fairly often',
                    '5': 'Frequently',
                    '6': 'I prefer not to answer this question.'
                }
            },
            'violence_verbal': {
                'text': "How often does anyone, including family and friends, scream or curse at you?",
                'options': {
                    '1': 'Never',
                    '2': 'Rarely',
                    '3': 'Sometimes',
                    '4': 'Fairly often',
                    '5': 'Frequently',
                    '6': 'I prefer not to answer this question.'
                }
            },
            'summary': {
                'text': '''That was the last question in this survey.
                Would you like to view a summary of your responses?''',
                'options': {
                    '1': 'Yes',
                    '2': 'No'
                }
            }
        }
        
        for key in self.questions:
            if key not in ['ptid','setup','consent','ptname','pronouns'] and 'type' not in self.questions[key]:
                self.questions[key]['type'] = 'multiple_choice'
        
        self.responses = {}
        self.current_question = 'ptid'
        self.conversation_history = []

    def display_question(self):
        """Format and display the current question with numbered options."""
        question = self.questions[self.current_question]
        
        if question.get('type') == 'display_only':
            if self.current_question == 'summary':
                return f"\n{question['text']}\n{self.generate_summary()}\n"
            return f"\n{question['text']}\n"

        display_text = f"\n{question['text']}\n"

        if question['type'] == 'multiple_choice':
            for key, value in question['options'].items():
                display_text += f"{key}) {value}\n"
        else:  # short_answer
            # Check if prompt exists, otherwise use a default prompt
            if 'prompt' in question:
                display_text += f"{question['prompt']}\n"
        
        return display_text

    def is_valid_input(self, user_input: str) -> bool:
        """Check if the user input is valid for the current question."""
        question = self.questions[self.current_question]

        if question['type'] == 'display_only':
            return True
        
        if question['type'] == 'multiple_choice':
            return user_input in question['options']
        else:  # short_answer
            return len(user_input.strip()) > 0

    def get_next_question(self) -> str:
        """Determine the next question based on current state."""
        question_order = ['ptid','setup','consent', 'ptname','pronouns', 'conv_style', 'living_situation', 
                        'hh_problems', 'utilities', 'food_worry', 'food_ranout', 'transportation',
                        'help_job', 'help_school', 'violence_physical', 'violence_insult', 
                        'violence_threaten', 'violence_verbal','summary']
        try:
            current_index = question_order.index(self.current_question)
            if current_index + 1 < len(question_order):
                return question_order[current_index + 1]
            return None
        except ValueError:
            return None

    def generate_anthropic_response(self, question_type: str, user_input: str) -> str:
        """Generate a response using the Anthropic API based on conversation context."""
        # Construct conversation history for context
        context = """You are TRISHA, a healthcare survey chatbot. Your role is to ask questions sensitively and 
        respond with empathy and understanding. Your responses should adhere to the principles of trauma-informed
        care, including safety, trust, collaboration, empowerment, and intersectionality.  Keep responses brief (1 sentence) 
        but warm and supportive.  
        Customize your response based on the responses that theuser has already provided, such as their name, preferred pronouns, and
        response to previous questions. You do not need to include the name provided by the patient in each response.
        Your responses should align with the preferred communication style selected
        by the user. If they choose straightforward then your responses should be short and informative.  If they choose helpful, then
        your responses should be supportive and encouraging, i.e., I'll let your doctor know so that they can help you with this. If they
        choose easygoing, then your responses should use casual yet appropriate language, i.e., thanks, good to know! 
        If the user indicates any concerning situations regarding safety, housing, food security, or abuse, acknowledge their response 
        with care but maintain professional boundaries.  Avoid the following trigger words: abuse, threatening, harm, poverty, violence,
        drugs, alcohol.  Do not ask any questions in your response, such as asking if the user has any 
        questions for you.  The user's responses will be limited to the options presented, so please do not offer them the 
        chance to let you know if they have any questions or issues about the survey. Do not include emotes 
        in your response, such as *smiles warmly*.\n\n"""
        
        # Add previous responses for context
        context += "Previous responses:\n"
        for q, r in self.responses.items():
            if q != self.current_question:
                context += f"Q: {self.questions[q]['text']}\nA: {r}\n"
        
        # Add current question and response
        current_q = self.questions[self.current_question]
        if current_q['type'] == 'multiple_choice':
            response_text = current_q['options'][user_input]
        else:
            response_text = user_input
            
        context += f"\nCurrent question: {current_q['text']}\nUser's answer: {response_text}\n"
        context += "\nPlease generate an empathetic response limited to one sentence:"

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=150,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"Claude API Error: {e}")
            # Return a consistent fallback response
            return "Thank you for your response. Let's continue with the survey."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Thank you for sharing that. Let's continue with the survey."

    
    def log_interaction(self, question: str, user_input: str, bot_response: str):
        """Log the interaction to the conversation log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conversation_log.append({
            'timestamp': timestamp,
            'question': question,
            'user_input': user_input,
            'bot_response': bot_response
        })

    def save_log(self):
        """Save the conversation log to a file."""
        filename = f"survey_log_{self.timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("SURVEY INTERACTION LOG\n")
            f.write("=====================\n\n")
            
            for entry in self.conversation_log:
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Question: {entry['question']}\n")
                f.write(f"User Response: {entry['user_input']}\n")
                f.write(f"Bot Response: {entry['bot_response']}\n")
                f.write("-" * 50 + "\n\n")
                
        return filename

    def process_response(self, user_input: str) -> tuple[str, bool]:
        """Process user response and return appropriate reply."""
        question = self.questions[self.current_question]
        
        # Special handling for display_only questions
        if question.get('type') == 'display_only':
            next_question = self.get_next_question()
            if next_question:
                self.current_question = next_question
                return self.display_question(), False
            return "", True
        
        # For multiple choice questions, handle the case where the input is the value instead of the key
        if question['type'] == 'multiple_choice':
            # Create a reverse mapping from option values to keys
            option_values_to_keys = {value: key for key, value in question['options'].items()}
            
            # If the user input matches a value (like "OK" or "Yes") instead of a key (like "1")
            if user_input in option_values_to_keys:
                # Convert the value to its corresponding key
                user_input = option_values_to_keys[user_input]
        
        # Special handling for summary choice
        if self.current_question == 'summary':
            if user_input == '1':  # User wants to see summary
                summary = self.generate_summary()
                
                return f"Here's a summary of your responses:\n\n{summary}\n\nThank you for completing the survey.", True
            else:  # User doesn't want summary
                # Complete the survey without showing summary
                return "Thank you for completing the survey.", True
        
        # Store the response
        try:
            if question['type'] == 'multiple_choice':
                self.responses[self.current_question] = question['options'][user_input]
            else:
                self.responses[self.current_question] = user_input.strip()
        except KeyError as e:
            print(f"KeyError when processing response: {e}")
            # Default behavior if key is not found
            self.responses[self.current_question] = user_input.strip()
        
        # Handle specific question logic
        if self.current_question == 'consent':
            if user_input == '2':  # Initial No
                return "I understand. Thank you for your time. Have a great day!", True
            elif user_input == '3':  # Need more information
                # Store that we're in the explanation phase
                self.responses['needs_explanation'] = True
                explanation = """I'm here to ask you some questions about your daily life and any challenges you might be facing.

                Your doctor wants to understand if there are things making it harder for you to stay healthy, like trouble
                getting food, housing issues, or feeling unsafe. 

                This helps them connect you with resources and support that might be helpful.

                Would you like to proceed with the questions? (Press 1 for Yes, 2 for No)"""
                # Update the intro question to just Yes/No
                self.questions['consent']['options'] = {
                    '1': 'Yes',
                    '2': 'No'
                }
                return explanation, False
            
        # Add this section to handle the response after explanation
        if 'needs_explanation' in self.responses and self.current_question == 'consent':
            if user_input == '2':  # No after explanation
                return "I understand. Thank you for your time. Have a great day!", True
            elif user_input == '1':  # Yes after explanation
                # Remove the flag since we're proceeding
                self.responses.pop('needs_explanation', None)
                # Store the consent response
                self.responses[self.current_question] = 'Yes'
                # Move to the next question
                next_question = self.get_next_question()
                if next_question:
                    self.current_question = next_question
                    return self.display_question(), False
                else:
                    return "Thank you for completing the survey.", True
        
        # Handle progression to next question
        try:
            bot_response = self.generate_anthropic_response(question['type'], user_input)
        except Exception as e:
            print(f"Error generating response: {e}")
            bot_response = "Thank you for sharing that. Let's continue with the survey."
            
        next_question = self.get_next_question()
        
        if next_question is None:
            return bot_response, True
        else:
            self.current_question = next_question
            return f"{bot_response}\n\n{self.display_question()}", False

    def generate_summary(self) -> str:
        """Generate a summary of the survey responses using Anthropic."""
        context = """You are TRISHA, a healthcare survey chatbot. Generate a brief, caring summary of the user's 
        responses, focusing on any areas where they might need support or resources. The summary should adhere to the 
        principles of trauma-informed care, i.e. safety, trust, collaboration, empowerment, and intersectionality.
        Be professional and respectful. Focus on strengths in the information the patient provided, such as stable housing
        and transportation, as well as areas to seek support, such as help with food or housing.  
        Limit the response to 4 to 5 sentences and format it as a paragraph, not a letter to the patient. 
        If the user responses indicate any concerning situations regarding safety, housing, food security, 
        or abuse, acknowledge their response with care but maintain professional boundaries.  Avoid the following trigger words: abuse, 
        threatening, harm, poverty, violence, drugs, alcohol.  Do not ask any questions in your response, such as asking if the user has any 
        questions for you.  The user's responses will be limited to the options presented, so please do not offer them the 
        chance to let you know if they have any questions or issues about the survey. Do not include emotes 
        in your response, such as *smiles warmly*. When you write the summary, write it as though you are giving it to the patient
        as opposed to writing it about them. For example, 'Thanks for sharing this really important information today. I know how difficult
        it can be to answer sensitive questions like these.  Here is a recap of what we discussed today.  It seems like you have a stable
        place to live and aren't worried about your food situation.  Sometimes transportation can be a problem.  Fortunately, it doesn't 
        sound like you have any issues at home with people treating you poorly. I'll be sure to share this information with your
        provider so that they are aware and can talk to you about any of these things if you would like.'  Here are their responses:\n\n"""
        
        for question, response in self.responses.items():
            if question != 'setup':
                context += f"Q: {self.questions[question]['text']}\nA: {response}\n"
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self.generate_basic_summary()

def load_config():
    """Load API key from config file."""
    config_file = 'config.json'
    
    # Check if config file exists
    if not os.path.exists(config_file):
        # Create config file if it doesn't exist
        print("No config file found. Let's create one!")
        print("Please enter your Anthropic API key (starts with 'sk-ant-'):")
        api_key = input().strip()
        
        if not api_key.startswith('sk-ant-'):
            raise ValueError("Invalid API key format. It should start with 'sk-ant-'")
            
        # Save config
        config = {'anthropic_api_key': api_key}
        with open(config_file, 'w') as f:
            json.dump(config, f)
        print(f"Config saved to {config_file}")
        return api_key
    
    # Load existing config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('anthropic_api_key')
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None

def main():
    try:
        # Load API key from config
        api_key = load_config()
        if not api_key:
            print("Error: Could not load API key from config file.")
            return
            
        bot = SurveyBot(api_key)
        survey_complete = False
        
        print("Survey Bot Initialized...")
        print(bot.display_question())
        
        while not survey_complete:
            # Get user input
            if bot.questions[bot.current_question]['type'] == 'multiple_choice':
                user_input = input("You (enter number): ")
            else:
                user_input = input("You: ")

            # Store current question to see if we are moving from violence_verbal to summary
            current_q = bot.current_question
            
            print("\nTRISHA: ...")
            
            # Process response and get next question
            response, survey_complete = bot.process_response(user_input)
            
            # Clear the ... from the bot while it was thinking
            print("\33[A\033[K", end = "")
            print("\nTRISHA:", response)
                    
            # Log the interaction
            bot.log_interaction(
                bot.questions[bot.current_question]['text'],
                user_input,
                response
            )
            
            # Save log when survey is complete
            if survey_complete:
                log_file = bot.save_log()
                print(f"\nInteraction log saved to: {log_file}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        # Try to save log even if there's an error
        try:
            log_file = bot.save_log()
            print(f"\nPartial interaction log saved to: {log_file}")
        except:
            print("Could not save interaction log.")

if __name__ == "__main__":
    main()