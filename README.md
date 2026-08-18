# API-Trello

API RESTful para aplicación tipo Trello, desarrollada con FastAPI y MongoDB.

## Descripción

Backend que permite gestionar workspaces, listas y tareas de forma jerárquica, con autenticación vía Firebase y JWT.

## Funcionalidades

- Autenticación de usuarios (Firebase Auth + JWT)
- CRUD de Workspaces
- CRUD de Lists (dentro de workspaces)
- CRUD de Tasks (dentro de listas)
- Mover tareas entre listas
- Paginación de resultados
- Validación de permisos (solo el owner puede modificar)

## Endpoints

### Auth

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/users` | Registrar nuevo usuario |
| POST | `/login` | Iniciar sesión |

### Workspaces

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/workspaces` | Crear workspace |
| GET | `/workspaces` | Listar workspaces del usuario |
| GET | `/workspaces/{id}` | Obtener workspace por ID |
| PUT | `/workspaces/{id}` | Actualizar workspace |
| DELETE | `/workspaces/{id}` | Eliminar workspace |

### Lists

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/{workspace_id}/lists` | Crear lista |
| GET | `/{workspace_id}/lists` | Obtener listas del workspace |
| GET | `/{workspace_id}/lists/{id}` | Obtener lista por ID |
| PUT | `/{workspace_id}/lists/{id}` | Actualizar lista |
| DELETE | `/{workspace_id}/lists/{id}` | Eliminar lista |

### Tasks

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/{workspace_id}/lists/{list_id}/tasks` | Crear tarea |
| GET | `/{workspace_id}/tasks` | Listar tareas del workspace |
| GET | `/{workspace_id}/tasks/{id}` | Obtener tarea por ID |
| PUT | `/{workspace_id}/tasks/{id}` | Actualizar tarea |
| DELETE | `/{workspace_id}/tasks/{id}` | Eliminar tarea |
| PUT | `/{workspace_id}/tasks/{id}/move` | Mover tarea a otra lista |

## Tecnologías

- **FastAPI** 0.116.1
- **MongoDB** (pymongo 4.13.2)
- **Firebase Authentication**
- **JWT** (PyJWT)
- **Pydantic** 2.11.7

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/API-Trello.git
cd API-Trello

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar el servidor
uvicorn main:app --reload
```

La documentación interactiva estará disponible en: `http://localhost:8000/docs`

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_NAME` | Nombre de la base de datos MongoDB |
| `MONGODB_URI` | URI de conexión a MongoDB Atlas |
| `SECRET_KEY` | Clave secreta para JWT |
| `FIREBASE_CREDENTIALS_BASE64` | Credenciales de Firebase en Base64 |
| `FIREBASE_API_KEY` | API Key de Firebase |

## Estructura del Proyecto

```
API-Trello/
├── main.py                 # Punto de entrada
├── controllers/            # Lógica de negocio
│   ├── users.py
│   ├── workspaces.py
│   ├── lists.py
│   └── tasks.py
├── models/                 # Modelos Pydantic
│   ├── base.py
│   ├── users.py
│   ├── login.py
│   ├── workspaces.py
│   ├── lists.py
│   ├── tasks.py
│   └── ...
├── pipelines/              # Aggregation pipelines MongoDB
│   ├── workspace_pipelines.py
│   ├── list_pipline.py
│   └── task_pipline.py
├── routes/                 # Endpoints HTTP
│   ├── workspaces.py
│   ├── lists.py
│   └── tasks.py
├── utils/                  # Utilidades
│   ├── mongodb.py          # Conexión MongoDB
│   └── security.py         # JWT y autenticación
├── requirements.txt
└── .env
```

## Despliegue

API desplegada en **Render**: [https://api-trello-v7re.onrender.com](https://api-trello-v7re.onrender.com)

