from django.contrib.auth.models import AbstractUser
# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class PersonalList(models.Model):
    user = models.OneToOneField(
        to='User',
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        related_query_name='%(class)ss'
    )

    class Meta:
        abstract = True


class PersonalRecipeList(PersonalList):
    recipe = models.ManyToManyField(
        to='Recipe',
        verbose_name='рецепт',
        blank=True,
        related_name='%(class)s',
        related_query_name='%(class)ss'
    )

    class Meta:
        abstract = True


class Favorite(PersonalRecipeList):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} <3 {self.recipe}'

    def __repr__(self):
        return f'{self.user} <3 {self.recipe}'


class ShoppingCart(PersonalRecipeList):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Sh. cart of {self.user}'

    def __repr__(self):
        return f'Sh. cart of {self.user}'


class Subscription(PersonalList):
    following = models.ManyToManyField(
        'User',
        verbose_name='преследуемый',
        blank=True,
        related_name='subscription_by',
        related_query_name='subscriptions_by'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user}=>{self.following}'

    def __repr__(self):
        return f'{self.user}=>{self.following}'


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

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            Favorite.objects.create(user=self)
            ShoppingCart.objects.create(user=self)
            Subscription.objects.create(user=self)

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username


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

    def __repr__(self):
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

    def __repr__(self):
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
    image = models.FileField(
        'Изображение',
        upload_to='recipes/',
        blank=False,
    )
    text = models.TextField(
        'Описание',
        default='Текстовое описание',
    )
    ingredients = models.ManyToManyField(
        'AmountOfIngredient',
        blank=True,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=False,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
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

    def __repr__(self):
        return self.name


class AmountOfIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount_of_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount_of_ingredients'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(
            MinValueValidator(1,
                              message='Минимальное количество - 1!'),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        unique_together = ['ingredient', 'recipe']

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} ' +
                f'{self.ingredient.measurement_unit}')

    def __repr__(self):
        return (f'{self.ingredient.name} - {self.amount} ' +
                f'{self.ingredient.measurement_unit}')
