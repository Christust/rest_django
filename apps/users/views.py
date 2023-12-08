from django.contrib.auth import authenticate

from rest_framework import views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users import serializers, models
from apps.base.views import BaseGenericViewSet


class UserViewSet(BaseGenericViewSet):
    model = models.User
    serializer_class = serializers.UserSerializer
    out_serializer_class = serializers.UserOutSerializer
    queryset = serializer_class.Meta.model.objects.filter(is_active=True)
    permission_types = {
        "list": ["admin"],
        "retrieve": ["admin"],
        "set_password": ["admin"],
        "create": ["admin"],
        "update": ["admin"],
    }

    def list(self, request):
        offset = int(self.request.query_params.get("offset", 0))
        limit = int(self.request.query_params.get("limit", 10))

        users = self.queryset.all()[offset : offset + limit]
        users_out_serializer = self.out_serializer_class(users, many=True)
        return self.response(
            data=users_out_serializer.data, status=self.status.HTTP_200_OK
        )

    def create(self, request):
        user_serializer = self.serializer_class(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = self.get_object(user_serializer.data.get("id"))
            user_out_serializer = self.out_serializer_class(user)
            return self.response(
                data=user_out_serializer.data, status=self.status.HTTP_201_CREATED
            )
        return self.response(
            data=user_serializer.errors, status=self.status.HTTP_406_NOT_ACCEPTABLE
        )

    def retrieve(self, request, pk):
        user = self.get_object(pk)
        user_out_serializer = self.out_serializer_class(user)
        return self.response(
            data=user_out_serializer.data, status=self.status.HTTP_200_OK
        )

    def update(self, request, pk):
        user = self.get_object(pk)
        user_out_serializer = self.out_serializer_class(
            user, data=request.data, partial=True
        )
        if user_out_serializer.is_valid():
            user_out_serializer.save()
            return self.response(
                data=user_out_serializer.data, status=self.status.HTTP_202_ACCEPTED
            )
        return self.response(
            data=user_out_serializer.errors, status=self.status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post", "put"])
    def set_password(self, request, pk=None):
        current_user = self.request.user
        user = self.get_object(pk)
        password_serializer = serializers.PasswordSerializer(
            data=request.data, context={"current_user": current_user, "user": user}
        )
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data["password"])
            user.save()
            return self.response(
                data={"message": "Password updated"}, status=self.status.HTTP_200_OK
            )
        return self.response(
            data=password_serializer.errors, status=self.status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk):
        user = self.get_object(pk)
        user.is_active = False
        user.save()
        return self.response(
            data={"message": "Deleted"}, status=self.status.HTTP_200_OK
        )


class Login(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = serializers.UserOutSerializer(user)
                return Response(
                    {
                        "token": login_serializer.validated_data.get("access"),
                        "refresh": login_serializer.validated_data.get("refresh"),
                        "user": user_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "No existe el usuario"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"error": "No existe el usuario"}, status=status.HTTP_400_BAD_REQUEST
        )


class Logout(views.APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user:
            token = RefreshToken(request.data.get("refresh_token"))
            token.blacklist()
            return Response({"message": "Sesion cerrada"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "No existe el usuario"}, status=status.HTTP_400_BAD_REQUEST
        )
