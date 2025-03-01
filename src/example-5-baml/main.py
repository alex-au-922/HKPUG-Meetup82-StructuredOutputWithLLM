import asyncio
from baml_client.async_client import b
from baml_client.types import WorkExperience, JobNature
import instructor
import openai
from pydantic import BaseModel

resume = """
Alex, Cheuk Ming Au (852) 9270 9638 | alexuau922@gmail.com | https://github.com/alex-au-922 Education___________________________________________________ The Chinese University of Hong Kong (CUHK)                                                  Shatin, Hong Kong SAR ENRICHMENT STREAM IN THEORETICAL PHYSICS (BSc in Physics)                                 Sep 2018 – Jul 2022 • Cumulative GPA: 3.843 / 4.000 MINOR IN COMPUTER SCIENCE Work Experience_____________________________________________ Software Engineer II @ CHAI Research Corp. (Palo Alto US, Hybrid)	   Nov 2024 –Jan 2025 •	Conducted root-cause analysis on common GPU clusters outages / traffic issues. •	Created canary rollout and backup tools on GPU K8s clusters with 3000 QPS (Query Per Second) to assist error-rate analysis and prevent sharp traffic shifts. •	Backend development for LLM (Large Language Models) trainings in AI team. •	Reduced deployment outages and increased deployment speed with Test-Driven Design (TDD) on cluster infrastructure tools and backend, both end-to-end and unit test cases. Technical Analyst (Enterprise Framework & Cloud Computing)   @ OOCL 	   Sep 2024 – Oct 2024 •	Created cluster API server for cluster Day-2 operations task scheduling automation. Cloud Engineer  @ HKET						 	   Feb 2024 – Sep 2024 •	Reduced 500x operational cost by self-developing in-house FinOps backend pipeline for cluster cost computation and resources utilization recommendations in K8s clusters. •	Created custom scalable multi-tenants K8s environment on GCP with Istio Service Mesh and Observability integrations with AWS EKS environments, reducing operation costs. Developer (Data Science Specialist) @ CTGoodJobs (Sub-branch of HKET)   Nov 2022 – Feb 2024 •	Increased about 40% click and apply rate and shortened 5x operational time of job alerts for 600k users by revamping on-premises job matching solution with hybrid vector-full-text-search on OpenSearch and AWS SES. •	Integrated Azure OpenAI for generating interview questions (RAG) for job applicants. •	Setup and maintain multi-tenant Apache Airflow pipeline for synchronizing internal database with Cloud (AWS) database for hybrid cloud usage. Reduced cost on networking and server resources with increased flexibility of scheduled jobs. •	Increased 20% job application rate with lowered cost by revamping a real-time semantic similarity search system (Embedding Search) with CDC (Change Data Capture) data ingestion pipeline on AWS. Reduced update time from 1 hour to near-real-time. •	Created an end-to-end Transformer-based anonymous user action recommendation pipeline on AWS based on interacted job posts with selected job features. 8-fold refresh time reduced for new recommendations and around 30% more click-rate. Qualifications________________________________________________ GCP 	Professional Cloud Developer Professional Cloud Architect 	 Jun 2024 – Jun 2026 May 2024 – May 2026 Associate Cloud Engineer 	Apr 2024 – Apr 2027 AWS 	Data Engineer Associate 	Jul 2024 – Jul 2027 Developer Associate 	May 2024 – May 2027 Solution Architect Associate 	Oct 2023 – Oct 2026 HashiCorp 	Terraform Associate 	Apr 2024 – Apr 2026 Other Experience_____________________________________________ Speaker of PyCon HK 2024, Hong Kong SAR.                                                                        16 Nov 2024 Topic Organizers 	Operate with Confidence -- OpenTelemetry in Python PyCon Hong Kong, OSHK (Open Source Hong Kong) URL 	https://pretalx.com/pyconhk2024/talk/9HHTWK/ Speaker of PyCon HK 2023, Hong Kong SAR.                                                                        11 Nov 2023 Topic Organizers 	As Soft as Ever Changing — Clean Architecture in Python PyCon Hong Kong, OSHK (Open Source Hong Kong) URL 	https://pycon.hk/2023/as-soft-as-ever-changing-clean-architecture-in-python/ Skills_______________________________________________________ Programming 	Proficient in Python, Advanced in Go, SQL, Typescript, Familiar with Rust Technical Skills 	Git, Linux, Container Orchestration, K8s, CI/CD, Observability Technical Tools GitHub Action, Terraform, Istio Mesh, Apache Airflow, PyTorch, Jenkins, KServe, VCluster, ArgoCD, Grafana & Prometheus, Elasticsearch Knowledge 	Data Pipelines, RDBMS / NoSQL Databases, Software Design Pattern, Cloud
"""

async def baml_extract_work_experiences(resume: str) -> list[WorkExperience]:
  response = await b.ExtractResume(resume)
  return response

class WorkExperienceList(BaseModel):
    work_exp: list[WorkExperience]

async def instructor_extract_work_experiences(resume: str) -> list[WorkExperience]:
    client = instructor.from_openai(
      openai.AsyncOpenAI(
          base_url="https://api.fireworks.ai/inference/v1",
          api_key="fw_3ZWCmqo4iwAN2PfLujuBDjwD"
      )
    )
    response, completion = await client.chat.completions.create_with_completion(
        model="accounts/fireworks/models/deepseek-v3",
        response_model=WorkExperienceList,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "Parse the following resume into multiple work experiences. Do not include volunteer work or internships.",
            },
            {
                "role": "user",
                "content": resume
            }
        ],
    )
    print(f"Instructor usage: {completion.usage}")

async def native_openai_extract_work_experiences(resume: str) -> list[WorkExperience]:
    client = openai.AsyncOpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key="fw_3ZWCmqo4iwAN2PfLujuBDjwD"
    )
    response = await client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "Parse the following resume into multiple work experiences. Do not include volunteer work or internships.",
            },
            {
                "role": "user",
                "content": resume
            }
        ],
        tools=[{
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
                      "job_nature": {
                          "type": "string",
                          "enum": [nature.value for nature in JobNature],
                          "description": "The nature of the job."
                      }
                  },
                  "required": ["title", "company", "start_date", "description", "job_nature"]
              }
          }
        }],
        tool_choice="auto"
    )
    print(f"Native usage: {response.usage}")

async def main():
    await asyncio.gather(
        baml_extract_work_experiences(resume),
        instructor_extract_work_experiences(resume),
        native_openai_extract_work_experiences(resume)
    )

if __name__ == "__main__":
    asyncio.run(main())
