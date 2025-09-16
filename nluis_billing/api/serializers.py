from rest_framework import serializers

from nluis_billing.models import (
    Fee
)


class FeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ['id', 'name', 'gfs_code', 'project_type_name',
                  'currency_name', 'payment_option', 'price']
