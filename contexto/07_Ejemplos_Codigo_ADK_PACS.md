# El Cookbook Definitivo de Google ADK: De "Hola, Mundo" a Agentes PACS de Producción

## Introducción

El Agent Development Kit (ADK) de Google es un framework de código abierto, disponible en Python y Java, diseñado para simplificar la creación, evaluación y despliegue de agentes de inteligencia artificial sofisticados. Su filosofía principal es aplicar los principios de la ingeniería de software tradicional al desarrollo de agentes, lo que permite un control de versiones robusto, una alta capacidad de prueba y una mayor flexibilidad en el despliegue.

Este cookbook está diseñado como una guía progresiva. Comenzará con la configuración del entorno y la creación de un agente básico, para luego avanzar a través de recetas cada vez más complejas que exploran el rico ecosistema de herramientas de ADK, la orquestación de sistemas multi-agente, la gestión de la memoria, los patrones avanzados de interacción con sistemas médicos como PACS y, finalmente, la colaboración entre agentes a través del protocolo A2A.

### Conceptos Clave de ADK de un Vistazo

| Componente | Rol en el Framework |
| :--- | :--- |
| **Agent** | La unidad fundamental de lógica. Puede ser un `LlmAgent` impulsado por un modelo de lenguaje para razonar y tomar decisiones, o un `WorkflowAgent` para flujos predefinidos. |
| **Tool** | Una capacidad o función que un agente puede utilizar para interactuar con el mundo exterior, como llamar a una API, ejecutar código o invocar a otro agente. |
| **Runner** | El orquestador que gestiona el flujo de eventos entre el usuario, el agente y sus herramientas. |
| **Session** | Representa una única conversación o interacción continua. Almacena el historial de mensajes y eventos. |
| **State** | Un almacén de datos clave-valor volátil asociado a una sesión. Actúa como la "memoria de trabajo" del agente para la interacción actual. |
| **Memory** | Almacenamiento a largo plazo y entre sesiones. Permite a los agentes recordar información de conversaciones pasadas. |

---
## Parte 1: Su Primer Agente - Los Fundamentos

Esta primera parte se centra en poner en marcha al desarrollador lo más rápido posible.

### Receta 1.1: Preparando su Taller de Trabajo

**Descripción:** Esta receta detalla los pasos esenciales para configurar un entorno de desarrollo local para ADK.

**Código y Pasos:**

#### Crear y Activar un Entorno Virtual (Recomendado)
Un entorno virtual aísla las dependencias de su proyecto.
```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno (macOS/Linux)
source .venv/bin/activate

# Activar el entorno (Windows CMD)
.venv\Scripts\activate.bat
````

#### Instalar el Paquete ADK

```bash
pip install google-adk
```

#### Crear la Estructura del Proyecto

ADK espera una estructura de directorios específica.

```
mi_proyecto/
└── mi_primer_agente/
    ├── __init__.py
    ├── agent.py
    └── .env
```

#### Configurar `__init__.py`

Este archivo le dice a Python que el directorio es un paquete.

```python
# mi_primer_agente/__init__.py
from . import agent
```

#### Configurar el Archivo `.env` para las Claves de API

Este archivo almacena de forma segura sus credenciales. Necesitará una clave de API de Google de Google AI Studio.

```ini
# mi_primer_agente/.env
GOOGLE_GENAI_USE_VERTEXAI="False"
GOOGLE_API_KEY="SU_CLAVE_DE_API_DE_GOOGLE_AQUI"
```

### Receta 1.2: El Agente "Hola, Mundo"

**Descripción:** Esta receta presenta el código para el `LlmAgent` más simple posible, cuya única función es responder basándose en su instrucción inicial.

**Código:**

```python
# mi_primer_agente/agent.py
from google.adk.agents import Agent

# Definir el agente raíz.
root_agent = Agent(
    # El nombre del agente, usado para identificación.
    name="agente_hola_mundo",
    # El modelo de lenguaje que impulsará el razonamiento.
    model="gemini-1.5-flash",
    # La instrucción define la personalidad y el objetivo del agente.
    instruction="Eres un asistente amigable y servicial. Responde a las preguntas del usuario de manera concisa y alegre.",
)
```

**Cómo Ejecutarlo:**

ADK viene con una interfaz de usuario web para desarrollo. Para iniciarla, ejecute el siguiente comando desde el directorio raíz de su proyecto:

```bash
adk web
```

Esto abrirá una interfaz en su navegador donde podrá chatear con su `agente_hola_mundo`.

-----

## Parte 2: Diseño y Uso de Herramientas

Las herramientas son lo que dota a los agentes de capacidades funcionales para interactuar con el mundo exterior.

### Receta 2.1: El Agente con Herramientas Básicas

**Descripción:** Este agente utiliza dos herramientas (`get_weather`, `get_current_time`) para responder preguntas sobre el tiempo y la hora.

**Código:**

```python
# mi_agente_herramientas/agent.py
from google.adk.agents import Agent
import datetime
from zoneinfo import ZoneInfo

def get_weather(city: str) -> dict:
    """Recupera el informe meteorológico actual para una ciudad especificada."""
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "El tiempo en Nueva York es soleado con una temperatura de 25°C."
        }
    else:
        return {
            "status": "error",
            "error_message": f"La información del tiempo para '{city}' no está disponible."
        }

def get_current_time(timezone: str) -> dict:
    """Devuelve la hora actual en una zona horaria especificada (ej. 'Europe/Madrid')."""
    try:
        tz = ZoneInfo(timezone)
        current_time = datetime.datetime.now(tz).strftime('%H:%M:%S')
        return {"status": "success", "time": current_time}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-1.5-flash",
    description="Agente para responder preguntas sobre la hora y el tiempo.",
    instruction="Eres un agente útil que puede responder preguntas sobre la hora y el tiempo. Usa tus herramientas para ello.",
    tools=[get_weather, get_current_time],
)
```

### Receta 2.2: Práctica Recomendada - Salidas Estructuradas

**Descripción:** Esta función de herramienta demuestra la práctica recomendada de devolver datos estructurados (un diccionario) con una clave de `status`. Esto mejora la interpretación del LLM y el manejo de errores.

**Código:**

```python
def obtener_informe_meteorologico_robusto(ciudad: str) -> dict:
    """Recupera el informe meteorológico actual para una ciudad específica."""
    try:
        # En un caso real, aquí se llamaría a una API externa.
        if ciudad.lower() == "madrid":
            reporte = {"temperatura": "30°C", "condicion": "Soleado"}
            return {"status": "success", "data": reporte}
        else:
            raise ValueError("Ciudad no encontrada")
    except Exception as e:
        return {"status": "error", "error_message": f"No se pudo obtener el tiempo: {str(e)}"}
```

### Receta 2.3: Herramientas que Acceden al Estado (ToolContext)

**Descripción:** Estos ejemplos ilustran cómo las herramientas pueden leer y escribir datos en el estado de la sesión utilizando el objeto `ToolContext`, permitiendo la comunicación entre herramientas.

**Código:**

```python
# mi_agente_estado/agent.py
from google.adk.tools import ToolContext
import uuid

# Herramienta 1: Obtiene y guarda el perfil de usuario
def obtener_perfil_usuario(tool_context: ToolContext) -> dict:
    """Genera un ID de usuario simulado y lo guarda en el estado temporal."""
    user_id = str(uuid.uuid4())
    # Guarda el ID en el estado para que la siguiente herramienta lo use.
    # El prefijo 'temp:' significa que solo persiste para el turno actual.
    tool_context.state["temp:current_user_id"] = user_id
    return {"status": "success", "message": f"ID de usuario {user_id} generado y guardado."}

# Herramienta 2: Utiliza el ID de usuario del estado
def obtener_pedidos_usuario(tool_context: ToolContext) -> dict:
    """Recupera el ID de usuario del estado y busca sus pedidos."""
    user_id = tool_context.state.get("temp:current_user_id")
    if not user_id:
        return {"status": "error", "error_message": "ID de usuario no encontrado en el estado"}
    
    # Lógica simulada para buscar pedidos usando el user_id
    print(f"Buscando pedidos para el usuario ID: {user_id}")
    return {"status": "success", "data": {"pedidos": ["pedido123", "pedido456"]}}
```

-----

## Parte 3: Despliegue de Agentes en Google Cloud

Esta sección cubre el proceso de llevar un agente desde el desarrollo local a un entorno de producción escalable.

### Receta 3.1: Despliegue en Vertex AI Agent Engine

**Descripción:** Para desplegar un agente en la plataforma gestionada de Google, primero debe envolverse en un `AdkApp` y luego desplegarse usando el SDK de Vertex AI.

**Pasos de Código:**

#### Envolver el Agente en `AdkApp`

```python
from vertexai.preview.reasoning_engines import AdkApp

# Asumiendo que 'root_agent' es tu objeto de agente ADK ya definido
app = AdkApp(agent=root_agent, enable_tracing=True)
```

#### Inicializar el SDK de Vertex AI

```python
import vertexai

vertexai.init(
    project="<TU_PROJECT_ID>", 
    location="<TU_LOCATION>", 
    staging_bucket="gs://<TU_BUCKET_DE_STAGING>"
)
```

#### Desplegar el Agente

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    app, 
    requirements=["google-adk", "pydicom", "pynetdicom", "dicomweb-client"]
)
print(f"Agente desplegado con el nombre de recurso: {remote_app.resource_name}")
```

-----

## Parte 4: Pruebas y Evaluación

Validar el comportamiento de un agente es crucial. ADK se integra con `pytest` para permitir pruebas automatizadas.

### Receta 4.1: Prueba de Pytest para Evaluación de Agentes

**Descripción:** Este ejemplo muestra cómo integrar la evaluación de agentes ADK con `pytest`, permitiendo la ejecución automatizada de pruebas para validar el comportamiento del agente contra un conjunto de datos de evaluación.

**Código:**

```python
# tests/test_agent.py
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

def test_booking_agent_handles_simple_query():
    """
    Evalúa si el agente de reservas maneja correctamente una consulta simple.
    """
    results = AgentEvaluator.evaluate(
        agent_module="booking_agent", # Directorio del agente a probar
        eval_dataset_file_path_or_dir="evals/simple_query.evalset.json",
        config_file_path="evals/test_config.json"
    )
    # Pytest fallará automáticamente si la evaluación no pasa.
    assert results.overall_result.passed
```

-----

## Parte 5: Recetas Avanzadas - Integración con PACS y DICOM

Esta sección proporciona recetas prácticas para interactuar con sistemas de imagen médica.

### Receta 5.1: Abstracción de la Interacción con PACS

**Descripción:** Esta clase base abstracta define una interfaz común para interactuar con un sistema PACS. Esto promueve la modularidad y permite que diferentes implementaciones (DIMSE, DICOMweb) cumplan con los mismos métodos, desacoplando la lógica de la aplicación del protocolo de comunicación subyacente.

**Código:**

```python
from abc import ABC, abstractmethod

class PACS_Agent(ABC):
    """
    Clase base abstracta que define la interfaz para un agente 
    que interactúa con un sistema PACS.
    """
    @abstractmethod
    def buscar_estudios_paciente(self, patient_id: str) -> list:
        """Busca estudios por ID de paciente."""
        pass

    @abstractmethod
    def descargar_imagen_dicom(self, study_uid: str, series_uid: str, instance_uid: str, output_path: str) -> bool:
        """Descarga una única instancia DICOM."""
        pass

    @abstractmethod
    def enviar_estudio_pacs(self, directory_path: str) -> bool:
        """Envía todas las instancias DICOM de un directorio al PACS."""
        pass
```

### Receta 5.2: Agente de Interacción DIMSE (`pynetdicom`)

**Descripción:** Implementación de `PACS_Agent` que utiliza `pynetdicom` para la comunicación DIMSE. Incluye métodos para C-FIND, C-ECHO y C-STORE.

**Código:**

```python
# agentes_pacs/dimse_agent.py
from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, VerificationSOPClass, CTImageStorage
import os
from pydicom import dcmread

class DIMSE_Agent(PACS_Agent):
    def __init__(self, pacs_ip: str, pacs_port: int, pacs_aet: bytes, local_aet: bytes):
        self.pacs_ip = pacs_ip
        self.pacs_port = pacs_port
        self.pacs_aet = pacs_aet
        self.local_aet = local_aet
        # Descomentar para depuración detallada
        # debug_logger()

    def verificar_conexion(self) -> bool:
        """Realiza un C-ECHO (DICOM Ping) para verificar la conectividad."""
        ae = AE(ae_title=self.local_aet)
        ae.add_requested_context(VerificationSOPClass)
        assoc = ae.associate(self.pacs_ip, self.pacs_port, ae_title=self.pacs_aet)
        if assoc.is_established:
            status = assoc.send_c_echo()
            assoc.release()
            return status and status.Status == 0x0000
        return False

    def buscar_estudios_paciente(self, patient_id: str) -> list:
        """Busca estudios por ID de paciente usando C-FIND."""
        ae = AE(ae_title=self.local_aet)
        ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.PatientID = patient_id
        ds.StudyInstanceUID = ''
        
        resultados = []
        assoc = ae.associate(self.pacs_ip, self.pacs_port, ae_title=self.pacs_aet)
        if assoc.is_established:
            try:
                responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
                for (status, identifier) in responses:
                    if status and status.Status in (0xFF00, 0xFF01) and identifier:
                        resultados.append(identifier.StudyInstanceUID)
            finally:
                assoc.release()
        else:
            print(f"Error: No se pudo establecer la asociación DIMSE con {self.pacs_ip}:{self.pacs_port}")
        return resultados

    def enviar_estudio_pacs(self, directory_path: str) -> bool:
        """Envía un estudio al PACS usando C-STORE."""
        ae = AE(ae_title=self.local_aet)
        ae.add_requested_context(CTImageStorage) # Añadir más contextos si es necesario

        assoc = ae.associate(self.pacs_ip, self.pacs_port, ae_title=self.pacs_aet)
        if not assoc.is_established:
            print("Error: No se pudo establecer la asociación para C-STORE.")
            return False
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith(".dcm"):
                    filepath = os.path.join(directory_path, filename)
                    ds = dcmread(filepath)
                    status = assoc.send_c_store(ds)
                    if not status or status.Status != 0x0000:
                        print(f"Fallo al enviar {filename}. Estado: {status}")
                        return False
            return True
        finally:
            assoc.release()
    
    def descargar_imagen_dicom(self, study_uid: str, series_uid: str, instance_uid: str, output_path: str) -> bool:
        print("La descarga con C-MOVE requiere una implementación más compleja y no se incluye en esta receta.")
        return False
```

### Receta 5.3: Agente de Interacción DICOMweb (`dicomweb-client`)

**Descripción:** Implementación de `PACS_Agent` que utiliza `dicomweb-client`. Este enfoque es más moderno, simple y compatible con firewalls.

**Código:**

```python
# agentes_pacs/dicomweb_agent.py
from dicomweb_client.api import DICOMwebClient
from pydicom import dcmread
import os

class DICOMweb_Agent(PACS_Agent):
    def __init__(self, base_url: str, auth_token: str = None):
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self.client = DICOMwebClient(url=base_url, headers=headers)

    def buscar_estudios_paciente(self, patient_id: str) -> list:
        try:
            estudios_json = self.client.search_for_studies(search_filters={'PatientID': patient_id})
            # Extrae el StudyInstanceUID de cada resultado
            return [estudio['0020000D']['Value'][0] for estudio in estudios_json]
        except Exception as e:
            print(f"Error durante la búsqueda DICOMweb (QIDO-RS): {e}")
            return []

    def descargar_imagen_dicom(self, study_uid: str, series_uid: str, instance_uid: str, output_path: str) -> bool:
        try:
            instancia_bytes = self.client.retrieve_instance(
                study_instance_uid=study_uid,
                series_instance_uid=series_uid,
                sop_instance_uid=instance_uid
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(instancia_bytes)
            return True
        except Exception as e:
            print(f"Error durante la descarga DICOMweb (WADO-RS): {e}")
            return False

    def enviar_estudio_pacs(self, directory_path: str) -> bool:
        datasets = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".dcm"):
                filepath = os.path.join(directory_path, filename)
                datasets.append(dcmread(filepath))
        
        if not datasets:
            print("No se encontraron ficheros .dcm en el directorio.")
            return False
        
        try:
            self.client.store_instances(datasets=datasets)
            return True
        except Exception as e:
            print(f"Error durante el envío DICOMweb (STOW-RS): {e}")
            return False
```

### Receta 5.4: Herramienta de Anonimización DICOM

**Descripción:** Una herramienta crítica para la privacidad de los datos. Utiliza `pydicom` para eliminar información de identificación del paciente (PHI) de un archivo DICOM.

**Código:**

```python
from pydicom import dcmread

def anonymize_dicom_header(file_path: str, output_path: str) -> dict:
    """
    Lee un archivo DICOM, elimina los identificadores de paciente y lo guarda.
    Esencial para el cumplimiento de normativas de privacidad como HIPAA.
    """
    try:
        ds = dcmread(file_path)
        
        # Lista de etiquetas a eliminar o anonimizar
        tags_to_anonymize = [
            'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
            'OtherPatientIDs', 'OtherPatientNames', 'PatientAddress',
            'PatientTelephoneNumbers'
        ]
        
        for tag_name in tags_to_anonymize:
            if tag_name in ds:
                if tag_name == 'PatientName':
                    ds.PatientName = "Anonymous^Patient"
                else:
                    # Para otras etiquetas, simplemente las eliminamos
                    delattr(ds, tag_name)

        ds.save_as(output_path)
        return {"status": "success", "message": f"Archivo anonimizado guardado en {output_path}"}
    except Exception as e:
        return {"status": "error", "error_message": f"No se pudo anonimizar el archivo: {str(e)}"}
```

-----

## Parte 6: Arquitecturas Colaborativas - Sistemas Multi-Agente con el Protocolo A2A

Esta sección explora cómo hacer que los agentes ADK colaboren con otros agentes externos, creando ecosistemas de IA interoperables.

### Introducción a la Interoperabilidad con A2A

El panorama actual de la IA se caracteriza por una notable fragmentación. Agentes construidos en diferentes plataformas (LangGraph, CrewAI, ADK) no pueden comunicarse de forma nativa. Para resolver este desafío, Google introdujo el **Protocolo Agent-to-Agent (A2A)**.

**A2A es un estándar de comunicación universal y abierto diseñado para ser el "lenguaje común" que permita a los agentes de IA colaborar de manera fluida y segura, independientemente del framework en el que fueron construidos.**

### Receta 6.1: Entendiendo los Componentes de A2A

**Descripción:** La comunicación en A2A se estructura en torno a un conjunto de objetos de datos bien definidos.

| **Nombre del Objeto** | **Propósito/Descripción** |
| :--- | :--- |
| **AgentCard** | Manifiesto JSON público que sirve como la "tarjeta de visita" de un agente para el descubrimiento dinámico. |
| **Task** | La unidad de trabajo fundamental y con estado. Encapsula una solicitud completa de un agente a otro. |
| **Message** | Representa un único turno de comunicación (una solicitud, una respuesta) dentro del contexto de una `Task`. |
| **Part** | La unidad elemental de contenido dentro de un `Message` o `Artifact`. Es inherentemente multimodal (texto, ficheros, JSON). |
| **Artifact** | El resultado o producto duradero e inmutable de una `Task` completada. |

### Receta 6.2: Haciendo un Agente ADK Compatible con A2A

**Descripción:** Para que un agente ADK sea accesible a través de A2A, se debe añadir una capa de adaptación que traduzca entre el mundo interno de ADK y el mundo externo de A2A.

**Pasos Conceptuales:**

1.  **Definir el Agente ADK Central (`agent.py`)**: Construye tu agente ADK especialista como de costumbre, con su lógica y herramientas. En esta fase, el agente es agnóstico a A2A.
2.  **Establecer una Identidad Pública A2A (`__main__.py`)**: Define la `AgentCard` del agente, que publicita su nombre, URL, habilidades (`AgentSkill`) y requisitos de autenticación.
3.  **Implementar el Puente A2A (`task_manager.py`)**: Este es el componente clave. Se crea una clase `AgentTaskManager` que actúa como un **Adaptador**. Su método `execute` recibe una `Task` de A2A, la traduce a un formato que el `Runner` de ADK entiende, invoca la lógica del agente ADK y luego traduce los resultados de vuelta a los formatos de A2A para responder al cliente.

Este diseño desacoplado es robusto, permitiendo que la lógica de negocio del agente evolucione independientemente de su protocolo de comunicación.

### Receta 6.3: Eligiendo el Protocolo Correcto (A2A vs. MCP)

**Descripción:** Es útil entender cómo A2A se compara con otros estándares emergentes como MCP (Model Context Protocol).

| **Protocolo** | **Foco Principal** | **Caso de Uso Clave** | **Fortalezas** |
| :--- | :--- | :--- | :--- |
| **A2A (Google/LF)** | **Agente-a-Agente** | Colaboración, delegación y orquestación entre múltiples agentes autónomos. | Preparado para la empresa, multimodal, soporte nativo para tareas asíncronas, gobernanza abierta. |
| **MCP (Anthropic)** | **Agente-a-Herramienta** | Conectar un LLM a fuentes de datos, APIs y otras herramientas para proporcionar contexto. | Simple, fácil de adoptar, bueno para añadir capacidades a un solo agente. |

**Sinergia Clave:** A2A y MCP son complementarios. Un agente puede recibir una tarea de otro agente vía **A2A** y luego usar **MCP** internamente para comunicarse con una herramienta (como una base de datos) para completar esa tarea.


