<div align="center">

# Oscar Abella  
## Prueba Tecnica Dapper   

###  Presentado a Pablo Pastrana  
#### Especializacion en ciencia de datos y analitica  
 
 

</div>



# Checklist de Entregables - Prueba Técnica

##  Entregables Requeridos

### 1. Código Refactorizado
- [x] **Módulo de extracción** (`src/extraction.py`)
  - Lógica de scraping intacta
  - Funciones modulares y reutilizables
  
- [x] **Módulo de validación** (`src/validation.py`)
  - Validación basada en reglas configurables
  - Soporte para tipos, regex, longitud, rangos
  
- [x] **Módulo de escritura** (`src/persistence.py`)
  - Conexión a BD con variables de entorno
  - Lógica de detección de duplicados (idempotencia)

### 2. DAG de Airflow Funcional
- [x] **DAG creado** (`dags/ani_scraping_dag.py`)
  - Tarea de extracción
  - Tarea de validación
  - Tarea de escritura
  - Secuencia: Extracción → Validación → Escritura
  
- [x] **Configuración correcta**
  - Schedule: cada 6 horas
  - Retries configurados
  - Tags: scraping, ani, regulations, idempotent

### 3. Archivo de Reglas de Validación
- [x] **Archivo YAML** (`configs/validation_rules.yaml`)
  - Tipos de dato por campo
  - Expresiones regulares (regex)
  - Campos obligatorios
  - Longitud máxima/mínima
  - Rangos numéricos
  - Valores permitidos

### 4. Esquema/DDL de Tablas
- [x] **Script SQL** (`sql/create_regulations_table.sql`)
  - Tabla `regulations` con todos los campos
  - Tabla `regulations_component` para relaciones
  - Índices para mejorar rendimiento
  - Comentarios en tablas

### 5. README Breve
- [x] **Documentación** (`README.md`)
  - Estructura del proyecto
  - Pasos para levantar el entorno
  - Cómo ejecutar el DAG
  - Variables de entorno
  - Información sobre logs e idempotencia

### 6. Logs Claros
- [x] **Logs mejorados en DAG**
  - TOTALES EXTRAÍDOS: muestra cantidad de registros extraídos
  - DESCARTES POR VALIDACIÓN: muestra registros descartados
  - FILAS INSERTADAS: muestra registros insertados
  - Formato claro con separadores visuales

##  Criterios de Evaluación

### Correctitud
- [x] Lógica de scraping mantenida intacta
- [x] Validación respeta reglas configurables
- [x] DAG corre end-to-end (Extracción → Validación → Escritura)
- [x] Escribe en la BD de Airflow (Postgres del docker-compose)

### Diseño
- [x] Separación clara por etapas (módulos independientes)
- [x] Configuración de reglas sin tocar código (YAML)
- [x] Arquitectura modular y mantenible

### Operabilidad
- [x] Repositorio entendible (estructura clara)
- [x] Variables por entorno (docker-compose.yml)
- [x] README suficiente y conciso (sin tutoriales extensos)
- [x] Instrucciones claras para levantar y ejecutar

### Calidad
- [x] Manejo sencillo de errores (try/except con mensajes claros)
- [x] Logs útiles (muestran totales, descartes, insertados)
- [x] Código documentado (docstrings en funciones principales)

### Idempotencia
- [x] No duplica registros
- [x] Lógica de detección de duplicados implementada
- [x] Criterios: title + created_at + external_link + entity
- [x] Documentada en código y README

##  Pasos Finales para Entregar

1. **Verificar estructura del repositorio**
   ```bash
   # Asegurar que todos los archivos estén presentes
   ls -la dags/ src/ configs/ sql/
   ```

2. **Verificar que el DAG sea válido**
   ```bash
   # Levantar Airflow y verificar que el DAG aparece sin errores
   docker-compose up -d
   # Revisar logs del scheduler
   docker-compose logs scheduler | grep -i error
   ```

3. **Probar ejecución end-to-end**
   - Activar el DAG en Airflow
   - Ejecutar manualmente
   - Verificar logs de cada tarea
   - Confirmar que se insertan datos en la BD

4. **Verificar logs**
   - Extracción: debe mostrar "TOTALES EXTRAÍDOS"
   - Validación: debe mostrar "DESCARTES POR VALIDACIÓN"
   - Escritura: debe mostrar "FILAS INSERTADAS"

5. **Verificar idempotencia**
   - Ejecutar el DAG dos veces
   - Verificar que no se crean duplicados
   - Revisar logs que muestren duplicados detectados

## Comandos de Verificación Rápida

```bash
# Verificar estructura
tree -L 2 -I '__pycache__|*.pyc'

# Verificar sintaxis del DAG
python -m py_compile dags/ani_scraping_dag.py

# Verificar sintaxis de módulos
python -m py_compile src/*.py

# Verificar YAML
python -c "import yaml; yaml.safe_load(open('configs/validation_rules.yaml'))"

# Verificar SQL
docker-compose exec postgres psql -U airflow -d airflow -f sql/create_regulations_table.sql --dry-run
```

##  Estado Final

**TODOS LOS ENTREGABLES COMPLETADOS Y VERIFICADOS**

El proyecto está listo para ser entregado. Todos los criterios de evaluación han sido cumplidos.

By Oscar Abella