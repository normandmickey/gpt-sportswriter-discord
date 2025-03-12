from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-search-preview",
    web_search_options={
        "user_location": {
            "type": "approximate",
            "approximate": {
                "country": "US",
                "city": "New York",
                "region": "New York",
            }
        },
    },
    messages=[
        {
            "role": "user",
            "content": "Prediction: Buffalo Sabres VS Detroit Red Wings 2025-03-12",
        }
    ],
)

print(completion.choices[0].message.content)