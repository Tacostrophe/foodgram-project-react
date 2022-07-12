from django.contrib.auth.models import AbstractUser
# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class User(AbstractUser):
    """Класс, описывающий стандартного пользователя."""
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        blank=False,
        validators=(
            RegexValidator(regex=r'^[\w.@+-]',),
        )
    )
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
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

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
        validators=(
            RegexValidator(regex=r'^#[0-9a-fA-F]{6}',),
        )
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f"#{self.name}"


class Ingredient(models.Model):
    """Класс, описывающий ингридиент."""
    name = models.CharField(
        'Название',
        default='Название ингридиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50,
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
        related_name='recipes',
    )
    name = models.CharField(
        'Название',
        default='Название блюда',
        max_length=200,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        blank=False,
    )
    description = models.TextField(
        'Описание',
        default='Текстовое описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
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
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class AmountOfIngridient(models.Model):
    ingridient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        'Количество',
    )


class Subscribtion(models.Model):
    following = models.ForeignKey(
        User,
        verbose_name='преследуемый',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='followers'
    )
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='followings'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.CheckConstraint(
                check=~models.Q(following=models.F('user')),
                name='cant_follow_youself'
            ),
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_following'
            ),
        )

    def __str__(self):
        return f'{self.user}=>{self.following}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='fans'
    )

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user}<3{self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='purchases'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='customers'
    )

    def __str__(self):
        return f'{self.user}-{self.recipe}'
