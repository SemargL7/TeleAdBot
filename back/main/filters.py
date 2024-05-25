import django_filters
from .models import Order, OrderStatus, Advertisement


class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateTimeFromToRangeFilter()
    expired_at = django_filters.DateTimeFromToRangeFilter()
    payment_time = django_filters.DateTimeFromToRangeFilter()
    finished_at = django_filters.DateTimeFromToRangeFilter()
    order_status = django_filters.ChoiceFilter(choices=OrderStatus.objects.all().values_list('order_status', 'order_status_name'))

    class Meta:
        model = Order
        fields = ['created_at', 'expired_at', 'payment_time', 'finished_at', 'order_status']


class AdvertisementFilter(django_filters.FilterSet):
    chat_type = django_filters.CharFilter(field_name='chat__chat_type__chat_type_name', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Advertisement
        fields = ['chat_type', 'description']