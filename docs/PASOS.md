# Inicio del proyecto

Empiezas el proyecto:

```
django-admin startproject dapi
```

Te mueves al proyecto:

```
cd dapi
```

Empiezas un entorno virtual:

```
python3 -m venv venv
source venv/bin/activate
```

Instalas las dependencias del proyecto:

```
pip install Django
pip install djangorestframework
pip install django-simple-history
pip install Pillow
pip install drf-yasg
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install django-extensions
```

Para un mayor control podemos dividir las apps en settings.py, aprovechamos para agregar las apps de terceros que acabamos de instalar:

```
BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = []

THIRD_APPS = [
    "rest_framework",
    "simple_history",
    "drf_yasg",
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_extensions",
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS
```

Agregamos las configuraciones para seguridad y cors en el proyecto en nuestro archivo settings.py del folder principal:

```
# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]

CORS_ORIGIN_WHITELIST = [
    "http://localhost:8000",
    "http://localhost:3000",
]

# Auth Rest
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# SIMPLE JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

Creamos la app que gestionara a nuestros usuarios:

```
mkdir apps
cd apps
django-admin startapp users
```

Modificamos el archivo apps.py de la app users:

```
name = "apps.users"
```

Cada que creemos una app colocaremos el nombre de su carpeta contedora en caso de que no esten en la raiz del proyecto.

Dentro de la app users y en su archivo models.py agregamos:

```
# Importamos models para crear nuestros atributos de nuestro modelo
from django.db import models

# Importamos AbstractBaseUser para crear un modelo personalizado de usuario casi desde 0
# Importamos BaseUserManager para crear un manager para nuestro modelo, el manager
# es el atributo llamado objects que gestiona las funciones create_user por ejemplo
# Importamos PermissionsMixin para heredar a nuestro usuario el mixin de permisos y grupos
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Importamos la clase HistoricalRecords, una app de terceros que lleva un historico de las
# acciones de nuestro modelo
from simple_history.models import HistoricalRecords


# Create your models here.
class UserManager(BaseUserManager):
    # Función base que utilizaran nuestras funciones para crear usuarios normales o superusuario
    def _create_user(
        self,
        username: str,
        email: str,
        name: str,
        last_name: str,
        password: str | None,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ):
        """
        Función base que utilizaran nuestras funciones para crear usuarios normales o superusuario
        """

        # Instanciamos el modelo con los parametros recibidos
        user = self.model(
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )

        # Encriptamos el parametro password y lo depositamos en el atributo password de
        # este usuario
        user.set_password(password)

        # Guardamos el usuario
        user.save(using=self.db)

    # Función para crear usuarios normales
    def create_user(
        self,
        username: str,
        email: str,
        name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Función para crear usuarios normales
        """

        # Con los parametros recibidos creamos un usuario normal llamando _create_user
        return self._create_user(
            username, email, name, last_name, password, False, False, **extra_fields
        )

    # Función para crear superusuarios
    def create_superuser(
        self,
        username: str,
        email: str,
        name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Función para crear superusuarios
        """

        # Con los parametros recibidos creamos un superusuario llamando _create_user
        return self._create_user(
            username, email, name, last_name, password, True, True, **extra_fields
        )


class User(AbstractBaseUser):
    # Atributo principal de nuestro modelo persoanlizado
    username = models.CharField("Username", unique=True, max_length=100)

    # Atributos extra que personalizamos para nuestro modelo
    email = models.EmailField("Email", unique=True, max_length=100)
    name = models.CharField("Name", max_length=100, blank=True, null=True)
    last_name = models.CharField("Lastname", max_length=100, blank=True, null=True)
    image = models.ImageField("Image", upload_to="perfil/", max_length=200, height_field=None, width_field=None, blank=True, null=True)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Atributos requeridos para nuestro mixin de permisos
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=True)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Atributo que sera nuestro manager
    objects = UserManager()

    # Atributo necesario para el historial de acciones
    historical = HistoricalRecords()

    # Clase Meta, declaramos aqui nuestro metadatos para el modelo
    class Meta:
        # Atributos para el nombre en singular y el nombre en plural
        verbose_name = "User"
        verbose_name_plural = "Users"

    # Atributos necesarios para un modelo de usuario

    # El atributo USERNAME_FIELD es para delcarar el atributo principal de la clase
    USERNAME_FIELD = "username"

    # El atributo REQUIRED_FIELDS se usa para declarar los atributos requeridos al crear un usuario
    REQUIRED_FIELDS = ["email", "name", "last_name"]

    # Función para declarar la llave natural del modelo, si hay relaciones uno a muchos o muchos
    # a muchos, en lugar de mostrar el id, mostrara lo que esta función nos retorne
    def natural_key(self):
        return self.username

    # Función para retornar un string al llamar una instancia de este modelo
    def __str__(self):
        return f"User {self.username}"


```

Agregamos la app users a nuestras apps locales:

```
LOCAL_APPS = ["apps.users"]
```

Agregamos en settings.py el modelo customizado de usuario que creamos:

```
# Custom user
AUTH_USER_MODEL = "users.User"

```

Ejecutamos las migraciones:

```
python manage.py makemigrations
python manage.py migrate
```

Creamos un superusuario:

```
python manage.py createsuperuser
```

En la app users crearemos el archivo serializers.py:

```
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["created_at", "updated_at", "last_login"]

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "created_at", "updated_at", "last_login"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass

```

En la app users en su archivo views.py colocamos lo siguiente:

```
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import (
    UserSerializer,
    UserOutSerializer,
    CustomTokenObtainPairSerializer,
    PasswordSerializer,
)
from apps.users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView


class UserViewSet(viewsets.GenericViewSet):
    model = User
    serializer_class = UserSerializer
    out_serializer_class = UserOutSerializer
    queryset = serializer_class.Meta.model.objects.filter(is_active=True)

    def get_object(self, pk):
        return get_object_or_404(self.queryset, pk=pk)

    def list(self, request):
        users = self.queryset.all()
        users_out_serializer = self.out_serializer_class(users, many=True)
        return Response(data=users_out_serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user_serializer = self.serializer_class(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user_out_serializer = self.out_serializer_class(user_serializer.data)
            return Response(
                data=user_out_serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            data=user_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    def retrieve(self, request, pk):
        user = self.get_object(pk)
        user_out_serializer = self.out_serializer_class(user)
        return Response(data=user_out_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk):
        user = self.get_object(pk)
        user_out_serializer = self.out_serializer_class(
            user, data=request.data, partial=True
        )
        if user_out_serializer.is_valid():
            user_out_serializer.save()
            return Response(
                data=user_out_serializer.data, status=status.HTTP_202_ACCEPTED
            )
        return Response(
            data=user_out_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post", "put"])
    def set_password(self, request, pk=None):
        user = self.get_object(pk)
        password_serializer = PasswordSerializer(data=request.data)
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data["password"])
            user.save()
            return Response(
                data={"message": "Password updated"}, status=status.HTTP_200_OK
            )
        return Response(
            data=password_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk):
        user = self.get_object(pk)
        user.is_active = False
        user.save()
        return Response(data={"message": "Deleted"}, status=status.HTTP_200_OK)


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = UserOutSerializer(user)
                return Response(
                    {
                        "token": login_serializer.validated_data.get("access"),
                        "refresh": login_serializer.validated_data.get("refresh"),
                        "user": user_serializer.data,
                    },
                    status.HTTP_200_OK,
                )
            return Response(
                {"error": "No existe el usuario"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"error": "No existe el usuario"}, status=status.HTTP_400_BAD_REQUEST
        )


class Logout(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user:
            token = RefreshToken(request.data.get("refresh_token"))
            token.blacklist()
            return Response({"message": "Sesion cerrada"})
        return Response(
            {"error": "No existe el usuario"}, status=status.HTTP_400_BAD_REQUEST
        )

```

Creamos el archivo urls.py dentro de nuestra aplicación users y le colocamos el router con nuestro viewSet de usuarios:

```
from rest_framework.routers import DefaultRouter
from apps.users import views

router = DefaultRouter()

router.register(r"", views.UserViewSet)

urlpatterns = [] + router.urls
```

Para agregar las rutas ahora hacemos un include en el archivo urls.py principal del proyecto:

```
from django.urls import ..., include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import Login, Logout
...

urlpatterns = [
    ...
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", include("apps.users.urls")),
    ...
]
```

Si en algun punto necesitamos de un modelo base para declarar atributos y metodos compartidos podemos crearlo:

```
from django.db import models

class BaseModel(models.Model):
id = models.AutoField(primary_key=True)
state = models.BooleanField("Estado", default=True)
created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
updated_at = models.DateTimeField("Fecha de actualización", auto_now=True)
deleted_at = models.DateTimeField("Fecha de eliminación", auto_now=True)

    class Meta:
        abstract = True
        verbose_name = "Base Model"
        verbose_name_plural = "Base Models"

```

En el modelo que querramos que tenga esos atributos solo debemos heredarlo de BaseModel.

# Serializers

Los serializers son clases cambian a json los modelos de Django y viceversa.

```
from rest_framework import serializers
from apps.example.models import ExampleModel

class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        # Campos a mostrar:
        # fields = "__all__"
        # o
        # fields = ["field1", "field2", ...]
        # O campos a ocultar usando la misma sintaxis:
        # exclude = ["field1", ...]
```

Podemos usarlos para mandar un json o para recibir un json.

Para mandar:

```
# Alguna View que retorne a los usuarios por ejemplo

users = User.objects.all()

# El parametro many=True es necesario si son varios registros
# En caso de ser solo uno, no es necesario ya que por defecto
# es False
users_serializer = UserSerializer(users, many=True)
return Response(users_serializer.data, status.HTTP_200_OK)
```

Para recibir y guardar un nuevo registro:

```
users_serializer = UserSerializer(data=request.data)
if users_serializer.is_valid():
    user_serializer.save()
    return Response(user_serializer.data)
return Response(user_serializer.errors)
```

Para recibir y actualizar un registro existente:

```
user = User.objects.filter(id=pk).first()
users_serializer = UserSerializer(user, data=request.data)
if users_serializer.is_valid():
    user_serializer.save()
    return Response(user_serializer.data)
return Response(user_serializer.errors)
```

Podemos crear validaciones para nuestros campos:

```
def validate_field(self, value):
    if condition:
        raise serializers.ValidationError("Message")
    return value
```

Tenemos un metodo para los serializadores cuando guardan datos validados para nuestros campos:

```
def create(self, validated_data):
    return ExampleModel.objects.create(**validated_data)
```

Tenemos un metodo para los serializadores cuando actualizan datos validados para nuestros campos:

```
def update(self, instance, validated_data):
    instance.field1 = validated_data.get("field1", instance.field1)
    instance.save()
    return instance
```

Tenemos un metodo para los serializadores cuando retornan datos y asi separar el fields="**all**" para guardar y actualizar datos y este metodo para listar un registro o varios:

```
def to_representation(self, instance):
    return {
        # Este en caso de usar all()
        "field":instance.field,
        # En caso de usar all().values("field1", "field2")
        # Usamos "field":instance["field"]
        ...
    }
```

Si se necesita usar un serializador con relaciones foraneas, si solo pintamos el serializador este nos mostrara unicamente los ids de las llaves, si lo que necesitamos es mostrar mas informacion tenemos tres metodos para cambiar esto:

```
# Metodo 1:
# Esto retornara solo el metodo string del campo relacionado
class ProductSerializer(serializers.ModelSerializer):
    measure_unit = serializers.StringRelatedField()
    category_product = serializers.StringRelatedField()

    class Meta:
        model = Product
        exclude = ["state", "created_at", "updated_at"]

# Metodo 2
# Esto retornara el serializer para dicho campo relacionado
class ProductSerializer(serializers.ModelSerializer):
    measure_unit = general.MeasureUnitSerializer()
    category_product = general.CategoryProductSerializer()

    class Meta:
        model = Product
        exclude = ["state", "created_at", "updated_at"]

# Metodo 3
# Este nos permite crear una respuesta mas personalizada y completa pero
# necesita de validaciones cuando se declara.
class ProductSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "description": instance.description,
            "image": instance.image if instance.image != "" else "",
            "measure_unit": instance.measure_unit.description,
            "category_product": instance.category_product.description,
        }

    class Meta:
        model = Product
        exclude = ["state", "created_at", "updated_at"]
```

# Views Rest

Django Rest ofrece una clase de la cual se puede heredar para generar rutas basadas en clases:

```
from rest_framework.views import APIView

class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        users_serializer = UserSerializer(users, many=True)
        return Response(users_serializer.data, status.HTTP_200_OK)
```

Si queremos una clase generica para listar elementos podemos usar ListAPIView:

```
from rest_framework.generics import ListAPIView
from apps.products import models


class MeasureUnitListAPIView(ListAPIView):
    model = models.MeasureUnit
    queryset = model.objects.filter(state=True)
```

# Decoradores REST

Django Rest nos ofrece un decorador llamado api_view el cual nos ayudara a utilizar funciones aisladas para determinadas rutas.

```
@api_view(["GET"])
def user_api_view(request):
    if request.method == "GET":
        users = User.objects.all()
        users_serializer = UserSerializer(users, many=True)
        return Response(users_serializer.data, status.HTTP_200_OK)
```
