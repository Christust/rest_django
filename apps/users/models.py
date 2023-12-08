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
        email: str,
        name: str,
        last_name: str,
        user_type: str,
        password: str | None,
        **extra_fields,
    ):
        """
        Función base que utilizaran nuestras funciones para crear usuarios normales o superusuario
        """

        # Instanciamos el modelo con los parametros recibidos
        user = self.model(
            email=email,
            name=name,
            last_name=last_name,
            user_type=user_type,
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
        email: str,
        name: str,
        last_name: str,
        user_type: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Función para crear usuarios normales
        """

        # Con los parametros recibidos creamos un usuario normal llamando _create_user
        return self._create_user(
            email,
            name,
            last_name,
            user_type,
            password,
            **extra_fields,
        )

    # Función para crear superusuarios
    def create_superuser(
        self,
        email: str,
        name: str,
        last_name: str,
        user_type: str = "superuser",
        password: str | None = None,
        **extra_fields,
    ):
        """
        Función para crear superusuarios
        """

        # Con los parametros recibidos creamos un superusuario llamando _create_user
        return self._create_user(
            email,
            name,
            last_name,
            user_type,
            password,
            **extra_fields,
        )


class User(AbstractBaseUser):
    # Enum de tipos de usuario
    class UserType(models.TextChoices):
        SUPER_ADMIN = "superadmin"
        ADMIN = "admin"
        COMMON = "common"

    # Atributo principal de nuestro modelo persoanlizado
    email = models.EmailField("Email", unique=True, max_length=100)

    # Atributos extra que personalizamos para nuestro modelo
    name = models.CharField("Name", max_length=100, blank=False, null=False)

    last_name = models.CharField("Lastname", max_length=100, blank=False, null=False)

    user_type = models.CharField(
        "User type", max_length=20, choices=UserType.choices, blank=False, null=False
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Atributos requeridos para nuestro mixin de permisos
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.name} {self.last_name}"

    @property
    def is_superuser(self):
        return self.user_type == self.UserType.SUPER_ADMIN

    def has_perm(self, perm, obj=None):
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
    USERNAME_FIELD = "email"

    # El atributo REQUIRED_FIELDS se usa para declarar los atributos requeridos al crear un usuario
    REQUIRED_FIELDS = ["name", "last_name", "user_type"]

    # Función para declarar la llave natural del modelo, si hay relaciones uno a muchos o muchos
    # a muchos, en lugar de mostrar el id, mostrara lo que esta función nos retorne
    def natural_key(self):
        return self.email

    # Función para retornar un string al llamar una instancia de este modelo
    def __str__(self):
        return f"{self.full_name}"
