# AI.py
import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)


jsonModel = """
{
    "name": "string",
    "size": "string",
    "type": "string",
    "alignment": "string",
    "ac": number,
    "armorType": "string",
    "hp": number,
    "hpCalculation": "string",
    "speed": "string",
    "str": number,
    "dex": number,
    "con": number,
    "int": number,
    "wis": number,
    "cha": number,
    "savingThrows": "string",
    "skills": "string",
    "damageImmunities": "string",
    "damageResistances": "string",
    "properties": [
    {
        "name": "string",
        "description": "string"
    }
    ],
    "damageVulnerabilities": "string",
    "conditionImmunities": "string",
    "senses": "string",
    "languages": "string",
    "challengeRating": "number",
    "actions": [
    {
        "name": "string",
        "description": "string"
    },
    {
        "name": "Stomp",
        "description": "string"
    }
    ]
}
"""


def run_job(monster):
    messages = [
        {"role": "user", "content": f"make a monster for dnd, stat block, description, and fighting style for a {monster}.  Skip any extra text stick to just the content, return JSON that looks like {jsonModel}"},
    ]

    response = completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content


def run_jobx(monster):
    # Create a new assistant for each Job Rec, this avoids canidate info bleeding into one another
    my_assistant = client.beta.assistants.create(
        name=f"monster-{monster}",
        instructions="I want you to make a monster for dnd, stat block, description, and fighting style.  Skip any extra text stick to just the content, return JSON",
        model="gpt-3.5-turbo-1106",
        top_p=0.9,
        response_format={"type": "json_object"}

    )

    thread = client.beta.threads.create()

    # Set up the Job Rec
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Scary Cat"
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=my_assistant.id
    )
    if run.status == 'completed':
        monster_content = client.beta.threads.messages.list(
            thread_id=thread.id
        )
    else:
        print(run.status)
        return run.status

    # Set up the canidates
    # print(json.dumps(monster_content, indent=4))
    print(monster_content)
    # print(json.dumps(monster_content, indent=4))

    return f"{monster_content}"
