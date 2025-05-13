# Sistema de Videovigilancia Distribuida

Este proyecto implementa una **arquitectura de videovigilancia** basada en contenedores y Kubernetes, que ingiere, almacena y procesa flujos de video para detectar intrusiones. Utiliza RabbitMQ para la mensajería, MinIO para almacenamiento de objetos y InfluxDB para series temporales.

---

## 📖 Descripción

El sistema consta de tres servicios principales:

1. **Producer**: Lee videos (archivos `.mp4`/`.avi`) y publica cada frame como mensaje (bytes) en RabbitMQ, junto con metadatos JSON.
2. **Consumer**:

   * **Imágenes**: Extrae los bytes del frame, los sube a MinIO y publica un enlace firmado.
   * **Metadatos**: Recibe JSON con `image_name`, `probability` y `image_url`, y escribe un punto en InfluxDB.
3. **Almacenamiento y Base de datos**:

   * **MinIO**: Bucket `intrusiones` para guardar las imágenes capturadas.
   * **InfluxDB**: Bucket `intrusiones` para series temporales de eventos de intrusión.

Complementan el repositorio scripts auxiliares bajo `otros/` para descargar datos, generar URLs firmadas y consultas.

---

## 🚀 Requisitos

* **Kubernetes** con `kubectl` configurado.
* **Docker**.
* **Python 3.13**.
* **Pip** y **Poetry**.

---

## 📂 Estructura del Repositorio

```
ingenieria-datos-viabi/
├── CHANGELOG.md
├── deploy.sh             # Orquesta instalación de todos los componentes
├── namespace.yaml        # Namespace Kubernetes: monitoring-stack
├── pyproject.toml        # Dependencias comunes
├── release.config.mjs    # Configuración de semantic-release
├── producer/             # Servicio que envía frames y metadatos
│   ├── main.py
│   └── videos/.gitkeep
├── consumer/             # Servicio que procesa mensajes de RabbitMQ
│   ├── images/           # Sube imágenes a MinIO
│   └── metadata/         # Inserta metadatos en InfluxDB
├── influxdb/             # Manifiestos y script para InfluxDB
├── minio/                # Manifiestos y script para MinIO
├── rabbitmq/             # Manifiestos y script para RabbitMQ
├── otros/                # Scripts auxiliares (descarga, consulta, uploads)
└── .github/              # Workflow de CI/CD (semantic-release)
```

---

## 🛠️ Despliegue en Kubernetes

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/ingenieria-datos-viabi.git
   cd ingenieria-datos-viabi
   ```

2. Aplica el namespace y despliega todos los servicios:

   ```bash
   bash deploy.sh
   ```

   Este script crea el namespace `monitoring-stack` e invoca los `install.sh` de cada subdirectorio.

---

## ⚙️ Configuración

Cada despliegue utiliza variables de entorno definidas en sus respectivos YAML de Deployment:

* **MinIO** (`minio/minio.yaml`):

  * `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
  * Servicios en puertos `9000` (API) y `9001` (Console).

* **InfluxDB** (`influxdb/influxdb.yaml`):

  * `DOCKER_INFLUXDB_INIT_*` para creación automática de `admin`/`miorganizacion`/`intrusiones`.
  * Puerto `8086`.

* **RabbitMQ** (`rabbitmq/rabbitmq.yaml`):

  * Usuario `admin` con contraseña `Admin@12345`.

* **Consumer & Producer**:

  * Edita `pyproject.toml` y las variables de entorno en `consumer/*.yaml` y `producer/main.py` para apuntar a tus URLs/credenciales.

---

## ▶️ Uso

### Producer (envío de frames)

Ejecuta localmente o en un Pod:

```bash
cd producer
python main.py
```

Automáticamente publica cada frame en la cola `images` y sus metadatos en `metadata`.

### Consumer Imágenes

1. Construye y sube la imagen Docker:

   ```bash
   docker build -t adriitoral/viabi-consumer-images:latest -f consumer/images/Dockerfile .
   docker push adriitoral/viabi-consumer-images:latest
   ```
2. &#x20;Despliega en Kubernetes:

```
kubectl apply -f consumer/images/consumer.yaml
```

### Consumer Metadatos

1. Construye y sube la imagen Docker:

   ```bash
   docker build -t adriitoral/viabi-consumer-metadata:latest -f consumer/metadata/Dockerfile .
   docker push adriitoral/viabi-consumer-metadata:latest
   ```
2. &#x20;Despliega en Kubernetes:

```
kubectl apply -f consumer/metadata/consumer.yaml
```

### Consultas y Descargas

* **Descargar todas las imágenes**:

  ```bash
  python otros/download_data.py
  ```
* &#x20;**Generar URL firmada**:

```
python otros/get_image_url.py
```

* **Insertar datos en InfluxDB**:

  ```bash
  python otros/insert_influx.py
  ```
* &#x20;**Consultar últimos registros en InfluxDB**:

```
python otros/query_influx.py
```

---

## 📄 Licencia

Este proyecto está bajo la [MIT License](LICENSE).
