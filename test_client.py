import asyncio
import json
from fastmcp import Client
from fastmcp.client.transports import SSETransport

# --- CONFIGURACIÓN ---
# Asegúrate de que esta URL coincide con la que muestra tu servidor al arrancar
SERVER_URL = "http://127.0.0.1:8000/sse/"
TOOL_NAME = "qido_web_query"

# --- PARÁMETROS DE LA PRUEBA ---
# Aquí puedes modificar los parámetros para probar diferentes consultas
TEST_PARAMS = {
    "query_level": "studies",
    "query_params": {
        "PatientID": "SN201033"
    }
}

async def run_test():
    """
    Se conecta al servidor MCP, llama a una herramienta y muestra el resultado.
    """
    print(f"🔌 Conectando al servidor MCP en: {SERVER_URL}")
    transport = SSETransport(url=SERVER_URL)
    client = Client(transport)

    print(f"🚀 Llamando a la herramienta '{TOOL_NAME}' con los parámetros:")
    print(json.dumps(TEST_PARAMS, indent=2))
    
    try:
        async with client as c:
            response = await c.call_tool(TOOL_NAME, TEST_PARAMS)

            print("\n--- ✅ RESPUESTA DEL SERVIDOR ---")
            if response.is_error:
                print("❌ Error recibido:")
                # response.content es una lista, imprimimos el texto del primer elemento si existe
                if response.content:
                    print(response.content[0].text)
                else:
                    print("Error desconocido sin contenido.")
            else:
                print("✔️ Éxito. Datos recibidos:")
                # response.data contiene el resultado deserializado
                print(json.dumps(response.data, indent=2))

    except Exception as e:
        print(f"\n--- ❌ ERROR DE CONEXIÓN O DEL CLIENTE ---")
        print(f"No se pudo completar la llamada: {e}")

if __name__ == "__main__":
    # Ejecuta el cliente de prueba de forma asíncrona
    asyncio.run(run_test())