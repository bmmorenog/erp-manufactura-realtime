import requests
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GooglePlacesService:
    def __init__(self):
        self.api_key = "AIzaSyCpVXQnjZDBOqIKn5_4jlZAHWplgDl-9fI"
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_place(self, name: str, address: str, lat: float, lng: float) -> Optional[str]:
        """Search for a place and return place_id"""
        try:
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': f"{name} {address}",
                'location': f"{lat},{lng}",
                'radius': 100,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('results'):
                return data['results'][0]['place_id']
            return None
            
        except Exception as e:
            logger.error(f"Error searching place: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed place information"""
        try:
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,photos,formatted_phone_number,website,user_ratings_total,reviews',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('result'):
                result = data['result']
                return {
                    'rating': result.get('rating'),
                    'phone': result.get('formatted_phone_number'),
                    'website': result.get('website'),
                    'reviews_count': result.get('user_ratings_total'),
                    'photo_url': self.get_photo_url(result.get('photos', []))
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None
    
    def get_photo_url(self, photos: list, max_width: int = 400) -> Optional[str]:
        """Get photo URL from photos array"""
        if photos:
            photo_reference = photos[0]['photo_reference']
            return f"{self.base_url}/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
        return None
