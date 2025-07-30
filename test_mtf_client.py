import asyncio
import json
from fastmcp import Client
from fastmcp.client.transports import SSETransport

# --- CONFIGURACIÓN ---
SERVER_URL = "http://127.0.0.1:8000/sse/"

# --- PARÁMETROS DE LA PRUEBA ---
STUDY_UID = "1.3.46.670589.30.41.0.1.128635483504446.1748856971024.1"
SERIES_UID = "1.3.46.670589.30.41.0.1.128635483504446.1748857021693.1"

async def run_test():
    """
    Se conecta al servidor MCP, llama a la herramienta de análisis y, si tiene éxito,
    llama a la herramienta de trazado para obtener el gráfico MTF.
    """
    print(f"🔌 Conectando al servidor MCP en: {SERVER_URL}")
    transport = SSETransport(url=SERVER_URL)
    client = Client(transport)
    
    try:
        async with client as c:
            # --- PASO 1: Llamar a la herramienta de análisis ---
            print("\n🚀 PASO 1: Llamando a la herramienta 'analyze_mtf_for_series'...")
            analysis_params = {
                "study_instance_uid": STUDY_UID,
                "series_instance_uid": SERIES_UID
            }
            analysis_response = await c.call_tool("analyze_mtf_for_series", analysis_params)

            if analysis_response.is_error or analysis_response.data.get("status") != "success":
                print("❌ Error en el paso de análisis:")
                print(json.dumps(analysis_response.data, indent=2))
                return

            print("✔️ Éxito en el análisis. Datos recibidos.")
            analysis_data = analysis_response.data
            
            # Extraer los datos necesarios para el siguiente paso
            frequencies = analysis_data.get("frequencies")
            mtf_values = analysis_data.get("mtf_values")
            mtf_at_50 = analysis_data.get("mtf_at_50_percent")

            if not all([frequencies, mtf_values, mtf_at_50 is not None]):
                print("❌ Error: La respuesta del análisis no contiene los datos necesarios para graficar.")
                return

            # --- PASO 2: Llamar a la herramienta de trazado con los datos del paso 1 ---
            print("\n🚀 PASO 2: Llamando a la herramienta 'plot_mtf_curve' con los datos del análisis...")
            plot_params = {
                "frequencies": frequencies,
                "mtf_values": mtf_values,
                "mtf_at_50": mtf_at_50
            }
            plot_response = await c.call_tool("plot_mtf_curve", plot_params)

            print("\n--- ✅ RESPUESTA FINAL DEL SERVIDOR ---")
            if plot_response.is_error:
                print("❌ Error en el paso de trazado:")
                print(json.dumps(plot_response.data, indent=2))
            else:
                print("✔️ Éxito. Gráfico HTML recibido:")
                # Imprimimos solo una parte del HTML para no llenar la consola
                html_snippet = plot_response.data.get("plot_html", "")[:300]
                print(html_snippet + "...")

    except Exception as e:
        print(f"\n--- ❌ ERROR DE CONEXIÓN O DEL CLIENTE ---")
        print(f"No se pudo completar la llamada: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())