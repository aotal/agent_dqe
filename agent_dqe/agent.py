from google.adk.agents import Agent
from .agent_tools import mcp_tools

# Instrucción más simple y directa
agent_instruction = """
Eres un asistente experto en DICOM. Tu misión es ayudar a los usuarios a consultar
información de imagenología médica. Para encontrar los estudios de un paciente,
utiliza la herramienta 'query_studies' con el ID del paciente.
"""

root_agent = Agent(
    model="gemini-2.0-flash",
    name="AgenteClienteMCP",
    instruction=agent_instruction,
    # Lista de herramientas reducida y sin ambigüedad
    tools=[
        mcp_tools.query_studies,
        mcp_tools.query_series,
        mcp_tools.query_instances
    ],
)