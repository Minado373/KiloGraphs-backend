import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")  # albo 2.5-flash jeśli masz dostęp

SYSTEM_PROMPT = """
You are a professional fitness coach and dietician.

RULES:
- NO markdown
- NO explanations
- STRICT FORMAT ONLY

DIET:
- 7 days
- 4 meals per day: Breakfast, Lunch, Dinner, Snack
- Each meal includes:
  calories, ingredients, macros (P/C/F)

TRAINING:
- 4 gym workouts + 1 optional
- include rest days
- each exercise:
name - sets x reps - weight - difficulty

FORMAT:

=== DIET PLAN ===
Day 1
Breakfast
~500 kcal
Meal name
Ingredient 1
Ingredient 2
Ingredient 3
P: x g C: x g F: x g

(repeat 7 days)

=== TRAINING PLAN ===
Day 1 - Workout
...

Day 2 - Rest
...
"""

def generate_plan(prompt: str):
    response = model.generate_content(SYSTEM_PROMPT + "\n\n" + prompt)

    content = response.text

    if not content or "=== TRAINING PLAN ===" not in content:
        return content or "", "No training plan generated"

    diet = content.split("=== TRAINING PLAN ===")[0]
    training = content.split("=== TRAINING PLAN ===")[1]

    return diet.strip(), training.strip()
