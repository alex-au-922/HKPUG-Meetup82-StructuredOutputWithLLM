client<llm> DeepSeek {
  provider "openai-generic"
  retry_policy Exponential
  options {
    api_key env.FIREWORKS_API_KEY 
    model "accounts/fireworks/models/deepseek-v3"
    base_url "https://api.fireworks.ai/inference/v1"
    temperature 0.1
  }
}

retry_policy Exponential {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}

