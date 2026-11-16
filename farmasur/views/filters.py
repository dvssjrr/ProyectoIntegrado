from rest_framework.filters import BaseFilterBackend

_TRUE = {'true', '1', 'yes', 'si', 'sí'}
_FALSE = {'false', '0', 'no'}


class DjangoFilterBackend(BaseFilterBackend):
    """Filtra por igualdad los campos declarados en `filterset_fields` usando query params."""

    def filter_queryset(self, request, queryset, view):
        fields = getattr(view, 'filterset_fields', None) or []
        filters = {}
        for field in fields:
            if field not in request.query_params:
                continue
            value = request.query_params[field]
            if value.lower() in _TRUE:
                value = True
            elif value.lower() in _FALSE:
                value = False
            filters[field] = value
        if not filters:
            return queryset
        try:
            return queryset.filter(**filters)
        except (ValueError, TypeError):
            return queryset.none()
