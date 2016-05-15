from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import generics
from dictionary.models import SemanticClass
import api.serializers as serializers


class SemanticClassesAPI(generics.ListCreateAPIView):
    queryset = SemanticClass.objects.all()
    serializer_class = serializers.SemanticClassSerializer


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'semantic_classes_api': reverse('semantic_classes_api', request=request, format=format),
    })
