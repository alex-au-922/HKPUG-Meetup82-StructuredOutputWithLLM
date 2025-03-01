from typing import Annotated, Optional, cast

import orjson
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, ORJSONResponse
import instructor
from contextlib import asynccontextmanager
import os
import openai
from pydantic import BaseModel, ConfigDict, Field, PastDate 

@asynccontextmanager
async def lifespan(app: FastAPI):
    native_blocking_fireworks_client = openai.OpenAI(
        base_url = "https://api.fireworks.ai/inference/v1",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
    )
    native_streaming_fireworks_client = openai.OpenAI(
        base_url = "https://api.fireworks.ai/inference/v1",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
    )
    instructor_fireworks_client = openai.AsyncOpenAI(
        base_url = "https://api.fireworks.ai/inference/v1",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
    )
    instructor_fireworks_client = instructor.from_openai(instructor_fireworks_client, mode=instructor.Mode.TOOLS)
    app.state.native_blocking_fireworks_client = native_blocking_fireworks_client
    app.state.native_streaming_fireworks_client = native_streaming_fireworks_client
    app.state.instructor_fireworks_client = instructor_fireworks_client
    yield


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Resume(BaseModel):
    text: str

class WorkExperience(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    title: str
    company: str
    start_date: PastDate = Field(alias="startDate")
    end_date: Optional[PastDate] = Field(alias="endDate")
    description: str

@app.post("/native_blocking", response_model=list[WorkExperience], response_model_by_alias=True)
def native_blocking_parsing(
    request: Request,
    resume: Annotated[Resume, Body()]
):
    native_blocking_fireworks_client: openai.OpenAI = request.app.state.native_blocking_fireworks_client
    response = native_blocking_fireworks_client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        messages=[
            {
                "role": "system",
                "content": "Parse the following resume into multiple work experiences. Do not include volunteer work or internships.",
            },
            {
                "role": "user",
                "content": resume.text,
            }
        ],
        temperature=0.1,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_work_experiences",
                    "description": "Creates work experiences from a resume.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the work experience."
                            },
                            "company": {
                                "type": "string",
                                "description": "The company of the work experience."
                            },
                            "start_date": {
                                "type": "string",
                                "description": "The start date (YYYY-MM-DD) of the work experience."
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date (YYYY-MM-DD) of the work experience."
                            },
                            "description": {
                                "type": "string",
                                "description": "The description of the work experience."
                            },
                        },
                        "required": ["title", "company", "start_date", "description"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )
    all_work_experiences: list[WorkExperience] = []
    for choice in response.choices:
        for tool_choice in choice.message.tool_calls:
            assert tool_choice.function.name == "create_work_experiences"
            work_experiences = WorkExperience.model_validate(orjson.loads(tool_choice.function.arguments))
            all_work_experiences.append(work_experiences)
    return all_work_experiences 

@app.post("/native_streaming", response_class=StreamingResponse)
def native_streaming_parsing(
    request: Request,
    resume: Annotated[Resume, Body()]
):
    native_streaming_fireworks_client: openai.OpenAI = request.app.state.native_streaming_fireworks_client
    response = native_streaming_fireworks_client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        messages=[
            {
                "role": "system",
                "content": "Parse the following resume into multiple work experiences. Do not include volunteer work or internships.",
            },
            {
                "role": "user",
                "content": resume.text,
            }
        ],
        temperature=0.6,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_work_experiences",
                    "description": "Creates work experiences from a resume.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the work experience."
                            },
                            "company": {
                                "type": "string",
                                "description": "The company of the work experience."
                            },
                            "start_date": {
                                "type": "string",
                                "description": "The start date (YYYY-MM-DD) of the work experience."
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date (YYYY-MM-DD) of the work experience."
                            },
                            "description": {
                                "type": "string",
                                "description": "The description of the work experience."
                            },
                        },
                        "required": ["title", "company", "start_date", "description"]
                    }
                }
            }
        ],
        tool_choice="auto",
        stream=True,
    )

    def generate():
        # Stream the response
        buffer = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.tool_calls is not None:
                buffer += delta.tool_calls[0].function.arguments
            try: 
                function_args = orjson.loads(buffer.strip()) # sometimes it will return \n
            except orjson.JSONDecodeError:
                continue
            else:
                buffer = ""
                yield f"data: {WorkExperience.model_validate(function_args).model_dump_json(by_alias=True)}\n\n"
        
    return StreamingResponse(generate(), media_type="text/event-stream")
        

@app.post("/instructor", response_class=StreamingResponse)
async def instructor_streaming_parsing(
    request: Request,
    resume: Annotated[Resume, Body()]
):

    instructor_fireworks_client = cast(instructor.AsyncInstructor, request.app.state.instructor_fireworks_client)
    response = instructor_fireworks_client.chat.completions.create_iterable(
        model="accounts/fireworks/models/deepseek-v3",
        response_model=WorkExperience,
        stream=True,
        temperature=0.1,
        max_retries=10,
        strict=False,
        messages=[
            {
                "role": "system",
                "content": "Parse the following resume into multiple work experiences. Do not include volunteer work or internships.",
            },
            {
                "role": "user",
                "content": resume.text
            }
        ],
    )

    async def generate():
        async for chunk in response:
            yield f"data: {chunk.model_dump_json(by_alias=True)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")