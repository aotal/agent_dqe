# agent_dqe/agent.py (Versión Final y Sincronizada)

from google.adk.agents import Agent
from .agent_tools import mcp_tools

agent_instruction = """
Eres un asistente experto en DICOM. Tu misión es ayudar a los usuarios a consultar
información de imagenología médica usando la jerarquía Paciente -> Estudio -> Serie -> Instancia.
"""

root_agent = Agent(
    model="gemini-2.0-flash",
    name="AgenteClienteMCP",
    instruction=agent_instruction,
    tools=[
        mcp_tools.list_dicom_nodes,
        mcp_tools.query_patients,
        # --- Registramos las nuevas herramientas explícitas ---
        mcp_tools.query_studies,
        mcp_tools.query_series,
        mcp_tools.query_instances
    ],
)