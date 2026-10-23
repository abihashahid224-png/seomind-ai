import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

for attempt in range(1, 11):
    try:
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents="Explain what an API is in two sentences.",
        )
        print(response.text)
        break
    except Exception as e:
        print(f"Try {attempt} failed, retrying in 10 sec...")
        time.sleep(10)