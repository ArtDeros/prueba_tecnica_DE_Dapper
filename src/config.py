"""
Módulo de Configuración
Contiene constantes y configuraciones compartidas entre módulos.
"""
import os

# Constantes para el scraping
ENTITY_VALUE = 'Agencia Nacional de Infraestructura'
FIXED_CLASSIFICATION_ID = 13

# Configuración de AWS Secrets Manager
SECRET_NAME = os.environ.get("SECRET_NAME", "Test")
REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")

