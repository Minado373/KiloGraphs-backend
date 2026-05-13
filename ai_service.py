import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")  # albo 2.5-flash jeśli masz dostęp


SYSTEM_PROMPT = """
You are a professional fitness coach and dietician.

RULES:
- NO markdown, NO explanations, NO conversational filler.
- Output ONLY a valid JSON object.
- DIET COMPLETENESS: You MUST generate exactly 7 days (day_1 to day_7).
- MEAL COMPLETENESS: Each day MUST contain exactly 4 meals: Breakfast, Lunch, Dinner, Snack.
- TRAINING COMPLETENESS: You MUST generate exactly 3 workouts (workout_1, workout_2, workout_3).
- CALORIE PRECISION: The sum of calories from the 4 meals in each day MUST equal the user's target calories EXACTLY (error margin: 30 kcal).
- MATH CHECK: Before outputting, mathematically verify that (Breakfast + Lunch + Dinner + Snack) = Target. Adjust ingredient grams to ensure this.

DIET:
7 days
4 meals per day: Breakfast, Lunch, Dinner, Snack. 
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
