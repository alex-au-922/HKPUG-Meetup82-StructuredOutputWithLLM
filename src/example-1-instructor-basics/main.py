import os
from fireworks.client import Fireworks
import openai
import instructor
from pydantic import BaseModel
import orjson

class User(BaseModel):
    name: str
    age: int

    def __str__(self):
        return f"{self.name} is {self.age} years old."

def native_fireworks():
    client = openai.OpenAI(
        base_url = "https://api.fireworks.ai/inference/v1",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        messages=[
            {
                "role": "user",
                "content": "Extract Jason is 25 years old",
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "extract_user",
                    "description": "Extracts the name and age of a user from a string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the user."
                            },
                            "age": {
                                "type": "integer",
                                "description": "The age of the user."
                            },
                        },
                        "required": ["name", "age"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )
    tool_choice = chat_completion.choices[0].message.tool_calls[0]
    assert tool_choice.function.name == "extract_user"
    user = User.model_validate(orjson.loads(tool_choice.function.arguments))
    print(user)  # Jason is 25 years old.

def instructor_fireworks():
    client = Fireworks(
        api_key=os.environ.get("FIREWORKS_API_KEY"),
    )

    client = instructor.from_fireworks(client)

    user = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        response_model=User,
        messages=[
            {
                "role": "user",
                "content": "Extract Jason is 25 years old",
            }
        ],
    )

    print(user)  # Jason is 25 years old.

if __name__ == "__main__":
    native_fireworks()
    instructor_fireworks()