// Defining a data model.
enum JobNature {
  ML_ENGINEER
  SOFTWARE_ENGINEER
  DEVOPS_ENGINEER
  CLOUD_ENGINEER
  OTHER
}

class WorkExperience{
  company_name string
  job_title string
  start_date string @description("ISO 8601 date format")
  end_date string @description("ISO 8601 date format") 
  description string
  job_nature JobNature

  @@stream.done
}

type WorkExperienceList = WorkExperience[]

function ExtractResume(resume: string) -> WorkExperienceList {
  client DeepSeek
  prompt #"
    Parse the following resume into multiple work experiences. Do not include volunteer work or internships.
    {{ resume }}

    {{ ctx.output_format }}
  "# 
}
