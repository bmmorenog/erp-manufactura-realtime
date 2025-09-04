from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class OperationalCenter(models.Model):
    # Primary Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="CO code")
    name = models.CharField(max_length=200, help_text="NOMBRE CO")
    
    # Cross-Reference Fields
    branch_reference = models.CharField(max_length=100, blank=True, null=True)
    headquarters_reference = models.CharField(max_length=100, blank=True, null=True)
    rtm_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Location & Classification
    center_type = models.CharField(max_length=100)
    regional = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    
    # Operational Data
    operation_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='ACTIVO')
    cameras = models.CharField(max_length=200, blank=True, null=True)
    
    # Dual Schedule System
    rtm_schedule = models.TextField(blank=True, null=True)
    ac_schedule = models.TextField(blank=True, null=True)
    
    # Geographic Coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'operational_centers'
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            return {'lat': float(self.latitude), 'lng': float(self.longitude)}
        return None

    # Google Places data
    google_place_id = models.CharField(max_length=200, blank=True, null=True)
    google_rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    google_photo_url = models.URLField(blank=True, null=True)
    google_phone = models.CharField(max_length=50, blank=True, null=True)
    google_website = models.URLField(blank=True, null=True)
    google_reviews_count = models.IntegerField(blank=True, null=True)
    google_last_updated = models.DateTimeField(blank=True, null=True)

    # Google Places data
    google_place_id = models.CharField(max_length=200, blank=True, null=True)
    google_rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    google_photo_url = models.URLField(blank=True, null=True)
    google_phone = models.CharField(max_length=50, blank=True, null=True)
    google_website = models.URLField(blank=True, null=True)
    google_reviews_count = models.IntegerField(blank=True, null=True)
    google_last_updated = models.DateTimeField(blank=True, null=True)
