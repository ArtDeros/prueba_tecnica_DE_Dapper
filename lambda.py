"""
Lambda handler refactorizado para usar módulos de extracción, validación y persistencia.
Mantiene compatibilidad con la función lambda_handler original.
Flujo: Extracción → Validación → Escritura
"""
import json
import pandas as pd
from src.extraction import (
    scrape_multiple_pages,
    check_for_new_content,
    ENTITY_VALUE
)
from src.validation import DataValidator
from src.persistence import (
    DatabaseManager,
    insert_new_records
)


def lambda_handler(event, context):
    """
    AWS Lambda handler function para el scraping de normativas ANI.
    Modificado para procesar las páginas más recientes (0-8) y detectar contenido nuevo.
    """
    try:
        # Obtener parámetros del evento
        num_pages_to_scrape = event.get('num_pages_to_scrape', 9) if event else 9
        force_scrape = event.get('force_scrape', False) if event else False
        
        print(f"Iniciando scraping de ANI - Páginas a procesar: {num_pages_to_scrape}")
        
        # Operaciones de base de datos para verificación
        db_manager = DatabaseManager()
        db_connected = db_manager.connect()
        
        # Verificar si hay contenido nuevo (a menos que se fuerce el scraping)
        if not force_scrape and db_connected:
            has_new_content = check_for_new_content(
                min(3, num_pages_to_scrape),
                db_manager=db_manager
            )
            if not has_new_content:
                db_manager.close()
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'No se detectó contenido nuevo. Scraping omitido.',
                        'records_scraped': 0,
                        'records_inserted': 0,
                        'content_check': 'no_new_content',
                        'success': True
                    })
                }
        
        if db_connected:
            db_manager.close()
        
        # Procesar las páginas más recientes (0 a num_pages_to_scrape-1)
        start_page = 0
        end_page = num_pages_to_scrape - 1
        
        print(f"Procesando páginas más recientes desde {start_page} hasta {end_page}")
        
        # Proceso principal de scraping usando el módulo de extracción
        all_normas_data = scrape_multiple_pages(
            num_pages=num_pages_to_scrape,
            start_page=start_page,
            verbose=True
        )
        
        if not all_normas_data:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No se encontraron datos válidos durante el scraping',
                    'records_scraped': 0,
                    'records_inserted': 0,
                    'pages_processed': f"{start_page}-{end_page}",
                    'success': True
                })
            }
        
        # Guardar cantidad original para estadísticas
        total_scraped = len(all_normas_data)
        
        # Crear DataFrame
        df_normas = pd.DataFrame(all_normas_data)
        print(f"Total de registros extraídos: {total_scraped}")
        
        # ETAPA DE VALIDACIÓN
        print("\n=== INICIANDO ETAPA DE VALIDACIÓN ===")
        validation_stats = None
        try:
            validator = DataValidator()
            df_validated, validation_stats = validator.validate_dataframe(df_normas, verbose=True)
            
            print(f"Registros después de validación: {len(df_validated)}")
            
            if df_validated.empty:
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Todos los registros fueron descartados durante la validación',
                        'records_scraped': len(df_normas),
                        'records_validated': 0,
                        'records_inserted': 0,
                        'validation_stats': validation_stats,
                        'pages_processed': f"{start_page}-{end_page}",
                        'success': True
                    })
                }
            
            # Usar el DataFrame validado para la escritura
            df_normas = df_validated
            
        except Exception as validation_error:
            print(f"Error en validación: {validation_error}")
            import traceback
            print(traceback.format_exc())
            # Continuar sin validación si hay error (comportamiento de fallback)
            print("Continuando sin validación debido a error...")
        
        # Operaciones de base de datos usando el módulo de persistencia
        db_manager = DatabaseManager()
        if not db_manager.connect():
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Error de conexión a la base de datos',
                    'success': False
                })
            }
        
        try:
            # Insertar nuevos registros usando el módulo de persistencia
            inserted_count, status_message = insert_new_records(db_manager, df_normas, ENTITY_VALUE)
            
            response_body = {
                'message': status_message,
                'records_scraped': total_scraped,
                'records_validated': len(df_normas),
                'records_inserted': inserted_count,
                'pages_processed': f"{start_page}-{end_page}",
                'content_check': 'new_content_found' if not force_scrape else 'forced_scrape',
                'success': True
            }
            
            # Agregar estadísticas de validación si están disponibles
            if validation_stats:
                response_body['validation_stats'] = validation_stats
            
            response = {
                'statusCode': 200,
                'body': json.dumps(response_body)
            }
            
            print(f"Operación completada: {status_message}")
            return response
            
        finally:
            db_manager.close()
        
    except Exception as e:
        error_message = f"Error en la ejecución de Lambda: {str(e)}"
        print(error_message)
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': error_message,
                'success': False
            })
        }


# Para pruebas locales
if __name__ == "__main__":
    # Evento de prueba
    test_event = {
        'num_pages_to_scrape': 3,
        'force_scrape': True
    }
    
    # Contexto de prueba (vacío para pruebas locales)
    test_context = {}
    
    # Ejecutar función
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))
