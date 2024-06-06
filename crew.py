from datetime import datetime
from typing import Callable
from langchain_openai import ChatOpenAI
from agents import CompanyResearchAgents
from job_manager import append_event
from tasks import CompanyResearchTasks
from crewai import Crew


class CompanyResearchCrew:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.crew = None
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")

    def setup_crew(self, companies: list[str], positions: list[str]):
        # print(f"Setting up crew for Job ID: {self.job_id}, with companies: {companies} and positions: {positions}")

        agents = CompanyResearchAgents()
        tasks = CompanyResearchTasks(job_id=self.job_id)

        research_manager = agents.research_manager(companies, positions)
        company_research_agent = agents.company_research_agent()

        company_research_tasks = [
            tasks.company_research(company_research_agent, company, positions) for company in companies
        ]

        manage_research_task = tasks.manage_research(
            research_manager, companies, positions, company_research_tasks)

        # Create CREW
        self.crew = Crew(
            agents=[research_manager, company_research_agent],
            tasks=[*company_research_tasks, manage_research_task],
            verbose=2,
        )

    def kickoff(self):
        # kickoff the crew

        if not self.crew:
            # print(f"No crew found for {self.job_id}")
            append_event(self.job_id, "Crew not setup")
            return "Crew not setup"

        append_event(self.job_id, "Task STARTED")

        try:
            # print(f"Running crew for {self.job_id}")
            results = self.crew.kickoff()
            append_event(self.job_id, "Task COMPLETED")
            return results

        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return str(e)
