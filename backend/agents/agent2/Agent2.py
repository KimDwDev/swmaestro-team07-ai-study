# 태환님 agent
import asyncio

from .job_requirement_agent import run_agent2
from .models import Agent2Request


class Agent2:
    def default(self, targetJob, preferredCompanyType, maxResults):
        request = Agent2Request(
            target_role=targetJob,
            company_type=preferredCompanyType,
            max_results=maxResults,
        )

        result = asyncio.run(run_agent2(request))

        return {
            "companies": [company.name for company in result.companies],
            "required_skills": result.required_skills,
            "preferred_skills": result.preferred_skills,
            "required_experience": result.required_experience,
            "keywords": result.keywords,
        }