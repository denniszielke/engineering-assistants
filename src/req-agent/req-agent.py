import asyncio
import logging
import dotenv
import os
from datetime import datetime

from autogen_core import EVENT_LOGGER_NAME, AgentId, AgentProxy, SingleThreadedAgentRuntime
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentMessage
from autogen_agentchat.teams import SelectorGroupChat
from typing import Sequence
from adapters.github import GithubWrapper

dotenv.load_dotenv()

github = GithubWrapper(
    repo_owner=os.getenv("GITHUB_REPO_OWNER"),
    repo_name=os.getenv("GITHUB_REPO_NAME"),
    access_token=os.getenv("GITHUB_ACCESS")
)

# Create the token provider
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
    model=os.getenv("AZURE_OPENAI_COMPLETION_MODEL"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_ad_token_provider=token_provider,  # Optional if you choose key-based authentication.
    # api_key="sk-...", # For key-based authentication.
)

planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    model_client=az_model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
        Engineering Agent: An advanced test case generator agent who is an expert in describing high quality software engineering requirements and test cases.
        Reviewer Agent: Reviews test cases, assess the formal quality of the test cases and provides concrete feedback to improve the quality.

    You only plan and delegate tasks - you do not execute them yourself.

    When assigning tasks, use this format:
    1. <agent> : <task>

    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)

async def get_requirements(workitem_id: int) -> str:
    issue = await github.get_issue(workitem_id)
    return f"The requirements for {workitem_id} are about {issue}."

engineering_agent = AssistantAgent(
    "EngineeringAgent",
    description="You are an advanced test case generator agent who is an expert in describing high quality software engineering requirements and test cases.",
    tools=[get_requirements],
    model_client=az_model_client,
    system_message="""
    You are an agent that generates test case description for software engineering projects.
    Your only tool is get_requirements - use it to retrieve the list of requirements for a specific workitem.
    You make only one search call at a time.
    """,
)

async def get_objectives(workitem_id: str) -> str:
    technical_objectives = """
Comprehensive Coverage:
Ensure that test cases cover all possible scenarios for updating the location of an inventory asset, including valid updates, invalid updates, and edge cases such as empty or malformed data.
Validation of Input Data:
Test cases should validate the integrity and format of the new location data, ensuring it meets predefined standards and constraints before allowing an update to proceed.
Audit Logging Verification:
Verify that updates to an asset's location correctly log the user who made the change and the exact timestamp of the update, ensuring accountability and traceability.
API Response Validation:
Test cases should verify that the REST API returns the appropriate success or error responses, including correct HTTP status codes and descriptive messages, for both successful and failed update attempts.
Security and Authentication:
Ensure that only authorized users can perform location updates by testing authentication and access controls, including scenarios for unauthorized access attempts.
Performance and Scalability:
Validate that the feature performs efficiently under expected load conditions, ensuring that location updates do not degrade system performance.
Integration Consistency:
Check that the new feature integrates seamlessly with existing systems and workflows, maintaining data consistency across the application and related modules.
User Experience and Usability:
Ensure that any user interface elements associated with the feature, if applicable, are intuitive and provide clear feedback to the user during the update process.
"""

    return f"The objectives for {workitem_id} are the following: {technical_objectives}."

reviewer_agent = AssistantAgent(
    "DataAnalystAgent",
    description="A reviewer agent for reviewing test cases, judging the quality of the test cases and providing feedback for quality improvement.",
    model_client=az_model_client,
    tools=[get_objectives],
    system_message="""
    You are a a reviewer agent for reviewing test cases, judging the quality of the test cases and providing feedback for quality improvement.
    Given the test cases provided you should use the get_objectives tool to retrieve the list of objectives for a specific workitem and validate the test cases based on the objectives.
    You should rate the quality of the test cases and provide a list of feedback for quality improvement.
    """,
)

async def main():
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    def selector_func(messages: Sequence[AgentMessage]) -> str | None:
        if messages[-1].source != planning_agent.name:
            return planning_agent.name
        return None

    team = SelectorGroupChat(
        [planning_agent, engineering_agent, reviewer_agent],
        model_client=az_model_client,
        termination_condition=termination,
        selector_func=selector_func,
    )

    task = "Create new test cases for feature number 1"

    await Console(team.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())
