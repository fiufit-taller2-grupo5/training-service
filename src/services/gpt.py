import openai

def ask_to_gpt(prompt: str) -> str:
    model = "gpt-3.5-turbo"
    messages = [{
        "role": "user",
        "content": prompt,
    }]
    chat_completion = openai.ChatCompletion.create(model=model, messages=messages)
    return chat_completion.choices[0].message.content