# Resiliencia en Agentes ADK para Sistemas DICOM/PACS

En el desarrollo de agentes de IA con el **Agent Development Kit (ADK)** de Google, especialmente para interactuar con sistemas críticos como **PACS** y el estándar **DICOM**, la **resiliencia** es un pilar arquitectónico fundamental. Un agente robusto debe ser capaz de anticipar, gestionar y recuperarse de una amplia gama de errores.

---

## I. Taxonomía de Errores DICOM

Para diseñar un agente resiliente, es crucial comprender que los fallos en un ecosistema PACS pueden ocurrir en múltiples capas.

### 1. Fallos de Conectividad de Red y Configuración
Estos problemas impiden que cualquier interacción DICOM comience.
* **Causas:** Cables desconectados, IP incorrectas, *firewalls* que bloquean puertos DICOM, o fallos de DNS.
* **Diagnóstico:** Es vital distinguir entre un **ping de red** (verifica la conectividad de red, Capa 3) y una **Verificación `C-ECHO` de DICOM**. Un `C-ECHO` exitoso valida toda la pila de comunicación, incluyendo la configuración de la aplicación y la negociación de Títulos de Entidad de Aplicación (AET).

### 2. Errores de Asociación y Autenticación DICOM
Ocurren cuando la red funciona, pero el cliente (SCU) y el servidor (SCP) no pueden establecer una asociación.
* **"Tríada DICOM" (IP, Puerto, AET):** La causa más frecuente es una configuración incorrecta de estos tres parámetros. Los AET son sensibles a mayúsculas y minúsculas.
* **Negociación de Contexto:** La asociación falla si el cliente y el servidor no pueden acordar una combinación de Clase de SOP y Sintaxis de Transferencia.
* **Seguridad y TLS:** Fallos durante el *handshake* TLS por certificados caducados, no confiables o discrepancias en las suites de cifrado.

### 3. Errores a Nivel de Comando (DIMSE)
Estos errores ocurren después de establecer una asociación exitosa.
* **`C-FIND`:** Las búsquedas pueden fallar si el *dataset* de la consulta está malformado (códigos de error `0xA900` o `0xCxxx`).
* **`C-MOVE`:** Es la operación más compleja y propensa a errores.
    * `0xA801`: **Destino de movimiento desconocido**. El AET de destino no está registrado en el PACS.
    * `0xA702`: **Sin recursos**. El PACS está sobrecargado.
    * `0xB000`: **Warning**. Fallo parcial, no todas las imágenes se transfirieron.
* **`C-STORE`:** Fallos por disco lleno en el servidor, corrupción de datos o ataques de Denegación de Servicio (DoS).

### 4. Degradación del Rendimiento y Sobrecarga
Son "fallos blandos" que se manifiestan como lentitud y *timeouts*.
* **Causas:** Infraestructura de red insuficiente, *hardware* obsoleto o volumen de datos que excede la capacidad del sistema.
* **Clave:** Es vital diferenciar entre errores **transitorios** (reintentables, como `0xA702`) y **permanentes** (no reintentables, como `0xA801`) para decidir la estrategia de recuperación.

---

## II. Estrategias de Resiliencia en Agentes ADK

Un agente robusto debe adoptar estrategias proactivas y reactivas para manejar estos errores.

### 1. Diagnóstico Proactivo: El Rol del `C-ECHO`
El agente debe realizar una verificación `C-ECHO` como una **"comprobación previa al vuelo"** antes de iniciar operaciones críticas. Si el `C-ECHO` falla, la operación principal debe detenerse inmediatamente, presentando un mensaje de error claro al usuario en lugar de fallar más tarde de forma ambigua.

### 2. Gestión de Fallos Transitorios: Reintentos con *Backoff* Exponencial
Para fallos transitorios (congestión, sobrecarga temporal), el agente debe implementar un mecanismo de reintento inteligente.
* ***Backoff* Exponencial:** Aumenta el tiempo de espera entre reintentos de forma exponencial (1s, 2s, 4s...) para no sobrecargar un servidor ya en dificultades.
* ***Jitter*:** Añade un valor aleatorio al tiempo de espera para evitar que múltiples clientes reintenten exactamente al mismo tiempo ("estampida atronadora").
* **Lógica de Fallo Rápido (*Fail-Fast*):** Los errores de configuración (como `0xA801`) no deben reintentarse. El agente debe fallar inmediatamente.

### 3. Gestión de Estado en Operaciones Asíncronas (`C-MOVE`)
La naturaleza asíncrona de `C-MOVE` exige que el agente implemente una **máquina de estados** para gestionar su ciclo de vida.
* **Estados Clave:**
    * `INITIATED`: Tras enviar la solicitud `C-MOVE`.
    * `IN_PROGRESS`: Al recibir respuestas con estado `Pending`. El agente debe escuchar las conexiones `C-STORE` entrantes para recibir las imágenes.
    * `CANCELLING`: Si el usuario solicita la cancelación.
    * `COMPLETED`: Estado terminal (`Success`, `Warning` o `Failure`). En caso de `Warning`, el agente debe intentar registrar las instancias que fallaron.

### 4. Diseño para Alta Disponibilidad: *Failover* y Balanceo de Carga
* ***Failover* (Conmutación por Error):** El agente debe permitir la configuración de AETs de PACS primarios y secundarios. Si el primario falla persistentemente, debe intentar la operación automáticamente con el secundario.
* **Balanceo de Carga:** En infraestructuras grandes, el agente debe comunicarse con el AET virtual proporcionado por un balanceador de carga DICOM.

### 5. Principios de Resiliencia: Degradación Agraciada vs. Fallo Rápido
* **Fallo Rápido (*Fail-Fast*):** Para errores irrecuperables (configuración, autenticación), la mejor estrategia es fallar inmediatamente y notificar al usuario.
* **Degradación Agraciada (*Graceful Degradation*):** Para fallos recuperables o no críticos, el agente debe continuar operando con capacidad reducida. Por ejemplo, si la recuperación de estudios previos falla, debe notificarlo, pero permitir seguir visualizando el estudio actual.

### 6. Defensa Proactiva: Validación y Seguridad
* **Validación de Entradas:** Antes de enviar datos a un PACS (ej. `C-STORE`), el agente debe validar el *dataset* DICOM para prevenir el envío de datos malformados.
* **Comunicación Segura:** El agente debe implementar y preferir **DICOM sobre TLS** para DIMSE, y **HTTPS** con **OAuth 2.0** para DICOMweb.
* **Auditoría de Seguridad:** El agente debe registrar todos los eventos de seguridad relevantes en un formato compatible con IHE ATNA.

### Tabla Resumen de Estrategias

| Categoría de Error | Ejemplo de Error | Estrategia Primaria del Agente | Estrategia Secundaria |
| :--- | :--- | :--- | :--- |
| **Configuración** | AET incorrecto, `0xA801` | **Fallo Rápido** (*Fail-Fast*) | Alerta al usuario con guía de configuración. |
| **Red Transitorio** | Timeout de conexión | ***Backoff* Exponencial con *Jitter*** | *Failover* si los reintentos fallan. |
| **Recurso del Servidor** | `0xA702` (Sin Recursos) | ***Backoff* Exponencial con *Jitter*** | Notificación al usuario de degradación. |
| **Fallo Parcial de Datos** | `C-MOVE` con *Warning* (`0xB000`) | **Máquina de Estado Asíncrona** | Reportar al usuario las instancias fallidas. |
| **Fallo de Característica**| Falla en el renderizador 3D | **Degradación Agraciada** | Usar visor 2D básico, registrar el error. |
| **Seguridad** | *Handshake* TLS fallido | **Fallo Rápido** (*Fail-Fast*) | Registrar evento de auditoría de seguridad. |

---

## Seguridad en Comunicaciones DIMSE con TLS

El protocolo tradicional **`DIMSE`** (DICOM Message Service Element) no tiene seguridad inherente. Para protegerlo, el estándar DICOM especifica el uso de **Transport Layer Security (`TLS`)**, lo que proporciona tres garantías esenciales:

* **Cifrado (Confidencialidad):** Todo el tráfico entre el cliente (`SCU`) y el servidor (`SCP`) se cifra, protegiéndolo de escuchas no autorizadas.
* **Autenticación de Nodos:** Mediante certificados digitales `X.509`, `TLS` permite verificar la identidad del cliente y del servidor, previniendo ataques de suplantación (*man-in-the-middle*). El estándar IHE **`ATNA`** (Audit Trail and Node Authentication) se basa en esta capacidad.
* **Integridad de Datos:** `TLS` asegura que los datos no sean alterados durante la transmisión.

La implementación exitosa de `TLS` depende de una gestión de certificados adecuada, que a menudo requiere una estrecha coordinación entre desarrolladores y administradores de sistemas.

---

## Seguridad en Comunicaciones DICOMweb con HTTPS y OAuth 2.0

La seguridad en **`DICOMweb`** es más sencilla porque aprovecha los estándares web maduros y ampliamente comprendidos.

* **Confidencialidad e Integridad con `HTTPS`:** De forma estándar, toda la comunicación se cifra utilizando `HTTPS` (HTTP sobre TLS), protegiendo los datos de la misma manera que las transacciones bancarias en línea.
* **Autorización con `OAuth 2.0`:** Para el control de acceso, `DICOMweb` se integra con marcos modernos como **`OAuth 2.0`**. Esto permite a una aplicación obtener acceso limitado a los recursos sin compartir directamente las credenciales del usuario. El flujo implica que la aplicación cliente obtiene un **`token de acceso`** de un servidor de autorización y lo incluye en cada petición al servidor `DICOMweb`.

---

## Gestión de Credenciales y la Capa de Aislamiento

La autenticación tradicional de PACS, basada en Títulos de Entidad de Aplicación (`AETs`) y listas blancas de IP, es insegura. **Integrar directamente esta lógica en una herramienta ADK es una mala práctica de seguridad**.

La arquitectura correcta es crear una **capa de aislamiento segura**, que es un **microservicio intermediario** (p. ej., una API REST con `FastAPI`) entre el agente ADK y el PACS. Este servicio se encarga de:

1.  **Autenticar** al agente ADK con métodos modernos (ej. `JWT`).
2.  **Recuperar** las credenciales del PACS de un sistema de gestión de secretos.
3.  **Realizar** la comunicación con el PACS en nombre del agente.

Este patrón **desacopla al agente del riesgo** del protocolo heredado y centraliza la gestión de secretos.

### Métodos de Gestión de Credenciales

* **Código Duro (*Hard-coding*):** **Inaceptable** para datos sensibles.
* **Archivo `.env`:** **Insuficiente** para producción.
* **Archivo Cifrado:** No recomendado, gestiona un nuevo problema: la clave de cifrado.
* **Llavero del SO (*OS Keyring*):** Inadecuado para servicios de *backend*.
* **Gestor de Secretos en la Nube (p.ej., Google Secret Manager):** **Altamente recomendado** para producción. Proporciona almacenamiento seguro, rotación, control de acceso y auditoría, características esenciales para el cumplimiento de normativas como HIPAA.

---

## Integración de la Seguridad en el Diseño del Agente ADK

La filosofía **"code-first"** y la arquitectura modular del ADK contribuyen directamente a un diseño más seguro.

* **Trazabilidad:** Al definir todo en código, se crea un rastro de auditoría completo a través del control de versiones, lo que mejora la gobernanza y el cumplimiento normativo.
* **Aislamiento:** La arquitectura de sistemas multiagente permite aislar las operaciones sensibles en agentes especializados. Por ejemplo, un agente principal delega la comunicación con el PACS a un subagente específico que, a su vez, interactúa con la capa de aislamiento segura.
* **Defensas Proactivas:** Un agente robusto debe incluir:
    * **Validación de Entradas:** Verificar los *datasets* DICOM antes de enviarlos para prevenir el envío de datos malformados.
    * **Auditoría de Seguridad:** Registrar todos los eventos relevantes (inicios de sesión, acceso a datos) en un formato compatible con **`IHE ATNA`**.
    * **Verificación `C-ECHO`:** Realizar una comprobación proactiva de la conectividad antes de iniciar operaciones críticas.