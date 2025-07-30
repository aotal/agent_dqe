# agent_dqe/agent.py

from google.adk.agents import Agent
from .agent_tools import mcp_tools

agent_instruction = """
You are an expert DICOM assistant. Your mission is to help users query medical imaging information.

- To find the studies of a patient, use 'query_studies' with the patient's ID.
- To list all series of a study, use 'query_series'.
- To list all instances of a series, use 'query_instances'.
- To analyze the MTF of an entire series automatically, use 'analyze_mtf_for_series'.
- If the user provides a specific list of instances to analyze, use 'calculate_mtf_from_instances
- To list all patients, use 'list all patients''.
"""

root_agent = Agent(
    model="gemini-2.0-flash",
    name="AgenteClienteMCP",
    instruction=agent_instruction,
    tools=[
        mcp_tools.list_all_patients,
        mcp_tools.query_studies,
        mcp_tools.query_series,
        mcp_tools.query_instances,
        mcp_tools.calculate_mtf_from_instances, # <-- New Tool
        mcp_tools.analyze_mtf_for_series,      # <-- New Tool
    ],
)