"""
Módulo de Escritura (Persistencia)
Contiene toda la lógica de conexión a base de datos y escritura de datos.
Soporta tanto AWS Secrets Manager como variables de entorno.
"""
import pandas as pd
import psycopg2
import json
import os
from typing import Dict, Any, Tuple, List, Optional

# Configuración de AWS Secrets Manager (opcional)
SECRET_NAME = os.environ.get("SECRET_NAME", None)
REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")

# Variables de entorno para conexión directa (prioridad sobre Secrets Manager)
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Intentar importar boto3 solo si se necesita
secrets_client = None
if SECRET_NAME:
    try:
        import boto3
        from botocore.exceptions import ClientError
        secrets_client = boto3.client('secretsmanager', region_name=REGION_NAME)
    except ImportError:
        print("boto3 no disponible, usando variables de entorno")


def get_secret():
    """
    Recupera las credenciales de la base de datos de AWS Secrets Manager.
    Solo se usa si SECRET_NAME está configurado.
    """
    if not SECRET_NAME or not secrets_client:
        return None
    
    try:
        get_secret_value_response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None


def get_db_credentials() -> Dict[str, str]:
    """
    Obtiene las credenciales de la base de datos.
    Prioridad: Variables de entorno > Secrets Manager
    
    Returns:
        Dict con las credenciales de conexión
    """
    # Primero intentar variables de entorno
    if all([DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD]):
        return {
            'DB_HOST': DB_HOST,
            'DB_PORT': DB_PORT,
            'DB_NAME': DB_NAME,
            'DB_USERNAME': DB_USERNAME,
            'DB_PASSWORD': DB_PASSWORD
        }
    
    # Si no hay variables de entorno, intentar Secrets Manager
    if SECRET_NAME:
        secrets = get_secret()
        if secrets:
            return secrets
    
    # Si no hay ninguna opción, usar valores por defecto de Airflow
    return {
        'DB_HOST': os.environ.get("DB_HOST", "postgres"),
        'DB_PORT': os.environ.get("DB_PORT", "5432"),
        'DB_NAME': os.environ.get("DB_NAME", "airflow"),
        'DB_USERNAME': os.environ.get("DB_USERNAME", "airflow"),
        'DB_PASSWORD': os.environ.get("DB_PASSWORD", "airflow")
    }


class DatabaseManager:
    """
    Clase para manejar la conexión a la base de datos y realizar operaciones de inserción de datos.
    """
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, connection_params: Optional[Dict[str, str]] = None):
        """
        Conecta a la base de datos.
        
        Args:
            connection_params: Parámetros de conexión opcionales. 
                            Si no se proporcionan, se obtienen automáticamente.
        """
        try:
            if connection_params:
                credentials = connection_params
            else:
                credentials = get_db_credentials()
            
            self.connection = psycopg2.connect(
                dbname=credentials['DB_NAME'],
                user=credentials['DB_USERNAME'],
                password=credentials['DB_PASSWORD'],
                host=credentials['DB_HOST'],
                port=credentials['DB_PORT']
            )
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        if not self.cursor:
            raise Exception("Database not connected")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def bulk_insert(self, df, table_name):
        if not self.connection or not self.cursor:
            raise Exception("Database not connected")
        
        try:
            df = df.astype(object).where(pd.notnull(df), None)
            columns_for_sql = ", ".join([f'"{col}"' for col in df.columns])
            placeholders = ", ".join(["%s"] * len(df.columns))
            
            insert_query = f"INSERT INTO {table_name} ({columns_for_sql}) VALUES ({placeholders})"
            records_to_insert = [tuple(x) for x in df.values]
            
            self.cursor.executemany(insert_query, records_to_insert)
            self.connection.commit()
            return len(df)
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Error inserting into {table_name}: {str(e)}")


def insert_regulations_component(db_manager, new_ids):
    """
    Inserta los componentes de las regulaciones.
    
    Nota: Esta función no valida duplicados en la tabla regulations_component.
    Si se necesita idempotencia para componentes, se debe implementar validación
    similar a insert_new_records().
    
    Args:
        db_manager: Instancia de DatabaseManager conectada a la BD
        new_ids: Lista de IDs de regulaciones para las que insertar componentes
    
    Returns:
        Tuple (inserted_count, status_message)
    """
    if not new_ids:
        return 0, "No new regulation IDs provided"

    try:
        id_rows = pd.DataFrame(new_ids, columns=['regulations_id'])
        id_rows['components_id'] = 7
        
        inserted_count = db_manager.bulk_insert(id_rows, 'regulations_component')
        return inserted_count, f"Successfully inserted {inserted_count} regulation components"
        
    except Exception as e:
        return 0, f"Error inserting regulation components: {str(e)}"


def insert_new_records(db_manager, df, entity):
    """
    Inserta nuevos registros en la base de datos evitando duplicados.
    Esta función es IDEMPOTENTE: puede ejecutarse múltiples veces con los mismos
    datos sin crear duplicados.
    
    Criterios de duplicados (según lógica existente):
    - Un registro se considera duplicado si tiene la misma combinación de:
      * title (título)
      * created_at (fecha de creación)
      * external_link (enlace externo)
      * entity (entidad)
    
    La función:
    1. Consulta registros existentes en la BD para la entidad especificada
    2. Compara los nuevos registros con los existentes usando una clave única
    3. Filtra duplicados antes de insertar
    4. También remueve duplicados internos del DataFrame
    5. Maneja errores de duplicados en caso de que algunos se escapen
    
    Args:
        db_manager: Instancia de DatabaseManager conectada a la BD
        df: DataFrame con los registros a insertar
        entity: Nombre de la entidad (ej: 'Agencia Nacional de Infraestructura')
    
    Returns:
        Tuple (inserted_count, status_message):
        - inserted_count: Número de registros insertados
        - status_message: Mensaje con estadísticas del proceso
    
    Optimizada para velocidad y precisión.
    """
    regulations_table_name = 'regulations'
    
    try:
        # 1. OBTENER REGISTROS EXISTENTES INCLUYENDO EXTERNAL_LINK
        query = """
            SELECT title, created_at, entity, COALESCE(external_link, '') as external_link 
            FROM {} 
            WHERE entity = %s
        """.format(regulations_table_name)
        
        existing_records = db_manager.execute_query(query, (entity,))
        
        if not existing_records:
            db_df = pd.DataFrame(columns=['title', 'created_at', 'entity', 'external_link'])
        else:
            db_df = pd.DataFrame(existing_records, columns=['title', 'created_at', 'entity', 'external_link'])
        
        print(f"Registros existentes en BD para {entity}: {len(db_df)}")
        
        # 2. PREPARAR DATAFRAME DE LA ENTIDAD
        entity_df = df[df['entity'] == entity].copy()
        
        if entity_df.empty:
            return 0, f"No records found for entity {entity}"
        
        print(f"Registros a procesar para {entity}: {len(entity_df)}")
        
        # 3. NORMALIZAR DATOS PARA COMPARACIÓN CONSISTENTE
        # Normalizar created_at a string
        if not db_df.empty:
            db_df['created_at'] = db_df['created_at'].astype(str)
            db_df['external_link'] = db_df['external_link'].fillna('').astype(str)
            db_df['title'] = db_df['title'].astype(str).str.strip()
        
        entity_df['created_at'] = entity_df['created_at'].astype(str)
        entity_df['external_link'] = entity_df['external_link'].fillna('').astype(str)
        entity_df['title'] = entity_df['title'].astype(str).str.strip()
        
        # 4. IDENTIFICAR DUPLICADOS DE MANERA OPTIMIZADA
        print("=== INICIANDO VALIDACIÓN DE DUPLICADOS OPTIMIZADA ===")
        
        if db_df.empty:
            # Si no hay registros existentes, todos son nuevos
            new_records = entity_df.copy()
            duplicates_found = 0
            print("No hay registros existentes, todos son nuevos")
        else:
            # Crear claves únicas para comparación super rápida
            entity_df['unique_key'] = (
                entity_df['title'] + '|' + 
                entity_df['created_at'] + '|' + 
                entity_df['external_link']
            )
            
            db_df['unique_key'] = (
                db_df['title'] + '|' + 
                db_df['created_at'] + '|' + 
                db_df['external_link']
            )
            
            # Usar set para comparación O(1) - súper rápido
            existing_keys = set(db_df['unique_key'])
            entity_df['is_duplicate'] = entity_df['unique_key'].isin(existing_keys)
            
            new_records = entity_df[~entity_df['is_duplicate']].copy()
            duplicates_found = len(entity_df) - len(new_records)
            
            # Log para debugging
            if duplicates_found > 0:
                print(f"Duplicados encontrados: {duplicates_found}")
                duplicate_records = entity_df[entity_df['is_duplicate']]
                print("Ejemplos de duplicados:")
                for idx, row in duplicate_records.head(3).iterrows():
                    print(f"  - {row['title'][:50]}... | {row['created_at']}")
        
        # 5. REMOVER DUPLICADOS INTERNOS DEL DATAFRAME
        print(f"Antes de remover duplicados internos: {len(new_records)}")
        new_records = new_records.drop_duplicates(
            subset=['title', 'created_at', 'external_link'], 
            keep='first'
        )
        internal_duplicates = len(entity_df) - duplicates_found - len(new_records)
        if internal_duplicates > 0:
            print(f"Duplicados internos removidos: {internal_duplicates}")
        
        print(f"Después de remover duplicados internos: {len(new_records)}")
        print(f"=== DUPLICADOS IDENTIFICADOS: {duplicates_found + internal_duplicates} ===")
        
        if new_records.empty:
            return 0, f"No new records found for entity {entity} after duplicate validation"
        
        # 6. LIMPIAR DATAFRAME ANTES DE INSERTAR
        # Remover columnas auxiliares
        columns_to_drop = ['unique_key', 'is_duplicate']
        for col in columns_to_drop:
            if col in new_records.columns:
                new_records = new_records.drop(columns=[col])
        
        print(f"Registros finales a insertar: {len(new_records)}")
        
        # 7. INSERTAR NUEVOS REGISTROS
        try:
            print(f"=== INSERTANDO {len(new_records)} REGISTROS ===")
            
            total_rows_processed = db_manager.bulk_insert(new_records, regulations_table_name)
            
            if total_rows_processed == 0:
                return 0, f"No records were actually inserted for entity {entity}"
            
            print(f"Registros insertados exitosamente: {total_rows_processed}")
            
        except Exception as insert_error:
            print(f"Error en inserción: {insert_error}")
            # Si es error de duplicados, algunos se escaparon
            if "duplicate" in str(insert_error).lower() or "unique" in str(insert_error).lower():
                print("Error de duplicados detectado - algunos registros ya existían")
                return 0, f"Some records for entity {entity} were duplicates and skipped"
            else:
                raise insert_error
        
        # 8. OBTENER IDS DE REGISTROS INSERTADOS - MÉTODO OPTIMIZADO
        print("=== OBTENIENDO IDS DE REGISTROS INSERTADOS ===")
        
        # Método simple y eficiente - obtener los últimos N IDs
        new_ids_query = f"""
            SELECT id FROM {regulations_table_name}
            WHERE entity = %s 
            ORDER BY id DESC
            LIMIT %s
        """
        
        new_ids_result = db_manager.execute_query(
            new_ids_query, 
            (entity, total_rows_processed)
        )
        new_ids = [row[0] for row in new_ids_result]
        
        print(f"IDs obtenidos: {len(new_ids)}")
        
        # 9. INSERTAR COMPONENTES DE REGULACIÓN
        inserted_count_comp = 0
        component_message = ""
        
        if new_ids:
            try:
                inserted_count_comp, component_message = insert_regulations_component(db_manager, new_ids)
                print(f"Componentes: {component_message}")
            except Exception as comp_error:
                print(f"Error insertando componentes: {comp_error}")
                component_message = f"Error inserting components: {str(comp_error)}"
        
        # 10. MENSAJE FINAL CON ESTADÍSTICAS DETALLADAS
        total_duplicates = duplicates_found + internal_duplicates
        stats = (
            f"Processed: {len(entity_df)} | "
            f"Existing: {len(db_df)} | "
            f"Duplicates skipped: {total_duplicates} | "
            f"New inserted: {total_rows_processed}"
        )
        
        message = f"Entity {entity}: {stats}. {component_message}"
        print(f"=== RESULTADO FINAL ===")
        print(message)
        print("=" * 50)
        
        return total_rows_processed, message
        
    except Exception as e:
        if hasattr(db_manager, 'connection') and db_manager.connection:
            db_manager.connection.rollback()
        error_msg = f"Error processing entity {entity}: {str(e)}"
        print(f"ERROR CRÍTICO: {error_msg}")
        import traceback
        print(traceback.format_exc())
        return 0, error_msg

