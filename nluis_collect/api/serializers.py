from rest_framework import serializers
from nluis_collect.models import FormAnswer


class FormAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = ['id', 'claim_no', 'responce']


class QuestionnaireFormListSerializer(serializers.Serializer):

    def get_data(self, obj):
        if obj:
            return obj
        return None
