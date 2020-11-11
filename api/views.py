from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from .models import Event
from django.db.models.functions import Trunc
from django.db.models import Min, Max, Avg, F
from rest_framework import status
from datetime import datetime


class Tracking(APIView):

    def post(self, request):
        serializer = serializers.EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Aggregation(APIView):

    def get(self, request, namespace, event_name):
        events = Event.objects.filter(name=event_name, namespace=namespace)
        granularity = request.query_params.get('granularity', 'none')
        aggregation_type = request.query_params.get('aggregationType', None)
        ts_min = request.query_params.get('tsMin', None)
        ts_max = request.query_params.get('tsMax', None)
        if ts_min is not None and ts_max is not None:
            events = events.filter(timestamp__gte=datetime.fromtimestamp(int(ts_min)),
                                   timestamp__lte=datetime.fromtimestamp(int(ts_max)))

        # day was not in requirements, but definitely makes sense imho
        if granularity in ['minute', 'hour', 'day', 'week', 'month', 'year']:
            events = events.annotate(granularity_time=Trunc('timestamp', granularity))
        else:
            events = events.annotate(granularity_time=F('timestamp'))

        if aggregation_type == 'min':
            aggregation_method = Min
        elif aggregation_type == 'max':
            aggregation_method = Max
        elif aggregation_type == 'avg':
            aggregation_method = Avg
        else:
            # Default aggregation method
            aggregation_method = Avg

        events = events.values('granularity_time')\
            .annotate(value=aggregation_method('value'))\
            .annotate(aggregatedTimestamp=Min('timestamp'))
        return Response(events.values('aggregatedTimestamp', 'value'))
