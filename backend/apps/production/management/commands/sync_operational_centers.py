from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.production.models import OperationalCenter
from apps.production.services.google_sheets_service import GoogleSheetsService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manually sync Operational Centers data from Google Sheets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data seems unchanged',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Starting Operational Centers sync from Google Sheets...')
        )
        
        dry_run = options['dry_run']
        force_update = options['force']
        
        try:
            sheets_service = GoogleSheetsService()
            
            if not sheets_service.validate_connection():
                self.stdout.write(
                    self.style.ERROR('❌ Failed to connect to Google Sheets')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS('✅ Connected to Google Sheets successfully')
            )
            
            centers_data = sheets_service.get_operational_centers_data()
            
            if not centers_data:
                self.stdout.write(
                    self.style.WARNING('⚠️ No data found in Google Sheets')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'📊 Found {len(centers_data)} operational centers in sheets')
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('🔍 DRY RUN MODE - Preview only:')
                )
                self._preview_changes(centers_data)
                return
            
            stats = self._sync_centers(centers_data, force_update)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sync completed! '
                    f'Created: {stats["created"]}, '
                    f'Updated: {stats["updated"]}, '
                    f'Skipped: {stats["skipped"]}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Sync failed: {str(e)}')
            )
            logger.error(f"Sync command failed: {e}", exc_info=True)
    
    def _preview_changes(self, centers_data):
        for i, center in enumerate(centers_data[:5]):
            self.stdout.write(f"\n📋 Center {i+1}:")
            self.stdout.write(f"  Code: {center.get('code')}")
            self.stdout.write(f"  Name: {center.get('name')}")
            self.stdout.write(f"  City: {center.get('city')}")
            self.stdout.write(f"  Type: {center.get('center_type')}")
            self.stdout.write(f"  Status: {center.get('status')}")
        
        if len(centers_data) > 5:
            self.stdout.write(f"\n... and {len(centers_data) - 5} more centers")
    
    @transaction.atomic
    def _sync_centers(self, centers_data, force_update=False):
        stats = {'created': 0, 'updated': 0, 'skipped': 0}
        sync_time = timezone.now()
        
        for center_data in centers_data:
            code = center_data.get('code')
            
            if not code:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Skipping center without code: {center_data.get("name", "Unknown")}')
                )
                stats['skipped'] += 1
                continue
            
            try:
                center, created = OperationalCenter.objects.get_or_create(
                    code=code,
                    defaults={**center_data, 'last_sync_at': sync_time}
                )
                
                if created:
                    stats['created'] += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✨ Created: {center.code} - {center.name}')
                    )
                else:
                    needs_update = force_update or self._needs_update(center, center_data)
                    
                    if needs_update:
                        for field, value in center_data.items():
                            if hasattr(center, field):
                                setattr(center, field, value)
                        
                        center.last_sync_at = sync_time
                        center.save()
                        
                        stats['updated'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'🔄 Updated: {center.code} - {center.name}')
                        )
                    else:
                        stats['skipped'] += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error syncing {code}: {str(e)}')
                )
                stats['skipped'] += 1
                continue
        
        return stats
    
    def _needs_update(self, center, new_data):
        for field, new_value in new_data.items():
            if hasattr(center, field):
                current_value = getattr(center, field)
                if current_value != new_value:
                    return True
        return False
