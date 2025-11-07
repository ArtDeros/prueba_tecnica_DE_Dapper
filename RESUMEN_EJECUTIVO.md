# Resumen Ejecutivo - Proyecto ANI Scraping

##  Ejecución Rápida (3 Pasos)

```bash
# 1. Crear tablas
docker-compose exec postgres psql -U airflow -d airflow < sql/create_regulations_table.sql

# 2. Inicializar Airflow (solo primera vez)
make init-airflow

# 3. Levantar servicios
docker-compose up -d
```

**Acceder:** http://localhost:8080 (admin/admin)

**Ejecutar DAG:** Activar toggle → Trigger DAG

---

##  Explicación para Entrevista (Versión Corta)

### ¿Qué implementaste?

"Un pipeline de datos end-to-end con Airflow que extrae, valida y almacena normativas de ANI. Separé el código en 3 módulos (extracción, validación, escritura), implementé validación configurable mediante YAML, y aseguré idempotencia para evitar duplicados."

### ¿Cómo funciona?

1. **Extracción**: Scrapea páginas ANI, extrae títulos, fechas, enlaces
2. **Validación**: Valida según reglas YAML (tipos, regex, obligatoriedad)
3. **Escritura**: Inserta en PostgreSQL evitando duplicados

### ¿Qué destacar?

- ✅ **Modular**: Separación clara de responsabilidades
- ✅ **Configurable**: Reglas en YAML, sin tocar código
- ✅ **Idempotente**: No crea duplicados al re-ejecutar
- ✅ **Observable**: Logs claros (totales, descartes, insertados)
- ✅ **Robusto**: Manejo de errores en cada etapa

### ¿Cómo manejas duplicados?

"Antes de insertar, consulto registros existentes y creo claves únicas con título + fecha + enlace. Comparo usando sets (O(1)) y filtro duplicados. Esto permite re-ejecutar el DAG sin crear duplicados."

---

##  Métricas que Muestran los Logs

- **TOTALES EXTRAÍDOS**: X registros
- **DESCARTES POR VALIDACIÓN**: X registros
- **FILAS INSERTADAS**: X registros

---

##  Puntos Clave

1. **Arquitectura**: 3 módulos independientes
2. **Configuración**: YAML externo
3. **Idempotencia**: Reutilicé lógica existente
4. **Base de datos**: Misma Postgres de Airflow
5. **Variables**: Entorno configurado en docker-compose

---

**documento completo:** `EJECUCION_Y_EXPLICACION.md`

