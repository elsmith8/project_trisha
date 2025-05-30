from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from survey_bot import SurveyBot  # Your existing SurveyBot class
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active survey sessions
survey_sessions = {}

class SurveyResponse(BaseModel):
    response: str

def load_config():
    """Load API key from config file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('anthropic_api_key')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load API key: {str(e)}")

@app.post("/api/survey/start")
async def start_survey():
    """Initialize a new survey session."""
    try:
        api_key = load_config()
        bot = SurveyBot(api_key)
        session_id = len(survey_sessions) + 1
        survey_sessions[session_id] = bot
        
        # Get initial question
        question = bot.questions['intro']
        return {
            "session_id": session_id,
            "question": question['text'],
            "options": question.get('options'),
            "type": question.get('type', 'multiple_choice')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/survey/respond")
async def process_response(response: SurveyResponse):
    """Process a survey response and return the next question."""
    try:
        # For simplicity, using the last session
        # In production, you'd want to track sessions properly
        session_id = len(survey_sessions)
        if session_id not in survey_sessions:
            raise HTTPException(status_code=404, detail="Survey session not found")
            
        bot = survey_sessions[session_id]
        bot_response, survey_complete = bot.process_response(response.response)
        
        # If survey is not complete, get the next question's options
        options = None
        if not survey_complete:
            current_question = bot.questions[bot.current_question]
            if current_question['type'] == 'multiple_choice':
                options = current_question['options']
        
        return {
            "response": bot_response,
            "options": options,
            "surveyComplete": survey_complete
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
