# agent_dqe/agent_tools.py (Versión Jerárquica Correcta)

import os
import json
from typing import Any, Dict, List, Optional
from fastmcp import Client
from fastmcp.client.transports import SSETransport

class MCPServerTools:
    def __init__(self, server_url: str):
        if not server_url:
            raise ValueError("La URL del servidor MCP no puede estar vacía.")
        self.transport = SSETransport(url=server_url)
        self.client = Client(self.transport)

    async def _call_qido_tool(self, query_level: str, filters: Dict) -> Dict:
        """Función auxiliar interna para llamar a la herramienta qido_web_query."""
        tool_name = "qido_web_query"
        params = {"query_level": query_level, "filters": filters}
        print(f"ADK Tool: Llamando a la herramienta remota '{tool_name}' con params: {params}")
        try:
            async with self.client as c:
                response = await c.call_tool(tool_name, params)
                if response.is_error:
                    error_content = response.content[0].text if response.content else "Error desconocido"
                    raise ConnectionError(error_content)
                return {"status": "success", "data": response.data}
        except Exception as e:
            return {"status": "error", "message": f"Fallo al llamar a la herramienta '{tool_name}': {e}"}

    async def list_dicom_nodes(self) -> Dict[str, Any]:
        """Obtiene la lista de nodos DICOM del servidor."""
        print("ADK Tool: Leyendo el recurso 'resource://dicom_nodes'...")
        try:
            async with self.client as c:
                content_parts = await c.read_resource("resource://dicom_nodes")
                if not content_parts or not hasattr(content_parts[0], 'text'):
                    raise ConnectionError("La respuesta del recurso estaba vacía o mal formada.")
                response_data = json.loads(content_parts[0].text)
                return {"status": "success", "data": response_data}
        except Exception as e:
            return {"status": "error", "message": f"Fallo al leer el recurso 'dicom_nodes': {e}"}

    async def query_patients(self, name_pattern: Optional[str] = None, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Busca pacientes en el nodo DICOM activo."""
        tool_name = "query_patients"
        params = {k: v for k, v in {"name_pattern": name_pattern, "patient_id": patient_id}.items() if v is not None}
        print(f"ADK Tool: Llamando a la herramienta remota '{tool_name}' con params: {params}")
        try:
            async with self.client as c:
                response = await c.call_tool(tool_name, params)
                if response.is_error:
                    error_content = response.content[0].text if response.content else "Error desconocido"
                    raise ConnectionError(error_content)
                return {"status": "success", "data": response.data}
        except Exception as e:
            return {"status": "error", "message": f"Fallo al llamar a la herramienta '{tool_name}': {e}"}

    # --- NUEVAS HERRAMIENTAS EXPLÍCITAS Y CORRECTAS ---
    async def query_studies(self, PatientID: Optional[str] = None, **kwargs: Any) -> Dict:
        """Busca estudios. Si se provee PatientID, filtra por ese paciente."""
        filters = kwargs
        if PatientID:
            filters['PatientID'] = PatientID
        return await self._call_qido_tool(query_level="studies", filters=filters)

    async def query_series(self, StudyInstanceUID: str, **kwargs: Any) -> Dict:
        """Busca todas las series de un estudio específico."""
        query_level = f"studies/{StudyInstanceUID}/series"
        return await self._call_qido_tool(query_level=query_level, filters=kwargs)

    async def query_instances(self, StudyInstanceUID: str, SeriesInstanceUID: str, **kwargs: Any) -> Dict:
        """Busca todas las instancias de una serie específica."""
        query_level = f"studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances"
        return await self._call_qido_tool(query_level=query_level, filters=kwargs)

# --- Instancia única para ser importada por el agente ---
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/sse/")
mcp_tools = MCPServerTools(server_url=MCP_SERVER_URL)