import os
from enum import StrEnum
from typing import List

import instructor
from fireworks.client import Fireworks
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
    client = instructor.from_fireworks(
        Fireworks(
            api_key=os.environ.get("FIREWORKS_API_KEY")
        )
    )
    
    result = client.chat.completions.create(
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
    

def native_openai_without_enum():
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
                            "enum": list(ProductCategory),
                            "description": "Category of the product"
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": list(Sentiment),
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

def main():
    print("\n=== Using native OpenAI without Enum support ===")
    native_openai_without_enum()

    print("=== Using instructor with Enum support ===")
    instructor_with_enum()
    

if __name__ == "__main__":
    main()