# mcp_wrapper.py (actualizado)

import asyncio
from fastmcp import Client
import json

class MCP_Client_Wrapper:
    """
    Encapsula la lógica para interactuar con el servidor DICOM MCP.
    """
    def __init__(self, server_url="http://127.0.0.1:8000/mcp/"):
        self.server_url = server_url
        self.client = Client(self.server_url)

    async def _call_tool_async(self, tool_name: str, params: dict = None):
        """Método auxiliar asíncrono para llamar a una herramienta."""
        async with self.client as c:
            response = await c.call_tool(tool_name, params or {})
            if response.is_error:
                error_content = response.content[0].text if response.content else "Error desconocido"
                raise ConnectionError(f"Error en la herramienta '{tool_name}': {error_content}")
            return response.data

    async def _read_resource_async(self, uri: str):
        """Método auxiliar asíncrono para leer un recurso."""
        async with self.client as c:
            response = await c.read_resource(uri)
            if not response:
                 raise ConnectionError(f"Error al leer el recurso '{uri}': Sin respuesta.")
            # La respuesta es una lista, devolvemos el texto del primer elemento.
            return response[0].text

    def list_configured_nodes(self) -> dict:
        """Obtiene la lista de nodos DICOM del recurso del servidor."""
        print("Llamando al recurso para listar nodos DICOM...")
        try:
            loop = asyncio.get_event_loop()
            # 'list_dicom_nodes' es un recurso, no una herramienta.
            json_text = loop.run_until_complete(
                self._read_resource_async("resource://dicom_nodes")
            )
            # El resultado es un texto JSON, lo parseamos.
            data = json.loads(json_text)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def qido_query(self, query_level: str, query_params: dict) -> dict:
        """Realiza una consulta QIDO-RS y devuelve los resultados."""
        print(f"Ejecutando QIDO query: level='{query_level}', params={query_params}")
        try:
            # Ejecuta la corutina asíncrona y obtiene el resultado
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(
                self._call_tool_async("qido_web_query", {"query_level": query_level, "query_params": query_params})
            )
            return {"status": "success", "data": results.result}
        except Exception as e:
            return {"status": "error", "message": str(e)}