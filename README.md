# Proyecto de Scraping de Normativas ANI

Pipeline de datos para extraer, validar y almacenar normativas de ANI usando Airflow.

## Estructura

```
├── dags/ani_scraping_dag.py      # DAG con 3 tareas: Extracción → Validación → Escritura
├── src/
│   ├── extraction.py            # Módulo de extracción (scraping)
│   ├── validation.py             # Módulo de validación
│   └── persistence.py            # Módulo de escritura (BD)
├── configs/validation_rules.yaml # Reglas de validación (tipos/regex/obligatoriedad)
├── sql/create_regulations_table.sql # DDL para crear tablas
└── docker-compose.yml             # Configuración de Airflow
```

## Levantar el Entorno

### 1. Crear tablas en la base de datos

```bash
docker-compose exec postgres psql -U airflow -d airflow < sql/create_regulations_table.sql
```

### 2. Inicializar Airflow (solo primera vez)

```bash
make init-airflow
# O manualmente:
docker-compose run --rm webserver airflow db init
docker-compose run --rm webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com
```

### 3. Levantar servicios

```bash
docker-compose up -d
```

### 4. Acceder a Airflow

- URL: http://localhost:8080
- Usuario: `admin` / Contraseña: `admin`

## Ejecutar el DAG

1. En la interfaz de Airflow, buscar el DAG `ani_regulations_scraping`
2. Activar el DAG (toggle)
3. Ejecutar manualmente o esperar el schedule (cada 6 horas)

## Variables de Entorno

Configuradas en `docker-compose.yml`:
- `DB_HOST=postgres`
- `DB_PORT=5432`
- `DB_NAME=airflow`
- `DB_USERNAME=airflow`
- `DB_PASSWORD=airflow`

## Logs

Los logs muestran claramente:
- **TOTALES EXTRAÍDOS**: Registros obtenidos del scraping
- **DESCARTES POR VALIDACIÓN**: Registros descartados por no cumplir reglas
- **FILAS INSERTADAS**: Registros insertados en la BD

## Idempotencia

El proceso es idempotente: puede ejecutarse múltiples veces sin crear duplicados. Los criterios de duplicados son: `title + created_at + external_link + entity`.

## Configuración de Validación

Las reglas están en `configs/validation_rules.yaml`. Se pueden modificar sin tocar código:
- Campos obligatorios (si no cumplen, se descarta la fila)
- Tipos de dato, regex, longitud, rangos por campo
- Si un campo no obligatorio no cumple, se pone a NULL
