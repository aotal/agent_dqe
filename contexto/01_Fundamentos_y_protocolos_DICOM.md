# El Estándar DICOM: Historia, Principios y Estructura

El estándar **DICOM** (Digital Imaging and Communications in Medicine) es el pilar fundamental que sustenta la interoperabilidad en la imagenología médica moderna, abarcando desde su génesis hasta sus complejos principios y estructuras de datos.

---

## 1. Historia y Evolución de DICOM

El estándar DICOM surgió para resolver la **falta de un lenguaje común** entre los equipos de imagen médica de diferentes fabricantes en la década de 1980. Inicialmente, cada fabricante tenía formatos de archivo y protocolos de comunicación propietarios, creando "islas de información" que impedían la visualización o el archivo de imágenes entre distintos sistemas.

* **ACR-NEMA (1985):** Para abordar este problema, el Colegio Americano de Radiología (ACR) y la Asociación Nacional de Fabricantes Eléctricos (NEMA) publicaron en 1985 el estándar ACR-NEMA 300. Este fue un primer intento de estandarización, enfocado en una interfaz de hardware punto a punto y un conjunto mínimo de comandos.
* **DICOM 3.0 (1993):** La verdadera revolución llegó en 1993 con la versión 3.0, rebautizada como DICOM. Esta versión **abandonó el enfoque de hardware específico y adoptó los protocolos de red estándar TCP/IP**. Este cambio fue crucial, ya que permitió la comunicación entre dispositivos DICOM a través de redes hospitalarias e incluso internet, sentando las bases para los modernos Sistemas de Comunicación y Archivo de Imágenes (PACS).
* **Evolución Continua:** Desde entonces, DICOM ha evolucionado bajo la supervisión de un comité internacional y es mucho más que un simple formato de archivo. Es un **ecosistema completo** que especifica un formato de archivo, un protocolo de comunicación de red (DIMSE) y un modelo de información jerárquica.

---

## 2. Principios Fundamentales

La interoperabilidad en DICOM se basa en conceptos abstractos pero esenciales para una comunicación fiable.

* **Definición de Objeto de Información (IOD - Information Object Definition):** Un IOD es una **plantilla que especifica qué atributos debe contener un tipo particular de objeto DICOM**. Por ejemplo, el IOD de una imagen de RM define los módulos de información (Paciente, Estudio, Serie, Equipo de RM, Píxeles de Imagen) y los atributos obligatorios y opcionales dentro de cada módulo, asegurando que todas las imágenes de RM contengan un conjunto base de metadatos consistentes.
* **Clase de Servicio-Objeto (SOP Class - Service-Object Pair Class):** Una SOP Class es la **unidad fundamental de conformidad en DICOM**. Se define como la combinación de un **Servicio** (una acción, como almacenar o buscar) y un **Objeto de Información** (el tipo de datos sobre el que actúa el servicio). Dos dispositivos DICOM solo pueden realizar una operación si ambos soportan la misma SOP Class. Por ejemplo, `CT Image Storage` combina el servicio `C-STORE` con el objeto `CT Image IOD`.
* **Declaración de Conformidad (Conformance Statement):** Este **documento técnico es el contrato que detalla exactamente qué capacidades DICOM posee un equipo**. Es indispensable para la integración de sistemas, ya que especifica las SOP Classes soportadas, el rol (SCU/SCP), las Sintaxis de Transferencia soportadas y opciones de red/seguridad. Un desarrollador debe consultar estos documentos antes de escribir código para verificar la compatibilidad, ya que la comunicación fallará si no hay un terreno común.

---

## 3. Estructura de Datos (Anatomía de un Objeto DICOM)

Un objeto DICOM es una colección estructurada de información.

* **Elemento de Datos (Data Element):** Es la **unidad atómica de información en DICOM**. Cada metadato se almacena en un Elemento de Datos, compuesto por cuatro partes:
    * **Tag (Etiqueta):** Un identificador único `(gggg,eeee)` que indica el Número de Grupo (`gggg`, par para tags públicos, impar para privados) y el Número de Elemento (`eeee`).
    * **Value Representation (VR - Representación de Valor):** Un código de dos caracteres que especifica el **tipo y formato del valor** (ej. `PN` para "Person Name", `DA` para "Date"). La integridad de los datos médicos depende de la correcta interpretación y generación de estas VRs. Bibliotecas como `pydicom` abstraen esta complejidad, convirtiendo VRs complejas en tipos de datos Python estructurados.
    * **Value Length (VL - Longitud de Valor):** Un entero que especifica la longitud en bytes del campo de valor.
    * **Value Field (VF - Campo de Valor):** Contiene el dato en sí, codificado según la VR.
    * **Multiplicidad de Valor (VM):** Indica cuántos valores puede contener un elemento; si es > 1, los valores se separan por `\`.

* **Sintaxis de Transferencia (Transfer Syntax):** Es un **conjunto de reglas de codificación** que especifica cómo se serializa un objeto DICOM en un flujo de bytes. Define tres características fundamentales:
    * **VR Implícita vs. Explícita:** Si el código VR se incluye explícitamente o debe inferirse.
    * **Orden de Bytes (Endianness):** Si el byte menos o más significativo se almacena primero.
    * **Compresión de Datos de Píxeles:** Si los datos de píxeles están sin comprimir o usan algoritmos como JPEG.
    
    Cuando dos aplicaciones DICOM se comunican, **negocian la Sintaxis de Transferencia** a utilizar. Un programa debe leer el `TransferSyntaxUID (0002,0010)` para decodificar correctamente el resto del archivo.

---

## 4. Modelo Jerárquico (Paciente-Estudio-Serie-Instancia)

Para organizar la vasta cantidad de datos clínicos, DICOM define un **modelo de información jerárquico** que refleja la estructura lógica de la atención al paciente. Esta jerarquía es crucial para la organización de datos en PACS y para las consultas.

* **Paciente (Patient):** Nivel más alto, representa a un individuo. Identificado por `Patient ID (0010,0020)`. Un paciente puede tener múltiples estudios.
* **Estudio (Study):** Representa un único evento de imagenología (ej. una visita para una TC de tórax). Cada estudio tiene un `Study Instance UID (0020,000D)` único.
* **Serie (Series):** Dentro de un estudio, las imágenes se agrupan en series, que son conjuntos de imágenes adquiridas con un protocolo común. Cada serie tiene un `Series Instance UID (0020,000E)` único.
* **Instancia (Instance):** Es el nivel más bajo, representa un **único objeto de información DICOM**, como una imagen o un informe. Cada instancia tiene un `SOP Instance UID (0008,0018)` único y persistente.

Esta estructura es la base de los servicios de consulta y recuperación de DICOM, permitiendo búsquedas en cualquier nivel usando sus UIDs como claves primarias.

# DIMSE vs. DICOMweb: Protocolos de Comunicación en Medicina

El estándar **DICOM** (Digital Imaging and Communications in Medicine) es fundamental para la interoperabilidad en la imagenología médica. Su evolución ha llevado a la creación de dos paradigmas de comunicación principales: el protocolo **DIMSE** (DICOM Message Service Element), más tradicional, y **DICOMweb**, un enfoque moderno basado en estándares web RESTful.

---

## 5. El Protocolo DIMSE: Comunicación DICOM Tradicional

El protocolo DIMSE define cómo se comunican las aplicaciones DICOM a través de una red TCP/IP. Se basa en un modelo cliente-servidor, donde una entidad inicia la operación (**SCU** - Service Class User) y otra la proporciona (**SCP** - Service Class Provider).

Antes de cualquier intercambio, el SCU y el SCP deben establecer una **Asociación**, un proceso de "apretón de manos" donde negocian parámetros como los **Contextos de Presentación** (combinación de `SOP Classes` y `Sintaxis de Transferencia`) y la identificación de cada aplicación mediante un **Título de Entidad de Aplicación (AET)**. La seguridad se habilita mediante **Transport Layer Security (TLS)** para cifrado y autenticación.

A continuación, se detallan los servicios DIMSE clave:

* **`C-ECHO` (DICOM Ping):** Es una operación de la capa de aplicación (Capa 7) que verifica la **conectividad de toda la pila de comunicación DICOM**. Una respuesta exitosa (código `0x0000`) confirma que la red, los firewalls, el AET del servidor y la aplicación PACS están funcionando correctamente.

* **`C-STORE` (Almacenamiento):** Es la operación más fundamental para **enviar una instancia de un objeto DICOM** (como una imagen) desde un SCU a un SCP para su almacenamiento. Por ejemplo, las modalidades de adquisición envían imágenes al PACS mediante `C-STORE`.

* **`C-FIND` (Consulta):** Permite a un SCU realizar **consultas en la base de datos de un SCP**, similar a una consulta `SELECT` en SQL. El SCU construye un **Identificador** (un dataset DICOM) con criterios de búsqueda y especifica un **Nivel de Consulta** (`PATIENT`, `STUDY`, `SERIES` o `IMAGE`).

* **`C-MOVE` y `C-GET` (Recuperación):** Se utilizan para recuperar estudios una vez identificados.
    * **`C-MOVE`** es el servicio más común en PACS comerciales. Es una operación asíncrona que involucra **dos asociaciones distintas**. El SCU original ordena al SCP (PACS) que envíe los datos a una **tercera entidad de aplicación**. La complejidad de `C-MOVE` es una fuente de problemas de configuración y conectividad (un error común es `0xA801`: "Destino de movimiento desconocido").
    * **`C-GET`** es un servicio alternativo que envía los datos de vuelta al SCU a través de la **misma asociación original**, lo que simplifica la configuración de red. Sin embargo, su adopción es mucho más limitada.

### Comparativa: C-GET vs C-MOVE

| Característica | C-GET | C-MOVE |
| :--- | :--- | :--- |
| **Flujo de Datos** | El cliente (SCU) **obtiene** los datos del servidor (SCP) en la misma asociación de red. | El cliente (SCU) **solicita** al servidor (SCP) que **mueva** los datos a un tercer destino preconfigurado. |
| **Modelo de Asociación** | Una **única asociación** para la consulta y la transferencia de datos. | **Dos asociaciones**: una para la solicitud `C-MOVE` y otra nueva que el PACS inicia hacia el destino. |
| **Facilidad con Firewalls** | **Problemático**. Requiere que el cliente abra un puerto de escucha para recibir los datos. | **Más amigable**. El destino es un servidor con un puerto conocido y la comunicación es iniciada desde el PACS. |
| **Implicaciones de Seguridad** | Considerado **menos seguro**, ya que la conexión entrante al cliente puede ser un vector de ataque. | Considerado **más seguro**. El PACS solo envía datos a destinos de confianza (AETs) preconfigurados. |
| **Caso de Uso Típico** | Estaciones de trabajo simples o redes no restringidas. | Flujos de trabajo empresariales, archivado a largo plazo y envío a estaciones de radiología específicas. |

---

## 6. El Protocolo DICOMweb: La Modernización RESTful

**DICOMweb** es una adaptación de los servicios DICOM al paradigma **RESTful**, diseñado para superar los desafíos de DIMSE en entornos web y móviles. Aprovecha estándares ubicuos como **HTTP/HTTPS**, mapea operaciones a verbos HTTP (`POST`, `GET`), trata los objetos como recursos con URLs y permite el intercambio de metadatos en **JSON y XML**. Esto reduce la barrera de entrada para los desarrolladores. La seguridad se logra usando **HTTPS** y **OAuth 2.0**.

Los servicios DICOMweb clave son:

* **`QIDO-RS` (Query based on ID for DICOM Objects):** Equivalente a `C-FIND` para **realizar consultas**. Las peticiones se construyen como `HTTP GET` a una URL, y el servidor responde con JSON o XML.

* **`WADO-RS` (Web Access to DICOM Objects):** Análogo a `C-MOVE`/`C-GET` para **recuperar objetos DICOM**. Utiliza peticiones `HTTP GET`. Permite solicitar una versión renderizada (ej., JPEG, PNG) en lugar del objeto DICOM nativo.

* **`STOW-RS` (Store Over the Web):** Equivalente a `C-STORE` para **almacenar objetos DICOM**. Se implementa mediante una petición `HTTP POST`, típicamente con un tipo de contenido `multipart/related`.

### Diferencias Clave: DIMSE vs. DICOMweb

| Característica | Protocolo DIMSE | Protocolo DICOMweb |
| :--- | :--- | :--- |
| **Protocolo Base** | TCP/IP (Protocolo binario personalizado) | HTTP/1.1 o superior (HTTPS) |
| **Estado de Conexión** | Stateful (requiere Asociación) | Stateless (cada petición es independiente) |
| **Formato de Datos** | Binario DICOM (Parte 10) | JSON, XML, Binario DICOM |
| **Amigable con Firewall** | No (especialmente `C-MOVE`) | Sí (usa puertos estándar 80/443) |
| **Almacenamiento** | `C-STORE` | `STOW-RS` (POST) |
| **Consulta** | `C-FIND` | `QIDO-RS` (GET) |
| **Recuperación** | `C-MOVE` / `C-GET` | `WADO-RS` (GET) |

---

## 7. Modelo Jerárquico DICOM y su Interacción

La organización de los datos DICOM se basa en un **modelo de información jerárquico** que refleja la atención al paciente: **Paciente -> Estudio -> Serie -> Instancia**.

* **Paciente:** Nivel más alto, identificado por `Patient ID (0010,0020)`.
* **Estudio:** Un evento de imagenología, con un `Study Instance UID (0020,000D)` único.
* **Serie:** Grupo de imágenes dentro de un estudio, con un `Series Instance UID (0020,000E)` único.
* **Instancia:** El objeto individual (ej. una imagen), con un `SOP Instance UID (0008,0018)` único.

Esta estructura es fundamental, ya que los servicios DIMSE (`C-FIND`, `C-MOVE`) y DICOMweb (`QIDO-RS`, `WADO-RS`) interactúan directamente con esta jerarquía para buscar y recuperar datos usando los UIDs de cada nivel como claves primarias.