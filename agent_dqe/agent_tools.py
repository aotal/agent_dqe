import os
import json
from typing import Any, Dict, Optional
from fastmcp import Client
from fastmcp.client.transports import SSETransport

class MCPServerTools:
    def __init__(self, server_url: str):
        if not server_url:
            raise ValueError("La URL del servidor MCP no puede estar vacía.")
        self.transport = SSETransport(url=server_url)
        self.client = Client(self.transport)
        self.session_cache: Dict[tuple, Any] = {}
        print("🔧 MCPServerTools inicializado con una caché de sesión.")

    async def _call_qido_tool(self, query_level: str, filters: Dict) -> Dict:
        """Función interna unificada para llamar a la herramienta qido_web_query."""
        filters_tuple = tuple(sorted(filters.items()))
        cache_key = (query_level, filters_tuple)

        if cache_key in self.session_cache:
            print(f"✅ Cache HIT para la clave: {cache_key}")
            return {"status": "success", "data": self.session_cache[cache_key]}
            
        print(f"⚡️ Cache MISS para la clave: {cache_key}. Consultando al servidor...")
        
        try:
            async with self.client as c:
                response = await c.call_tool(
                    "qido_web_query", 
                    {"query_level": query_level, "query_params": filters}
                )
                if response.is_error:
                    error_content = response.content[0].text if response.content else "Error desconocido"
                    raise ConnectionError(error_content)
                
                self.session_cache[cache_key] = response.data
                return {"status": "success", "data": response.data}
        except Exception as e:
            return {"status": "error", "message": f"Fallo al llamar a la herramienta 'qido_web_query': {e}"}

    # --- HERRAMIENTAS FINALES Y SIN AMBIGÜEDAD ---

    async def query_studies(self, PatientID: str) -> Dict:
        """
        Busca y devuelve una lista de ESTUDIOS para un ID de paciente (PatientID) específico.
        Esta es la única herramienta para buscar estudios de un paciente.
        """
        return await self._call_qido_tool(query_level="studies", filters={'PatientID': PatientID})

    async def query_series(self, StudyInstanceUID: str) -> Dict:
        """Busca todas las series de un estudio específico usando su StudyInstanceUID."""
        query_level = f"studies/{StudyInstanceUID}/series"
        return await self._call_qido_tool(query_level=query_level, filters={})

    async def query_instances(self, StudyInstanceUID: str, SeriesInstanceUID: str) -> Dict:
        """Busca todas las instancias de una serie específica."""
        query_level = f"studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances"
        return await self._call_qido_tool(query_level=query_level, filters={})

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/sse/")
mcp_tools = MCPServerTools(server_url=MCP_SERVER_URL)