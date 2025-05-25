import os
import openai
import requests
import re
import argparse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=imperial"
    res = requests.get(url).json()
    if res.get('cod') != 200:
        return f"Error: {res.get('message', 'Unable to fetch weather')}"
    return f"The weather in {city} is {res['weather'][0]['description']} with a temperature of {res['main']['temp']}F."

tools = {
    "get_weather": get_weather
}

def ask_agent(user_input):
    prompt = f"""
        You are an AI agent. You have access to the following tool:
        - get_weather(city): returns weather info for the given city.
        When the user asks a question, respond with the tool call like: get_weather("Lagos")

        User input: "{user_input}"

        Tool call:
        """
    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
    )

    tool_call = response['choices'][0]['message']['content'].strip()
    print("Tool Call: {tool_call}")
    match = re.match(r'(\w+)\(".+?)"\)', tool_call)
    print("match: {match}")
    if match:
        func_name, arg = match.groups()
        if func_name in tools:
            return tools[func_name](arg)

    return f"Agent response: {tool_call}"

def main():
    parser = argparse.ArgumentParser(description="AI Weather Agent CLI")
    parser.add_argument("question", help="Ask a weather-related question")
    args = parser.parse_args()
    print(ask_agent(args.question))

if __name__ == "__main__":
    main()
