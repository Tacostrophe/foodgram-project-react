from django.contrib.auth.models import AbstractUser
# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    """Класс, описывающий стандартного пользователя."""
#     USER = 'user'
#     MODERATOR = 'moderator'
#     ADMIN = 'admin'
#     Role = (
#         (USER, '0'),
#         (MODERATOR, '1'),
#         (ADMIN, '2'),
#     )
    email = models.EmailField(
        'email',
        max_length=254,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
    )
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

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=('username', 'email'),
                name='user_email_constraint'
            )
        ]
        ordering = ('-id',)
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
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=12,
        unique=True,
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
    G = 'g'
    KG = 'kg'
    ML = 'ml'
    L = 'l'
    UNIT = 'unitless'
    MEASUREMENT_UNITS = (
        (MG, 'мг'),
        (G, 'г'),
        (KG, 'кг'),
        (ML, 'мл'),
        (L, 'л'),
        (UNIT, 'шт')
    )
    name = models.CharField(
        'Название',
        default='Название ингридиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        choices=MEASUREMENT_UNITS,
        default=UNIT,
        max_length=10,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс, описывающий рецепт."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        # related_name='recipes',
    )
    name = models.CharField(
        'Название',
        default='Название блюда',
        max_length=200,
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
        through='AmountOfIngridient',
        blank=False,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=False,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        'Минут на приготовление',
        validators=(
            MinValueValidator(1,
                              message='Минимальное время готовки - 1 минута!'),
        ),
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name', 'author')

    def __str__(self):
        return self.name


class AmountOfIngridient(models.Model):
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        'Количество',
    )
