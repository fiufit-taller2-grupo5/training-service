import openai

openai.api_key = "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"

chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Tell me a Joke"}])

print(chat_completion.choices[0].message)


