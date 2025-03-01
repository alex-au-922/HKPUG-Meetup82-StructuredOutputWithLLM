import os
from enum import StrEnum
from typing import List

import instructor
import orjson
import openai
from pydantic import BaseModel, Field

review_text = """
I recently purchased the XYZ Wireless Headphones and I'm extremely impressed.
The sound quality is outstanding and the battery lasts for days.
They're comfortable to wear for long periods and the noise cancellation is excellent.
The only minor issue is that the carrying case is a bit bulky.
"""

class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"

class ProductCategory(StrEnum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME = "home"
    BEAUTY = "beauty"
    OTHER = "other"

class ProductReview(BaseModel):
    product_name: str
    category: ProductCategory
    sentiment: Sentiment
    key_points: List[str] = Field(description="Key points mentioned in the review")
 
def instructor_with_enum():
    # use openai.OpenAI instead of Fireworks for fair comparison
    client = instructor.from_openai(
        openai.OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=os.environ.get("FIREWORKS_API_KEY")
        )
    )
    
    result, completion = client.chat.completions.create_with_completion(
        model="accounts/fireworks/models/deepseek-v3",
        response_model=ProductReview,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this product review: {review_text}"
            }
        ]
    )
    
    print(f"Product: {result.product_name}")
    print(f"Category: {result.category}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Key points: {result.key_points}")
    
    if result.sentiment == Sentiment.POSITIVE:
        print("This is a positive review!")
    
    print(f"Input Token usages: {completion.usage.prompt_tokens}")
    print(f"Output Token usages: {completion.usage.completion_tokens}")
    

def native_openai_with_enum():
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=os.environ.get("FIREWORKS_API_KEY")
    )
    
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        temperature=0.1,
        messages=[
            {
                "role": "user", 
                "content": f"Analyze this product review: {review_text}"
            }
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "analyze_review",
                "description": "Analyze a product review",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "Name of the product being reviewed"
                        },
                        "category": {
                            "type": "string",
                            "enum": [cat.value for cat in ProductCategory],
                            "description": "Category of the product"
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": [sent.value for sent in Sentiment],
                            "description": "Overall sentiment of the review"
                        },
                        "key_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key points mentioned in the review"
                        }
                    },
                    "required": ["product_name", "category", "sentiment", "key_points"]
                }
            }
        }],
        tool_choice="auto"
    )
    
    tool_call = response.choices[0].message.tool_calls[0]
    result = orjson.loads(tool_call.function.arguments)
    product_review = ProductReview(**result)

    print(f"Product: {product_review.product_name}")
    print(f"Category: {product_review.category}")
    print(f"Sentiment: {product_review.sentiment}")
    print(f"Key points: {product_review.key_points}")


    if product_review.sentiment == Sentiment.POSITIVE:
        print("This is a positive review!")

    print(f"Input Token usages: {response.usage.prompt_tokens}")
    print(f"Output Token usages: {response.usage.completion_tokens}")

def main():
    print("\n=== Using native OpenAI with Enum support ===")
    native_openai_with_enum()

    print("=== Using instructor with Enum support ===")
    instructor_with_enum()
    

if __name__ == "__main__":
    main()