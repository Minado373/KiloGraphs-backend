import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")  # albo 2.5-flash jeśli masz dostęp


SYSTEM_PROMPT = """
You are a professional fitness coach and dietician.

RULES:
NO markdown
NO explanations
Strict adherence to the provided schema.
Output ONLY a valid JSON object.

DIET:
7 days
4 meals per day: Breakfast, Lunch, Dinner, Snack. Each meal calories should amount to the target calories with a +-100 margin of error.
Each meal includes:
Each meal must include: name, 3 main ingredients WITH amounts, macros (P/C/F), calories, and a preparation instruction.

TRAINING:
3 gym workouts
EACH workout MUST contain EXACTLY 4 exercises.
Each exercise must include: name, difficulty (easy/medium/hard), weight, sets, reps, rest time and a description how to perform it.

FORMAT:

{
  "diet_plan": {
    "day_n": {
      "meal_type": {
        "name": "string",
        "ingredients": ["item1: amount", "item2: amount", "item3: amount"],
        "instructions": "string how to prepare",
        "macros": { "p": 0, "c": 0, "f": 0 },
        "calories": 0
      }
    }
  },
  "training_plan": {
    "workout_n": [
      {
        "exercise_name": "string",
        "difficulty": "string",
        "weight": "string",
        "sets": 0,
        "reps": 0,
        "rest": "string",
        "description": "string"
      }
    ]
  }
}
"""

def generate_plan(prompt: str):
    response = model.generate_content(SYSTEM_PROMPT + "\n\n" + prompt)
    content = response.text.strip()

    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()

    try:
        parsed_data = json.loads(content)
        
        diet_str = json.dumps(parsed_data.get("diet_plan", {}))
        training_str = json.dumps(parsed_data.get("training_plan", {}))
        
        return diet_str, training_str

    except json.JSONDecodeError:
        return "{}", "[]"
