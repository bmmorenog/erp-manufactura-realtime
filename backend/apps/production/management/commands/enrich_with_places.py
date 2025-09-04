from django.core.management.base import BaseCommand
from apps.production.models import OperationalCenter
from apps.production.services.google_places_service import GooglePlacesService
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'Enrich operational centers with Google Places data'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Limit number of centers to process')
    
    def handle(self, *args, **options):
        limit = options['limit']
        places_service = GooglePlacesService()
        
        # Get centers without Google data
        centers = OperationalCenter.objects.filter(
            google_place_id__isnull=True,
            latitude__isnull=False,
            longitude__isnull=False
        )[:limit]
        
        self.stdout.write(f"Processing {centers.count()} centers...")
        
        for center in centers:
            try:
                self.stdout.write(f"Processing {center.code} - {center.name}")
                
                # Search for place
                place_id = places_service.search_place(
                    center.name, 
                    center.address or center.city,
                    float(center.latitude),
                    float(center.longitude)
                )
                
                if place_id:
                    # Get place details
                    details = places_service.get_place_details(place_id)
                    
                    if details:
                        center.google_place_id = place_id
                        center.google_rating = details.get('rating')
                        center.google_photo_url = details.get('photo_url')
                        center.google_phone = details.get('phone')
                        center.google_website = details.get('website')
                        center.google_reviews_count = details.get('reviews_count')
                        center.google_last_updated = timezone.now()
                        center.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Updated {center.code} - Rating: {details.get('rating')}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ No details found for {center.code}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ No place found for {center.code}")
                    )
                
                # Rate limiting - Google Places allows 10 requests per second
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error processing {center.code}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎯 Completed processing {centers.count()} centers")
        )
