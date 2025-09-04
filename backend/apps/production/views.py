from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.management import call_command
from django.utils import timezone
from .models import OperationalCenter
from .serializers import OperationalCenterSerializer, OperationalCenterMapSerializer
import io
import sys

class OperationalCenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationalCenter.objects.all()
    serializer_class = OperationalCenterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['center_type', 'regional', 'city', 'status']
    search_fields = ['code', 'name', 'city', 'address']
    ordering_fields = ['code', 'name', 'city', 'created_at']
    ordering = ['code']

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        centers = self.filter_queryset(self.get_queryset())
        serializer = OperationalCenterMapSerializer(centers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        stats = {
            'total_centers': queryset.count(),
            'by_regional': {},
            'by_center_type': {},
            'by_status': {}
        }
        
        for center in queryset:
            regional = center.regional
            if regional not in stats['by_regional']:
                stats['by_regional'][regional] = 0
            stats['by_regional'][regional] += 1
            
            center_type = center.center_type or 'Unknown'
            if center_type not in stats['by_center_type']:
                stats['by_center_type'][center_type] = 0
            stats['by_center_type'][center_type] += 1
            
            status = center.status or 'Unknown'
            if status not in stats['by_status']:
                stats['by_status'][status] = 0
            stats['by_status'][status] += 1
        
        return Response(stats)

    @action(detail=False, methods=['post'])
    def sync_from_sheets(self, request):
        """Sync operational centers from Google Sheets"""
        try:
            # Capture command output
            out = io.StringIO()
            
            # Run the sync command
            call_command('sync_operational_centers', stdout=out)
            
            # Get the output
            output = out.getvalue()
            
            # Get updated stats
            total_centers = OperationalCenter.objects.count()
            last_sync = timezone.now()
            
            return Response({
                'success': True,
                'message': 'Sync completed successfully',
                'total_centers': total_centers,
                'last_sync': last_sync,
                'details': output
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
