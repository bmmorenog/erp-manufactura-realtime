import os
import json
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SPREADSHEET_ID = '1X12FJ3KCDrTthsHFulKMujU8TODxHT6k3nP3XBvrEt8'
    CO_SHEET_RANGE = 'CO!A:P'  # Extended to include LAT/LNG columns (N and O)
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        credentials_path = os.path.join(settings.BASE_DIR, 'google_credentials.json')
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                "Google credentials file not found. "
                "Please add google_credentials.json to project root."
            )
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES
        )
        
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def get_operational_centers_data(self) -> List[Dict[str, Any]]:
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEET_ID,
                range=self.CO_SHEET_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in Google Sheets")
                return []
            
            headers = values[0]
            data_rows = values[1:]
            
            logger.info(f"Headers found: {headers}")
            
            field_mapping = {
                'CO': 'code',
                'NOMBRE CO': 'name',
                'TIPO': 'center_type',
                'REGIONAL': 'regional',
                'CIUDAD': 'city',
                'OPERACION': 'operation_type',
                'STATUS': 'status',
                'CAMARAS': 'cameras',
                'DIRECCIÓN': 'address',
                'HORARIO RTM': 'rtm_schedule',
                'HORARIO A+C': 'ac_schedule',
                'SEDE RTM': 'rtm_reference',
                'SUCURSAL': 'branch_reference',
                'SEDE': 'headquarters_reference',
                'LAT': 'latitude',
                'LNG': 'longitude'
            }
            
            operational_centers = []
            
            for row in data_rows:
                while len(row) < len(headers):
                    row.append('')
                
                center_data = {}
                for i, header in enumerate(headers):
                    if header in field_mapping:
                        field_name = field_mapping[header]
                        value = row[i].strip() if row[i] else None
                        
                        # Handle numeric fields (LAT/LNG)
                        if field_name in ['latitude', 'longitude'] and value:
                            try:
                                value = float(value)
                                logger.info(f"Converted {field_name} for {center_data.get('code', 'unknown')}: {value}")
                            except ValueError:
                                logger.warning(f"Invalid {field_name} value: {value}")
                                value = None
                        
                        if value == '':
                            value = None
                            
                        center_data[field_name] = value
                
                if center_data.get('code') and center_data.get('name'):
                    operational_centers.append(center_data)
            
            logger.info(f"Successfully processed {len(operational_centers)} operational centers")
            return operational_centers
            
        except Exception as error:
            logger.error(f"Error fetching Google Sheets data: {error}")
            raise
    
    def validate_connection(self) -> bool:
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.SPREADSHEET_ID
            ).execute()
            logger.info(f"Connected to spreadsheet: {result.get('properties', {}).get('title', 'Unknown')}")
            return True
        except Exception as error:
            logger.error(f"Connection validation failed: {error}")
            return False
