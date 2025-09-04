from rest_framework import serializers
from .models import OperationalCenter

class OperationalCenterSerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField()
    cross_references = serializers.ReadOnlyField(source='get_cross_references')
    
    class Meta:
        model = OperationalCenter
        fields = [
            'id', 'code', 'name', 'center_type', 'regional', 'city', 'address',
            'operation_type', 'status', 'cameras', 'rtm_schedule', 'ac_schedule',
            'branch_reference', 'headquarters_reference', 'rtm_reference',
            'latitude', 'longitude', 'coordinates', 'created_at', 'updated_at',
            'last_sync_at', 'cross_references'
        ]

class OperationalCenterMapSerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = OperationalCenter
        fields = [
            'id', 'code', 'name', 'center_type', 'city', 'regional',
            'status', 'coordinates', 'latitude', 'longitude'
        ]
