import django_filters
from django.utils import timezone
from .models import User
from django.db.models import Q

class UserFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(lookup_expr='iexact')
    gender = django_filters.CharFilter(lookup_expr='iexact')
    keyword = django_filters.CharFilter(method='filter_by_full_name')
    date_of_birth_gte = django_filters.DateFilter(field_name="date_of_birth" or 0000-00-00, lookup_expr="gte")
    date_of_birth_lte = django_filters.DateFilter(field_name="date_of_birth" or timezone.now().date(), lookup_expr="lte")

    class Meta:
        model = User
        fields = []

    @staticmethod
    def filter_by_full_name(queryset, name, value):

        full_name = value.split(" ")
        first_name = full_name[0]
        last_name = full_name[-1] if len(full_name) > 1 else ""

        if first_name and last_name:
            return queryset.filter(
                (Q(first_name__icontains=first_name) &
                Q(last_name__icontains=last_name)) |
                (Q(last_name__icontains=first_name) &
                Q(first_name__icontains=last_name))
            )
        elif first_name:
            return queryset.filter(Q(first_name__icontains=first_name) | Q(last_name__icontains=first_name))
        elif last_name:
            return queryset.filter(Q(last_name__icontains=last_name) | Q(first_name__icontains=last_name))
        else:
            return queryset
