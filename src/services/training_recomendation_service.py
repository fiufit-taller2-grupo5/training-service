import openai
import json
import os

class TrainingRecommendationResult:
    def __init__(self, types, min_difficulty, max_difficulty, keywords):
        self.types = types
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty
        self.keywords = keywords

def last_trainings_to_str(trainings):
    s = ""
    for training in trainings:
        s += f"  - Name: {training['title']}, Type: {training['type']}, Difficulty: {training['difficulty']})\n"

    return s

def parse_training_recommendation_result(json_str):
    try:
        data = json.loads(json_str)
        types = data["types"]
        min_difficulty = data["difficulty"]["greaterThan"]
        max_difficulty = data["difficulty"]["lowerThan"]
        keywords = data["keywords"]
        return TrainingRecommendationResult(types, min_difficulty, max_difficulty, keywords)
    except (KeyError, ValueError) as e:
        print("Failed parsing " + json_str + ": " + str(e))
        raise ValueError("Invalid JSON format") from e


def build_prompt(age, weight, height, gender, interests, last_trainings):
    template_gpt_query = """
    Pretend you are JSON Recommender GPT. I provide:

    You are a query in my backend of a fitness app, in a training recomendations system. I will provide you:

    - Some personal and health metrics from some person, such as height, weight, gender
    - Interests of the person. For example: Running, Swimming, Yoga, Weight Lifting
    - name, type and difficulty of the last 10 trainings

    I want you to respond ONLY (with no extra text!) with a json of this type:

    {
        "types": ["Running", "Swimming"],
        "difficulty": {
        "greaterThan": 2
        "lowerThan": 7
        }
        keywords: ["HIIT", "Cardio", "intenso", "naturaleza", "grupal", "equipo", "aeróbico", "desafiante"]
    }

    Where types can be one of:"Running", "Swimming", "Biking", "Yoga", "Basketball", "Football", "Walking", "Gymnastics", "Dancing" or "Hiking" and you should include up to 3 types, difficulty is from 1 to 10, where 10 is the hardest, and add up to 10 keywords for the training name like in the example (in english). Remember, respond only with that json, no text!

    In this case, I will give you this input and YOU SHOULD ONLY RESPOND WITH THAT JSON:
    """
    template_gpt_query += f"\n- weight: {weight}kg"
    template_gpt_query += f"\n- height: {height}cm"
    template_gpt_query += f"\n- age: {age} years old"
    template_gpt_query += f"\n- gender: {gender}"

    template_gpt_query += f"\ninterests: {','.join(interests)}" 
    if len(last_trainings) > 0:
        template_gpt_query += f"\nlast trainings:\n{last_trainings_to_str(last_trainings)}"
    return template_gpt_query


def recommend_trainings(age, weight, height, gender, interests, last_trainings):
    api_key = os.getenv("OPENAI_KEY")
    if api_key is None:
        print("No openai api key found!")
        return None
    
    openai.api_key = api_key
    
    prompt = build_prompt(age, weight, height, gender, interests, last_trainings)
    model = "gpt-3.5-turbo"
    messages = [{
        "role": "user",
        "content": prompt
    }]
    print(prompt)

    chat_completion = openai.ChatCompletion.create(model=model, messages=messages)
    result = chat_completion.choices[0].message.content
    return parse_training_recommendation_result(result)



