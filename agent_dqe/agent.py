# agent.py

from google.adk.agents import Agent
# Importa las herramientas que creamos en el paso anterior
from .agent_tools import tool_buscar_estudios_pacs, tool_analizar_mtf_serie, tool_listar_nodos_configurados

# Define el agente raíz.
root_agent = Agent(
    name="AgentePACS",
    model="gemini-2.0-flash",
    description="Un agente experto en interactuar con sistemas de imagen médica (PACS) para buscar estudios y realizar análisis de calidad de imagen como la MTF.",
    instruction="""
    Eres un asistente experto en sistemas PACS. Tu trabajo es ayudar a los usuarios
    a encontrar información y a ejecutar análisis complejos sobre las imágenes médicas.
    Usa tus herramientas para realizar las tareas que se te piden.
    Responde de forma clara y presenta los resultados de manera estructurada.
    """,
    # Aquí es donde le das sus "habilidades"
    tools=[
        tool_listar_nodos_configurados,
        tool_buscar_estudios_pacs,
        tool_analizar_mtf_serie,
    ],
)