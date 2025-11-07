# Pasos Finales para Completar la Prueba Técnica

## 📋 Checklist Pre-Entrega

### Paso 1: Verificar Estructura del Repositorio

```bash
# Verificar que todos los archivos estén presentes
ls -la dags/ani_scraping_dag.py
ls -la src/extraction.py src/validation.py src/persistence.py
ls -la configs/validation_rules.yaml
ls -la sql/create_regulations_table.sql
ls -la README.md
ls -la docker-compose.yml
```

**Debe tener:**
- ✅ `dags/ani_scraping_dag.py` - DAG con 3 tareas
- ✅ `src/extraction.py` - Módulo de extracción
- ✅ `src/validation.py` - Módulo de validación
- ✅ `src/persistence.py` - Módulo de escritura
- ✅ `configs/validation_rules.yaml` - Reglas de validación
- ✅ `sql/create_regulations_table.sql` - DDL de tablas
- ✅ `README.md` - Documentación breve
- ✅ `docker-compose.yml` - Configuración de Airflow

### Paso 2: Verificar Sintaxis del Código

```bash
# Verificar sintaxis del DAG
python -m py_compile dags/ani_scraping_dag.py

# Verificar sintaxis de módulos
python -m py_compile src/extraction.py
python -m py_compile src/validation.py
python -m py_compile src/persistence.py

# Verificar YAML
python -c "import yaml; yaml.safe_load(open('configs/validation_rules.yaml'))"
```

**Si no hay errores, continúa al siguiente paso.**

### Paso 3: Levantar el Entorno

```bash
# 1. Crear directorios necesarios (si no existen)
mkdir -p logs dags plugins config configs sql

# 2. Crear las tablas en la base de datos
docker-compose exec postgres psql -U airflow -d airflow < sql/create_regulations_table.sql

# 3. Inicializar Airflow (solo primera vez)
make init-airflow

# O manualmente:
docker-compose run --rm webserver airflow db init
docker-compose run --rm webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com

# 4. Levantar servicios
docker-compose up -d

# 5. Verificar que los servicios estén corriendo
docker-compose ps
```

**Debe mostrar:**
- ✅ `postgres` - running
- ✅ `scheduler` - running
- ✅ `webserver` - running

### Paso 4: Verificar que el DAG Aparece en Airflow

1. Abrir navegador en: http://localhost:8080
2. Login: `admin` / `admin`
3. Buscar el DAG `ani_regulations_scraping`
4. Verificar que aparece sin errores (icono verde)

**Si hay errores, revisar logs:**
```bash
docker-compose logs scheduler | tail -50
```

### Paso 5: Probar Ejecución End-to-End

1. **En Airflow UI:**
   - Activar el DAG (toggle en la izquierda)
   - Hacer clic en el DAG
   - Hacer clic en "Trigger DAG" (botón play)
   - Esperar a que termine la ejecución

2. **Verificar logs de cada tarea:**
   - Clic en la tarea `extraction`
   - Clic en "Log"
   - Debe mostrar: `✅ EXTRACCIÓN COMPLETADA` y `📊 TOTALES EXTRAÍDOS: X registros`
   
   - Clic en la tarea `validation`
   - Clic en "Log"
   - Debe mostrar: `✅ VALIDACIÓN COMPLETADA`, `📊 REGISTROS ORIGINALES`, `❌ DESCARTES POR VALIDACIÓN`
   
   - Clic en la tarea `writing`
   - Clic en "Log"
   - Debe mostrar: `✅ ESCRITURA COMPLETADA` y `📝 FILAS INSERTADAS: X`

3. **Verificar datos en la base de datos:**
```bash
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"
```

**Debe mostrar un número mayor a 0 si se insertaron registros.**

### Paso 6: Verificar Idempotencia

1. **Ejecutar el DAG una segunda vez:**
   - En Airflow UI, hacer clic en "Trigger DAG" nuevamente
   - Esperar a que termine

2. **Verificar logs de la tarea `writing`:**
   - Debe mostrar mensajes sobre duplicados detectados
   - Debe mostrar: `Duplicados encontrados: X`
   - Si todos son duplicados: `No new records found`

3. **Verificar que no se crearon duplicados:**
```bash
# Contar registros antes
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"

# Ejecutar DAG nuevamente

# Contar registros después (debe ser el mismo número)
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM regulations;"
```

### Paso 7: Verificar Variables de Entorno

```bash
# Verificar que las variables están en docker-compose.yml
grep -A 5 "DB_HOST\|DB_NAME\|DB_USERNAME" docker-compose.yml
```

**Debe mostrar:**
- `DB_HOST: postgres`
- `DB_NAME: airflow`
- `DB_USERNAME: airflow`
- `DB_PASSWORD: airflow`

### Paso 8: Verificar README

1. Abrir `README.md`
2. Verificar que contiene:
   - ✅ Estructura del proyecto
   - ✅ Pasos para levantar el entorno
   - ✅ Cómo ejecutar el DAG
   - ✅ Variables de entorno
   - ✅ Información sobre logs

**El README debe ser breve y al punto (no tutorial extenso).**

## ✅ Verificación Final

### Entregables Completados

- [x] Código refactorizado (módulos separados)
- [x] DAG de Airflow funcional (3 tareas en secuencia)
- [x] Archivo de reglas de validación (YAML)
- [x] Esquema/DDL de tablas (SQL)
- [x] README breve
- [x] Logs claros (totales, descartes, insertados)

### Criterios de Evaluación Cumplidos

- [x] **Correctitud**: Lógica mantenida, validación funciona, DAG corre end-to-end
- [x] **Diseño**: Separación clara, configuración sin tocar código
- [x] **Operabilidad**: Repositorio entendible, variables por entorno, README suficiente
- [x] **Calidad**: Manejo de errores, logs útiles
- [x] **Idempotencia**: No duplica registros

## 🚀 Listo para Entregar

Si todos los pasos anteriores se completaron exitosamente, el proyecto está **LISTO PARA ENTREGAR**.

### Resumen de lo que se entregará:

1. **Repositorio completo** con todos los archivos
2. **DAG funcional** que corre end-to-end
3. **Documentación** clara y concisa
4. **Logs** que muestran claramente los resultados
5. **Idempotencia** verificada

### Comandos de Limpieza (Opcional)

Si necesitas limpiar y empezar de nuevo:

```bash
# Detener y eliminar contenedores y volúmenes
docker-compose down --volumes

# Limpiar logs y archivos temporales
rm -rf logs/* dags/__pycache__ src/__pycache__
```

## 📝 Notas Finales

- El DAG está configurado para ejecutarse cada 6 horas automáticamente
- Los logs muestran claramente: totales extraídos, descartes por validación, filas insertadas
- La idempotencia está implementada y verificada
- Las reglas de validación se pueden modificar en `configs/validation_rules.yaml` sin tocar código
- Las variables de entorno están configuradas en `docker-compose.yml`

**¡Éxito en la prueba técnica! 🎉**

