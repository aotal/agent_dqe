# agent_dqe/agent_tools.py

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
        self.session_cache: Dict[tuple, Any] = {}
        print("🔧 MCPServerTools inicializado con una caché de sesión.")

    async def list_all_patients(self) -> Dict:
        """
        Busca y devuelve una lista de TODOS los pacientes en la base de datos con su ID y nombre.
        """
        # Llamamos a qido_web_query en el nivel 'patients' sin filtros
        return await self._call_qido_tool(query_level="patients", filters={})

    async def _call_mcp_tool(self, tool_name: str, params: Dict) -> Dict:
        """Generic helper function to call any MCP tool."""
        print(f"ADK Tool: Calling remote tool '{tool_name}' with params: {params}")
        try:
            async with self.client as c:
                response = await c.call_tool(tool_name, params)
                if response.is_error:
                    error_content = response.content[0].text if response.content else "Unknown error"
                    raise ConnectionError(error_content)
                return {"status": "success", "data": response.data}
        except Exception as e:
            return {"status": "error", "message": f"Failed to call tool '{tool_name}': {e}"}

    async def _call_qido_tool(self, query_level: str, filters: Dict) -> Dict:
        """Internal function for calling the qido_web_query tool with caching."""
        filters_tuple = tuple(sorted(filters.items()))
        cache_key = (query_level, filters_tuple)

        if cache_key in self.session_cache:
            print(f"✅ Cache HIT for key: {cache_key}")
            return {"status": "success", "data": self.session_cache[cache_key]}
            
        print(f"⚡️ Cache MISS for key: {cache_key}. Querying server...")
        
        response = await self._call_mcp_tool(
            "qido_web_query", 
            {"query_level": query_level, "query_params": filters}
        )
        
        # Only cache successful responses
        if response.get("status") == "success":
            self.session_cache[cache_key] = response["data"]

        return response

    async def query_studies(self, PatientID: str) -> Dict:
        """
        Searches for and returns a list of studies for a specific patient ID.
        This is the primary tool for finding studies.
        """
        return await self._call_qido_tool(query_level="studies", filters={'PatientID': PatientID})

    async def query_series(self, StudyInstanceUID: str) -> Dict:
        """Searches for all series within a specific study using its StudyInstanceUID."""
        query_level = f"studies/{StudyInstanceUID}/series"
        return await self._call_qido_tool(query_level=query_level, filters={})

    async def query_instances(self, StudyInstanceUID: str, SeriesInstanceUID: str) -> Dict:
        """Searches for all instances within a specific series."""
        query_level = f"studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances"
        return await self._call_qido_tool(query_level=query_level, filters={})

    # --- NEW MTF TOOLS ---
    
    async def calculate_mtf_from_instances(
        self, 
        study_instance_uid: str, 
        series_instance_uid: str, 
        sop_instance_uids: List[str]
    ) -> Dict:
        """
        Calculates the averaged MTF for an explicit list of DICOM instances.
        Use this when you have the specific instance UIDs to analyze.
        """
        params = {
            "study_instance_uid": study_instance_uid,
            "series_instance_uid": series_instance_uid,
            "sop_instance_uids": sop_instance_uids
        }
        return await self._call_mcp_tool("calculate_mtf_from_instances", params)

    async def analyze_mtf_for_series(
        self, 
        study_instance_uid: str, 
        series_instance_uid: str
    ) -> Dict:
        """
        High-level tool that automatically finds all MTF instances in a series and calculates their averaged MTF.
        Use this as the primary tool for analyzing an entire series for MTF.
        """
        params = {
            "study_instance_uid": study_instance_uid,
            "series_instance_uid": series_instance_uid
        }
        return await self._call_mcp_tool("analyze_mtf_for_series", params)


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/sse/")
mcp_tools = MCPServerTools(server_url=MCP_SERVER_URL)