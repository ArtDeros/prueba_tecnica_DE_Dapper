"""
Módulo de Validación
Valida los datos extraídos según reglas configurables.
- Si un campo no cumple, se deja NULL/vacío
- Si un campo obligatorio no cumple, se descarta la fila completa
"""
import re
import yaml
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import pandas as pd


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class DataValidator:
    """
    Validador de datos basado en reglas configurables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el validador con las reglas de configuración.
        
        Args:
            config_path: Ruta al archivo YAML de configuración. 
                        Si es None, busca en configs/validation_rules.yaml
        """
        if config_path is None:
            # Buscar en diferentes ubicaciones posibles
            possible_paths = [
                'configs/validation_rules.yaml',
                './configs/validation_rules.yaml',
                os.path.join(os.path.dirname(__file__), '..', 'configs', 'validation_rules.yaml')
            ]
            
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                raise FileNotFoundError(
                    f"No se encontró el archivo de configuración. "
                    f"Buscado en: {possible_paths}"
                )
        
        self.config = self._load_config(config_path)
        self.required_fields = self.config.get('fields', {}).get('required_fields', [])
        self.field_rules = self.config.get('fields', {})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Carga la configuración desde un archivo YAML.
        
        Args:
            config_path: Ruta al archivo YAML
            
        Returns:
            Dict con la configuración cargada
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise ValidationError(f"Error cargando configuración desde {config_path}: {e}")
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Valida el tipo de dato de un valor.
        
        Args:
            value: Valor a validar
            expected_type: Tipo esperado (str, int, bool, etc.)
            
        Returns:
            True si el tipo es correcto, False en caso contrario
        """
        if value is None:
            return False
        
        type_mapping = {
            'str': str,
            'int': int,
            'bool': bool,
            'float': float
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Tipo no reconocido, no validar
        
        return isinstance(value, expected_python_type)
    
    def _validate_regex(self, value: Any, pattern: str) -> bool:
        """
        Valida un valor contra una expresión regular.
        
        Args:
            value: Valor a validar
            pattern: Patrón regex
            
        Returns:
            True si coincide, False en caso contrario
        """
        if value is None:
            return False
        
        try:
            return bool(re.match(pattern, str(value)))
        except Exception:
            return False
    
    def _validate_length(self, value: Any, max_length: Optional[int] = None, 
                        min_length: Optional[int] = None) -> bool:
        """
        Valida la longitud de un valor.
        
        Args:
            value: Valor a validar
            max_length: Longitud máxima
            min_length: Longitud mínima
            
        Returns:
            True si cumple con las restricciones de longitud
        """
        if value is None:
            return False
        
        str_value = str(value)
        length = len(str_value)
        
        if max_length is not None and length > max_length:
            return False
        
        if min_length is not None and length < min_length:
            return False
        
        return True
    
    def _validate_range(self, value: Any, min_value: Optional[float] = None,
                       max_value: Optional[float] = None) -> bool:
        """
        Valida que un valor numérico esté en un rango.
        
        Args:
            value: Valor a validar
            min_value: Valor mínimo
            max_value: Valor máximo
            
        Returns:
            True si está en el rango, False en caso contrario
        """
        if value is None:
            return False
        
        try:
            num_value = float(value)
            
            if min_value is not None and num_value < min_value:
                return False
            
            if max_value is not None and num_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_allowed_values(self, value: Any, allowed_values: List[Any]) -> bool:
        """
        Valida que un valor esté en una lista de valores permitidos.
        
        Args:
            value: Valor a validar
            allowed_values: Lista de valores permitidos
            
        Returns:
            True si está en la lista, False en caso contrario
        """
        if value is None:
            # None puede estar permitido explícitamente
            return None in allowed_values
        
        return value in allowed_values
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Valida un campo individual según sus reglas.
        
        Args:
            field_name: Nombre del campo
            value: Valor a validar
            
        Returns:
            Tuple (es_válido, mensaje_error)
        """
        # Si el campo no tiene reglas definidas, se acepta
        if field_name not in self.field_rules:
            return True, None
        
        rules = self.field_rules[field_name]
        
        # Validar tipo
        if 'type' in rules:
            if not self._validate_type(value, rules['type']):
                return False, f"Tipo incorrecto. Esperado: {rules['type']}, obtenido: {type(value).__name__}"
        
        # Validar regex
        if 'regex' in rules and value is not None:
            if not self._validate_regex(value, rules['regex']):
                return False, f"No cumple con el patrón regex: {rules.get('description', '')}"
        
        # Validar longitud
        if 'max_length' in rules or 'min_length' in rules:
            if not self._validate_length(value, 
                                        max_length=rules.get('max_length'),
                                        min_length=rules.get('min_length')):
                max_len = rules.get('max_length', 'N/A')
                min_len = rules.get('min_length', 'N/A')
                return False, f"Longitud fuera de rango. Min: {min_len}, Max: {max_len}"
        
        # Validar rango (para números)
        if 'min_value' in rules or 'max_value' in rules:
            if not self._validate_range(value,
                                       min_value=rules.get('min_value'),
                                       max_value=rules.get('max_value')):
                min_val = rules.get('min_value', 'N/A')
                max_val = rules.get('max_value', 'N/A')
                return False, f"Valor fuera de rango. Min: {min_val}, Max: {max_val}"
        
        # Validar valores permitidos
        if 'allowed_values' in rules:
            if not self._validate_allowed_values(value, rules['allowed_values']):
                return False, f"Valor no permitido. Permitidos: {rules['allowed_values']}"
        
        return True, None
    
    def validate_record(self, record: Dict[str, Any], verbose: bool = False) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Valida un registro completo.
        
        Args:
            record: Diccionario con los datos del registro
            verbose: Si mostrar mensajes detallados
            
        Returns:
            Tuple (es_válido, registro_validado, errores)
            - es_válido: True si el registro es válido (puede tener campos NULL)
            - registro_validado: Registro con campos inválidos puestos a None
            - errores: Lista de mensajes de error
        """
        validated_record = record.copy()
        errors = []
        field_errors = []
        
        # Primero validar campos obligatorios
        for field_name in self.required_fields:
            value = validated_record.get(field_name)
            is_valid, error_msg = self.validate_field(field_name, value)
            
            if not is_valid:
                field_errors.append(f"{field_name}: {error_msg}")
                if verbose:
                    print(f"Campo obligatorio '{field_name}' inválido: {error_msg}")
        
        # Si algún campo obligatorio falla, descartar la fila completa
        if field_errors:
            errors.extend(field_errors)
            errors.append("Registro descartado: campos obligatorios inválidos")
            return False, None, errors
        
        # Validar todos los campos (no obligatorios pueden quedar NULL)
        for field_name, value in validated_record.items():
            # Saltar campos que no tienen reglas
            if field_name not in self.field_rules:
                continue
            
            is_valid, error_msg = self.validate_field(field_name, value)
            
            if not is_valid:
                # Campo no cumple, ponerlo a None
                validated_record[field_name] = None
                if verbose:
                    print(f"Campo '{field_name}' inválido, establecido a NULL: {error_msg}")
                errors.append(f"{field_name}: {error_msg} (establecido a NULL)")
        
        return True, validated_record, errors
    
    def validate_dataframe(self, df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Valida un DataFrame completo.
        
        Args:
            df: DataFrame con los datos a validar
            verbose: Si mostrar mensajes detallados
            
        Returns:
            Tuple (df_validado, estadísticas)
            - df_validado: DataFrame con registros válidos y campos inválidos en NULL
            - estadísticas: Dict con estadísticas de validación
        """
        if df.empty:
            return df, {
                'total_records': 0,
                'valid_records': 0,
                'discarded_records': 0,
                'field_errors': {}
            }
        
        validated_records = []
        discarded_count = 0
        field_errors = {}
        
        for idx, row in df.iterrows():
            record = row.to_dict()
            is_valid, validated_record, errors = self.validate_record(record, verbose=verbose)
            
            if is_valid:
                validated_records.append(validated_record)
            else:
                discarded_count += 1
                if verbose:
                    print(f"Registro {idx} descartado: {errors}")
                
                # Contar errores por campo
                for error in errors:
                    field_name = error.split(':')[0] if ':' in error else 'unknown'
                    field_errors[field_name] = field_errors.get(field_name, 0) + 1
        
        validated_df = pd.DataFrame(validated_records)
        
        stats = {
            'total_records': len(df),
            'valid_records': len(validated_records),
            'discarded_records': discarded_count,
            'field_errors': field_errors
        }
        
        if verbose:
            print(f"\n=== Estadísticas de Validación ===")
            print(f"Total de registros: {stats['total_records']}")
            print(f"Registros válidos: {stats['valid_records']}")
            print(f"Registros descartados: {stats['discarded_records']}")
            print(f"Errores por campo: {stats['field_errors']}")
            print("=" * 50)
        
        return validated_df, stats

