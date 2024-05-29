from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase


class ItemTag(TagBase):
    image = models.ImageField(
        upload_to='categories/',
        verbose_name='Изображение',
        blank=True
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        ItemTag,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name='Категория',
    )


class Item(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название', )
    description = models.TextField(verbose_name='Описание', )
    slug = models.CharField(
        unique=True,
        max_length=50,
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления', )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Новая цена',
    )
    old_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Старая цена',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='items/',
        blank=True,
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступно',
    )
    tags = TaggableManager(
        through=TaggedItem, related_name="tagged_items",
        verbose_name='Категории',
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-price']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ParsedPricesForItem(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='parsings'
    )
    source = models.CharField(null=False, blank=False, max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['item_id', 'source']

    @property
    def percent_difference(self):
        return abs(int((self.price - self.item.price) / self.item.price * 100))
