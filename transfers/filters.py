import django_filters
from .models import Transaction
from django.db.models import Q

class TransactionFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(method='filter_by_sender_full_name')
    agent = django_filters.CharFilter(method='filter_by_agent_full_name')
    status = django_filters.CharFilter(lookup_expr='iexact')
    created_at_gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")
    amount_gte = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_lte = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = []

    def filter_by_full_name(self, queryset, name, value):
        # Séparer la valeur entrée par l'utilisateur en prénom et nom de famille
        full_name = value.split(" ")
        first_name = full_name[0]
        last_name = full_name[-1] if len(full_name) > 1 else ""

        # Appliquer le filtrage en fonction des champs prénom et nom de famille
        if first_name and last_name:
            return queryset.filter(
                (Q(**{f"{name}__first_name__icontains": first_name}) &
                 Q(**{f"{name}__last_name__icontains": last_name})) |
                (Q(**{f"{name}__last_name__icontains": first_name}) &
                 Q(**{f"{name}__first_name__icontains": last_name}))
            )
        elif first_name:
            return queryset.filter(Q(**{f"{name}__first_name__icontains": first_name}) |
                                   Q(**{f"{name}__last_name__icontains": first_name}))
        elif last_name:
            return queryset.filter(Q(**{f"{name}__last_name__icontains": last_name}) |
                                   Q(**{f"{name}__first_name__icontains": last_name}))
        else:
            return queryset

    def filter_by_sender_full_name(self, queryset, name, value):
        return self.filter_by_full_name(queryset, 'sender', value)

    def filter_by_agent_full_name(self, queryset, name, value):
        return self.filter_by_full_name(queryset, 'agent', value)
