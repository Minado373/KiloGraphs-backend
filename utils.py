def calculate_calories(profile):
    if not profile.weight or not profile.height or not profile.age:
        return 2000

    if profile.gender == "Male":
        bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161

    activity_map = {
        "0": 1.2,
        "1": 1.55,
        "2": 1.725
    }

    calories = bmr * activity_map.get(profile.activity_level, 1.2)

    if profile.goal == "Weight Loss":
        calories -= 300
    elif profile.goal == "Muscle Gain":
        calories += 300

    return int(calories)


def build_prompt(profile, calories):
    return f"""
Gender: {profile.gender}
Age: {profile.age}
Weight: {profile.weight}
Height: {profile.height}

Goal: {profile.goal}
Activity: {profile.activity_level}
Additional info: {profile.additional_info}

Target calories: {calories} kcal
"""
