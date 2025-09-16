from rest_framework import serializers

from nluis_reports.models import (
    Report,

)


class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'name', 'endpoint', 'filter']
