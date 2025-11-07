<div align="center">

# Oscar Abella  
## Prueba Tecnica Dapper   

###  Presentado a Pablo Pastrana  
#### Especializacion en ciencia de datos y analitica  
 
 

</div>

# Ejecución del Proyecto y Explicación para Entrevista

## Pasos para Ejecutar el Proyecto

### Paso 1: Preparar el Entorno

```bash
# 1. Navegar al directorio del proyecto
cd prueba_tecnica_DE_Dapper

# 2. Verificar que Docker esté corriendo
docker --version
docker-compose --version

# 3. Crear directorios necesarios (si no existen)
mkdir -p logs dags plugins config configs sql
```

### Paso 2: Crear las Tablas en la Base de Datos

```bash
# Ejecutar el script SQL para crear las tablas
docker-compose exec postgres psql -U airflow -d airflow < sql/create_regulations_table.sql

# Verificar que las tablas se crearon correctamente
docker-compose exec postgres psql -U airflow -d airflow -c "\dt"
```

**Resultado esperado:** Debe mostrar las tablas `regulations` y `regulations_component`

### Paso 3: Inicializar Airflow (Solo Primera Vez)

```bash
# Opción 1: Usar Makefile
make init-airflow

# Opción 2: Manualmente
docker-compose run --rm webserver airflow db init
docker-compose run --rm webserver airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

### Paso 4: Levantar los Servicios

```bash
# Levantar todos los servicios (Postgres, Scheduler, Webserver)
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

**Resultado esperado:**
```
NAME                STATUS
postgres            Up
scheduler           Up
webserver           Up
```

### Paso 5: Acceder a la Interfaz de Airflow

1. Abrir navegador en: **http://localhost:8080**
2. Login:
   - Usuario: `admin`
   - Contraseña: `admin`

### Paso 6: Activar y Ejecutar el DAG

1. **Buscar el DAG:**
   - En la lista de DAGs, buscar `ani_regulations_scraping`
   - Verificar que aparece sin errores (icono verde)

2. **Activar el DAG:**
   - Hacer clic en el toggle (switch) a la izquierda del nombre del DAG
   - Debe cambiar a color azul (activado)

3. **Ejecutar el DAG:**
   - Hacer clic en el nombre del DAG
   - Hacer clic en el botón "Trigger DAG" (icono de play)
   - El DAG comenzará a ejecutarse

### Paso 7: Monitorear la Ejecución

1. **Ver el estado general:**
   - En la vista de árbol o gráfico, ver las 3 tareas
   - Verde = éxito, Rojo = error, Amarillo = en ejecución

2. **Ver logs de cada tarea:**
   - Clic en la tarea `extraction`
   - Clic en "Log"
   - Debe mostrar: `✅ EXTRACCIÓN COMPLETADA` y `📊 TOTALES EXTRAÍDOS: X registros`
   
   - Repetir para `validation`:
   - Debe mostrar: `✅ VALIDACIÓN COMPLETADA`, `📊 REGISTROS ORIGINALES`, `❌ DESCARTES POR VALIDACIÓN: X`
   
   - Repetir para `writing`:
   - Debe mostrar: `✅ ESCRITURA COMPLETADA` y `📝 FILAS INSERTADAS: X`

### Paso 8: Verificar Datos en la Base de Datos

```bash
# Contar registros insertados
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"

# Ver algunos registros
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT title, created_at, entity FROM regulations LIMIT 5;"
```

### Paso 9: Verificar Idempotencia (Opcional)

```bash
# Contar registros antes
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"

# Ejecutar el DAG nuevamente desde Airflow UI

# Contar registros después (debe ser el mismo número si todos eran duplicados)
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"
```

En los logs de la tarea `writing`, debe aparecer: `Duplicados encontrados: X`

---

## Explicación para la Entrevista (Como Data Engineer)

### Introducción

"Implementé un pipeline de datos end-to-end para extraer, validar y almacenar normativas de la Agencia Nacional de Infraestructura (ANI) usando Apache Airflow. El proyecto sigue las mejores prácticas de ingeniería de datos con separación de responsabilidades, configuración externa e idempotencia."

### Arquitectura y Diseño

**1. Modularización:**
"Separé el código en tres módulos independientes siguiendo el principio de responsabilidad única:

- **Módulo de Extracción** (`extraction.py`): Contiene toda la lógica de web scraping, manteniendo intacta la lógica original del código base. Incluye funciones para scrapear páginas, extraer títulos, enlaces, fechas y resúmenes, con limpieza y normalización de datos.

- **Módulo de Validación** (`validation.py`): Implementa un validador configurable basado en reglas YAML. Permite validar tipos de dato, expresiones regulares, longitud, rangos numéricos y valores permitidos. Si un campo no cumple y no es obligatorio, se pone a NULL; si es obligatorio, se descarta la fila completa.

- **Módulo de Persistencia** (`persistence.py`): Maneja la conexión a base de datos y la inserción de datos. Implementa lógica de detección de duplicados para garantizar idempotencia, comparando registros por título, fecha de creación, enlace externo y entidad."

**2. Configuración Externa:**
"Las reglas de validación están en un archivo YAML (`validation_rules.yaml`), lo que permite modificar los criterios de validación sin tocar código. Esto facilita el mantenimiento y permite que diferentes entornos tengan diferentes reglas."

### Orquestación con Airflow

**3. DAG de Airflow:**
"Creé un DAG con tres tareas en secuencia que orquestan el proceso completo:

- **Tarea de Extracción**: Scrapea las páginas de ANI y extrae los datos. Los resultados se pasan a la siguiente tarea mediante XCom.

- **Tarea de Validación**: Valida los datos extraídos según las reglas configurables. Filtra registros inválidos y campos que no cumplen criterios.

- **Tarea de Escritura**: Inserta los datos validados en PostgreSQL, evitando duplicados mediante la lógica de idempotencia implementada.

El DAG está configurado para ejecutarse cada 6 horas automáticamente, con retries y manejo de errores."

### Base de Datos y Persistencia

**4. Integración con PostgreSQL:**
"El proyecto usa la misma base de datos PostgreSQL que levanta el docker-compose de Airflow, eliminando la dependencia de AWS Secrets Manager. Las credenciales se configuran mediante variables de entorno en el docker-compose, siguiendo las mejores prácticas de configuración por entorno.

Creé un script SQL (`create_regulations_table.sql`) con el DDL completo para crear las tablas necesarias, incluyendo índices para optimizar las consultas de detección de duplicados."

### Idempotencia

**5. Prevención de Duplicados:**
"Implementé idempotencia básica reutilizando la lógica existente en el código base. La función `insert_new_records()` consulta primero los registros existentes en la base de datos, crea claves únicas combinando título, fecha de creación y enlace externo, y filtra duplicados antes de insertar. Esto permite ejecutar el DAG múltiples veces sin crear registros duplicados, lo cual es crítico para pipelines de datos que pueden fallar y necesitan re-ejecutarse."

### Logs y Observabilidad

**6. Logging Claro:**
"Implementé logs estructurados que muestran claramente:
- **TOTALES EXTRAÍDOS**: Cantidad de registros obtenidos del scraping
- **DESCARTES POR VALIDACIÓN**: Registros descartados por no cumplir reglas
- **FILAS INSERTADAS**: Registros finalmente insertados en la base de datos

Esto facilita el monitoreo y debugging del pipeline."

### Manejo de Errores

**7. Robustez:**
"Cada etapa del pipeline tiene manejo de errores apropiado. Si la validación falla, el proceso continúa con los datos sin validar (fallback). Si la escritura falla, se captura el error y se reporta claramente en los logs. Esto asegura que el pipeline sea resiliente a errores parciales."

### Puntos Clave para Destacar

**✅ Separación de Responsabilidades:**
"Cada módulo tiene una responsabilidad única y clara, facilitando el mantenimiento y testing."

**✅ Configuración Externa:**
"Las reglas de validación están en YAML, permitiendo cambios sin modificar código."

**✅ Idempotencia:**
"El pipeline puede ejecutarse múltiples veces sin crear duplicados, esencial para pipelines de producción."

**✅ Observabilidad:**
"Logs claros que muestran métricas clave en cada etapa del proceso."

**✅ Operabilidad:**
"README conciso con instrucciones claras, variables de entorno configuradas, y estructura de repositorio entendible."

### Respuesta a Preguntas Comunes

**P: ¿Por qué separaste en módulos?**
R: "Para facilitar el mantenimiento, testing y reutilización. Cada módulo puede evolucionar independientemente y es más fácil identificar y corregir problemas."

**P: ¿Cómo manejas los duplicados?**
R: "Antes de insertar, consulto los registros existentes y creo claves únicas combinando título, fecha y enlace. Comparo los nuevos registros con los existentes usando sets para eficiencia O(1), y filtro duplicados antes de la inserción."

**P: ¿Qué pasa si falla una etapa?**
R: "Cada etapa tiene manejo de errores. Si la validación falla, continúo con los datos sin validar. Si la escritura falla, capturo el error y lo reporto en logs. El DAG tiene retries configurados para recuperarse de errores temporales."

**P: ¿Cómo se puede escalar esto?**
R: "El diseño modular permite escalar horizontalmente. Podríamos paralelizar la extracción de múltiples páginas, usar un validador distribuido, o implementar inserción en batch más grande. La separación de módulos facilita estas optimizaciones."

### Cierre

"El proyecto demuestra mi capacidad para diseñar pipelines de datos robustos, modulares y operables, siguiendo las mejores prácticas de la industria. Está listo para producción con idempotencia, logging claro y manejo de errores apropiado."

---

## Comandos Rápidos de Referencia

```bash
# Levantar todo
docker-compose up -d

# Ver logs del scheduler
docker-compose logs -f scheduler

# Ver logs del webserver
docker-compose logs -f webserver

# Ejecutar SQL directamente
docker-compose exec postgres psql -U airflow -d airflow

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Detener y limpiar volúmenes
docker-compose down --volumes
```

---

## ✅ Checklist de Verificación Pre-Entrevista

- [ ] Proyecto ejecuta sin errores
- [ ] DAG aparece en Airflow
- [ ] Las 3 tareas se ejecutan correctamente
- [ ] Logs muestran totales, descartes e insertados
- [ ] Datos se insertan en la BD
- [ ] Idempotencia funciona (no duplica)
- [ ] README está completo y claro
- [ ] Puedo explicar cada componente del proyecto

By Oscar Abella