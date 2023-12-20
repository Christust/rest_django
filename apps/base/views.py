from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class HasGroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        required_user_types = view.permission_types.get(view.action)
        if required_user_types == None:
            return True
        elif request.user.is_anonymous:
            return False
        elif request.user.user_type == "superadmin":
            return True
        else:
            return request.user.user_type in required_user_types


class BaseGenericViewSet(viewsets.GenericViewSet):
    model = None
    status = status
    out_serializer_class = None
    serializer_class = None
    queryset = None
    permission_classes = [HasGroupPermission]
    permission_types = {}
    searched_object = None
    offset = 0
    limit = 100

    def get_object(self, pk):
        return get_object_or_404(self.queryset, pk=pk)

    def response(self, data, status):
        return Response(
            data=data, status=status if status is not None else self.status.HTTP_200_OK
        )


class BaseModelViewSet(viewsets.ModelViewSet):
    model = None
    status = status
    out_serializer_class = None
    serializer_class = None
    queryset = None
    permission_classes = [HasGroupPermission]
    permission_types = {}
    searched_object = None
    offset = 0
    limit = 100

    def get_object(self, pk):
        return get_object_or_404(self.queryset, pk=pk)

    def response(self, data, status):
        return Response(
            data=data, status=status if status is not None else self.status.HTTP_200_OK
        )
