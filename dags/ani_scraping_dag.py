"""
DAG de Airflow para el proceso de scraping de normativas ANI.
Flujo: Extracción → Validación → Escritura
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import os
import sys

# Agregar el directorio src al path para importar módulos
# En Airflow, los módulos están en /opt/airflow/src
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
# También intentar la ruta absoluta de Airflow
sys.path.insert(0, '/opt/airflow/src')

from src.extraction import scrape_multiple_pages, ENTITY_VALUE
from src.validation import DataValidator
from src.persistence import DatabaseManager, insert_new_records

# Configuración por defecto de argumentos del DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    'ani_regulations_scraping',
    default_args=default_args,
    description='DAG para extraer, validar y escribir normativas de ANI. '
                'La tarea de escritura es idempotente: evita duplicados automáticamente.',
    schedule_interval=timedelta(hours=6),  # Ejecutar cada 6 horas
    start_date=days_ago(1),
    catchup=False,
    tags=['scraping', 'ani', 'regulations', 'idempotent'],
)


def task_extraction(**context):
    """
    Tarea de Extracción: Scrapea las páginas de ANI y extrae los datos.
    """
    print("=== INICIANDO TAREA DE EXTRACCIÓN ===")
    
    # Obtener parámetros del contexto o usar valores por defecto
    num_pages = context.get('dag_run').conf.get('num_pages_to_scrape', 9) if context.get('dag_run') else 9
    
    print(f"Extrayendo datos de {num_pages} páginas...")
    
    # Realizar scraping
    all_normas_data = scrape_multiple_pages(
        num_pages=num_pages,
        start_page=0,
        verbose=True
    )
    
    if not all_normas_data:
        print("No se encontraron datos durante la extracción")
        # Guardar resultado vacío en XCom para que las siguientes tareas lo manejen
        return {
            'data': [],
            'total_records': 0
        }
    
    total_extracted = len(all_normas_data)
    print("=" * 60)
    print(f"✅ EXTRACCIÓN COMPLETADA")
    print(f"📊 TOTALES EXTRAÍDOS: {total_extracted} registros")
    print("=" * 60)
    
    # Guardar datos en XCom para la siguiente tarea
    return {
        'data': all_normas_data,
        'total_records': total_extracted
    }


def task_validation(**context):
    """
    Tarea de Validación: Valida los datos extraídos según las reglas configuradas.
    """
    print("=== INICIANDO TAREA DE VALIDACIÓN ===")
    
    # Obtener datos de la tarea anterior
    ti = context['ti']
    extraction_result = ti.xcom_pull(task_ids='extraction')
    
    if not extraction_result or extraction_result.get('total_records', 0) == 0:
        print("No hay datos para validar")
        return {
            'data': [],
            'total_records': 0,
            'valid_records': 0,
            'discarded_records': 0
        }
    
    all_normas_data = extraction_result.get('data', [])
    
    if not all_normas_data:
        print("Lista de datos vacía")
        return {
            'data': [],
            'total_records': 0,
            'valid_records': 0,
            'discarded_records': 0
        }
    
    # Crear DataFrame
    df_normas = pd.DataFrame(all_normas_data)
    print(f"Validando {len(df_normas)} registros...")
    
    # Validar datos
    try:
        validator = DataValidator()
        df_validated, validation_stats = validator.validate_dataframe(df_normas, verbose=True)
        
        print("=" * 60)
        print(f"✅ VALIDACIÓN COMPLETADA")
        print(f"📊 REGISTROS ORIGINALES: {validation_stats['total_records']}")
        print(f"✅ REGISTROS VÁLIDOS: {validation_stats['valid_records']}")
        print(f"❌ DESCARTES POR VALIDACIÓN: {validation_stats['discarded_records']}")
        if validation_stats.get('field_errors'):
            print(f"⚠️  ERRORES POR CAMPO: {validation_stats['field_errors']}")
        print("=" * 60)
        
        # Convertir DataFrame validado a lista de diccionarios para XCom
        validated_data = df_validated.to_dict('records') if not df_validated.empty else []
        
        return {
            'data': validated_data,
            'total_records': validation_stats['total_records'],
            'valid_records': validation_stats['valid_records'],
            'discarded_records': validation_stats['discarded_records'],
            'validation_stats': validation_stats
        }
        
    except Exception as e:
        print(f"Error en validación: {e}")
        import traceback
        print(traceback.format_exc())
        # En caso de error, continuar con los datos sin validar
        print("Continuando con datos sin validar debido a error...")
        validated_data = df_normas.to_dict('records')
        return {
            'data': validated_data,
            'total_records': len(df_normas),
            'valid_records': len(df_normas),
            'discarded_records': 0,
            'validation_error': str(e)
        }


def task_writing(**context):
    """
    Tarea de Escritura: Escribe los datos validados en la base de datos.
    
    Esta tarea es IDEMPOTENTE: puede ejecutarse múltiples veces sin crear duplicados.
    La función insert_new_records() implementa la lógica de detección de duplicados
    usando los criterios: title + created_at + external_link + entity.
    
    Si se ejecuta el DAG múltiples veces con los mismos datos, solo se insertarán
    los registros nuevos, evitando duplicados automáticamente.
    """
    print("=== INICIANDO TAREA DE ESCRITURA ===")
    
    # Obtener datos de la tarea anterior
    ti = context['ti']
    validation_result = ti.xcom_pull(task_ids='validation')
    
    if not validation_result or validation_result.get('valid_records', 0) == 0:
        print("No hay datos válidos para escribir")
        return {
            'records_inserted': 0,
            'message': 'No hay datos válidos para insertar'
        }
    
    validated_data = validation_result.get('data', [])
    
    if not validated_data:
        print("Lista de datos validados vacía")
        return {
            'records_inserted': 0,
            'message': 'Lista de datos validados vacía'
        }
    
    # Crear DataFrame
    df_validated = pd.DataFrame(validated_data)
    print(f"Escribiendo {len(df_validated)} registros en la base de datos...")
    
    # Conectar a la base de datos
    # Usar la misma base de datos Postgres de Airflow
    db_manager = DatabaseManager()
    
    # Configurar conexión usando variables de entorno de Airflow
    # Por defecto, Airflow usa: postgres/airflow/airflow
    connection_params = {
        'DB_HOST': os.environ.get('DB_HOST', 'postgres'),
        'DB_PORT': os.environ.get('DB_PORT', '5432'),
        'DB_NAME': os.environ.get('DB_NAME', 'airflow'),
        'DB_USERNAME': os.environ.get('DB_USERNAME', 'airflow'),
        'DB_PASSWORD': os.environ.get('DB_PASSWORD', 'airflow')
    }
    
    if not db_manager.connect(connection_params=connection_params):
        error_msg = 'Error de conexión a la base de datos'
        print(error_msg)
        return {
            'records_inserted': 0,
            'message': error_msg,
            'success': False
        }
    
    try:
        # Insertar registros
        inserted_count, status_message = insert_new_records(
            db_manager, 
            df_validated, 
            ENTITY_VALUE
        )
        
        print("=" * 60)
        print(f"✅ ESCRITURA COMPLETADA")
        print(f"📝 FILAS INSERTADAS: {inserted_count}")
        print(f"📋 Detalles: {status_message}")
        print("=" * 60)
        
        return {
            'records_inserted': inserted_count,
            'message': status_message,
            'success': True
        }
        
    except Exception as e:
        error_msg = f"Error en escritura: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return {
            'records_inserted': 0,
            'message': error_msg,
            'success': False
        }
        
    finally:
        db_manager.close()


# Definición de las tareas
extraction_task = PythonOperator(
    task_id='extraction',
    python_callable=task_extraction,
    dag=dag,
)

validation_task = PythonOperator(
    task_id='validation',
    python_callable=task_validation,
    dag=dag,
)

writing_task = PythonOperator(
    task_id='writing',
    python_callable=task_writing,
    dag=dag,
)

# Definir dependencias: Extracción → Validación → Escritura
extraction_task >> validation_task >> writing_task

