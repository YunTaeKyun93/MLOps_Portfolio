from django.shortcuts import render
from rest_framework import viewsets
from directors.models import Director
from directors.serializers import DirectorSerializer

# Create your views here.

class DirectorViewSet(viewsets.ModelViewSet):
  queryset = Director.objects.all()
  serializer_class = DirectorSerializer
