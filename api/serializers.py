from rest_framework import serializers
from dictionary.models import SemanticClass, Sense


class SenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sense
        fields = ('slug', 'xml_id')


class SemanticClassSerializer(serializers.ModelSerializer):
    senses = SenseSerializer(many=True, read_only=True)

    class Meta:
        model = SemanticClass
        fields = ('name', 'slug', 'senses')



