from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
# from django.utils import timezone


User = get_user_model()

# class User(AbstractUser):
#     """Класс, описывающий стандартного пользователя."""
#     USER = 'user'
#     MODERATOR = 'moderator'
#     ADMIN = 'admin'
#     Role = (
#         (USER, '0'),
#         (MODERATOR, '1'),
#         (ADMIN, '2'),
#     )
#     email = models.EmailField(
#         'email',
#         max_length=254,
#         unique=True
#     )
#     first_name = models.CharField(
#         'first name',
#         max_length=150,
#         blank=True,
#     )
#     last_name = models.CharField(
#         'last name',
#         max_length=150,
#         blank=True,
#     )
#     bio = models.TextField(
#         'biography',
#         blank=True,
#         null=True,
#     )
#     role = models.CharField(
#         'role',
#         default='user',
#         choices=Role,
#         max_length=10,
#     )
# 
#     class Meta:
#         constraints = [
#             models.constraints.UniqueConstraint(
#                 fields=('username', 'email'),
#                 name='user_email_constraint'
#             )
#         ]
#         ordering = ('-id',)
# 
#     @property
#     def is_user(self):
#         return self.role == self.USER
# 
#     @property
#     def is_moderator(self):
#         return self.role == self.MODERATOR
# 
#     @property
#     def is_admin(self):
#         return self.role == self.ADMIN
# 
#     def permission_level(self) -> int:
#         return int(self.get_role_display())


class Tag(models.Model):
    """Класс, описывающий тэг."""
    name = models.CharField(
        'Тэг',
        default='Наименаование тэга',
        max_length=50,
    )
    hex_code = models.CharField(
        'HEX код',
        max_length=12,
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f"#{self.name}"


class Ingridient(models.Model):
    """Класс, описывающий ингридиент."""
    MG = 'mg'
    ML = 'ml'
    UNITLESS = 'unitless'
    UNITS = (
        (MG, 'мг'),
        (ML, 'мл'),
        (UNITLESS, 'шт')
    )
    name = models.CharField(
        'Название',
        default='Название ингридиента',
        max_length=50,
    )
    amount = models.PositiveIntegerField(
        'Количество',
        default=1,
        validators=(
            MinValueValidator(1,
                              message='Ингридиентов должны быть не менее 1!'),
        )
    )
    unit = models.CharField(
        'Единицы измерения',
        choices=UNITS,
        default=UNITLESS,
        max_length=10,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name', )

    def __str__(self):
        return f"{self.name} - {self.amount}{self.unit}"


class Recipe(models.Model):
    """Класс, описывающий рецепт."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.CharField(
        'Название',
        default='Название блюда',
        max_length=50,
    )
    # image = models.ImageField(
    #     'Изображение',
    #     upload_to='recipes/'
    # )
    description = models.TextField(
        'Описание',
        default='Текстовое описание',
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        related_name='recipes'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    time = models.IntegerField(
        'Минут на приготовление',
        validators=(
            MinValueValidator(1,
                              message='Время приготовления - положительное!'),
        ),
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('title', 'author')
