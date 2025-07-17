# agent_tools.py

from .mcp_wrapper import MCP_Client_Wrapper

def tool_listar_nodos_configurados() -> dict:
    """
    Usa esta herramienta para obtener una lista de todos los nodos DICOM configurados
    en el servidor y para saber cuál es el nodo activo actualmente.
    Es útil para ver las opciones de conexión disponibles.
    """
    wrapper = MCP_Client_Wrapper()
    return wrapper.list_configured_nodes()

def tool_buscar_estudios_pacs(patient_name: str = "", study_description: str = "") -> dict:
    """
    Usa esta herramienta para buscar estudios de pacientes en el PACS.
    Puedes filtrar por nombre de paciente o por descripción del estudio.
    Devuelve una lista de estudios encontrados con sus detalles.
    """
    wrapper = MCP_Client_Wrapper()
    params = {"PatientName": patient_name, "StudyDescription": study_description}
    # Filtra los parámetros que no están vacíos
    active_params = {k: v for k, v in params.items() if v}
    return wrapper.qido_query(query_level="studies", query_params=active_params)

def tool_analizar_mtf_serie(study_uid: str, series_uid: str) -> dict:
    """
    Usa esta herramienta para ejecutar un análisis completo de la MTF (Función de Transferencia de Modulación)
    para todas las imágenes de una serie específica.
    Necesitas proporcionar el Study UID y el Series UID.
    """
    wrapper = MCP_Client_Wrapper()
    params = {"study_instance_uid": study_uid, "series_instance_uid": series_uid}
    try:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            wrapper._call_tool_async("analyze_mtf_for_series", params)
        )
        return {"status": "success", "data": results.dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}