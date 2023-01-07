import datetime
import os
import uuid as uuid
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import utc
from timezone_field import TimeZoneField


def image_file_name(instance, filename):
    extension = os.path.splitext(filename)[1]
    file_name = instance.uuid
    return f'media/${file_name}${extension}'


class ImageUpload(models.Model):
    uuid = models.CharField(max_length=32, default=uuid.uuid4, primary_key=True, editable=False)
    image = models.ImageField(upload_to=image_file_name)
    author = models.ForeignKey(User, related_name='images', null=True, blank=True, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.image.name

    def get_absolute_url(self):
        return self.image.url


class SystemMessage(models.Model):
    message = models.CharField(max_length=500)
    author = models.ForeignKey(User, related_name='sys_messages', null=True, blank=True, on_delete=models.SET_NULL)
    users_read = models.ManyToManyField(User, related_name='read_sys_messages', blank=True)
    date_sent = models.DateField(auto_now_add=True)
    important = models.BooleanField(default=False)

    def has_read(self, user):
        if user in self.users_read.all():
            return True
        return False

    def __str__(self):
        return '%s: %s...' % (self.author.username, self.message[:50])

    class Meta:
        verbose_name_plural = "System Messages"
        ordering = ['-date_sent']


class UserPrefs(models.Model):
    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    CURRENCIES = (
        ('USD', 'USD: $'),
        ('GBP', 'GBP: &pound;'),
        ('AUD', 'AUD: $'),
        ('EUR', 'EUR: &euro;'),
        ('CAD', 'CAD: $')
    )
    DATE_FORMATS = (
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
    )
    user = models.OneToOneField(User, primary_key=True, related_name='prefs', on_delete=models.CASCADE)
    # Profile Settings
    gender = models.CharField(max_length=1, choices=GENDERS, null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    # Localization Settings
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='USD')
    time_zone = TimeZoneField(null=True, blank=True)
    date_format = models.CharField(max_length=10, choices=DATE_FORMATS, default="MM/DD/YYYY")
    public_wardrobe = models.BooleanField(default=False)

    def get_today(self, pobj=False):
        today = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.time_zone:
            today = today.astimezone(self.time_zone)
            if pobj:
                return today
        return today.strftime(self.get_date_format())

    def get_date_format(self):
        if self.date_format == 'MM/DD/YYYY':
            return '%m/%d/%Y'
        elif self.date_format == 'DD/MM/YYYY':
            return '%d/%m/%Y'

    def get_currency_symbol(self):
        if self.currency == 'USD':
            return '$'
        elif self.currency == 'AUD':
            return '$'
        elif self.currency == 'CAD':
            return '$'
        elif self.currency == 'GBP':
            return '&pound;'
        elif self.currency == 'EUR':
            return '&euro;'

    def is_male(self):
        if self.gender == 'M':
            return True
        return False

    def is_female(self):
        if self.gender == 'F':
            return True
        return False

    def get_age(self):
        if self.birth_year:
            today = self.get_today(pobj=True)
            return today.replace(today.year - self.birth_year).year
        return None

    def is_adult(self):
        if self.get_age() > 18:
            return True
        return False

    def __str__(self):
        return 'Prefences for user %s' % self.user.username

    class Meta:
        verbose_name_plural = "User Preferences"
        ordering = ['user']


class Category(models.Model):
    name = models.CharField(max_length=200)
    parent_category = models.ForeignKey('self', null=True, blank=True, related_name='subcats', on_delete=models.CASCADE)

    def get_count_dict(self, user):
        item_count = self.item_count(user)
        if item_count == 0:
            return None
        else:
            cat_dict = {'name': self.name, 'value': item_count}
            subcats = self.subcats.all()
            if subcats:
                child_cats = []
                for subcat in subcats:
                    subcat_dict = subcat.get_count_dict(user)
                    if subcat_dict:
                        child_cats.append(subcat_dict)
                if child_cats:
                    cat_dict['children'] = child_cats
            return cat_dict

    def get_value_dict(self, user):
        value = self.value(user)
        if value == 0:
            return None
        else:
            cat_dict = {'name': self.name, 'value': value}
            subcats = self.subcats.all()
            if subcats:
                child_cats = []
                for subcat in subcats:
                    subcat_dict = subcat.get_value_dict(user)
                    if subcat_dict:
                        child_cats.append(subcat_dict)
                if child_cats:
                    cat_dict['children'] = child_cats
            return cat_dict

    def value(self, user):
        value = 0
        for item in self.items.filter(owner=user):
            value += item.value()
        if self.subcats.all():
            for cat in self.subcats.all():
                value += cat.value(user)
        return value

    def children_value(self, user):
        value = 0
        for cat in self.subcats.all():
            value += cat.value(user)
        return value

    def is_top_level(self):
        if self.parent_category is None:
            return True
        return False

    def has_children(self):
        if self.subcats.all():
            return True
        return False

    def has_items(self, user):
        if self.items.filter(owner=user):
            return True
        else:
            for subcat in self.subcats.all():
                if subcat.has_items(user):
                    return True
            return False

    def item_count(self, user):
        count = 0
        count += self.items.filter(owner=user).count()
        count += self.children_item_count(user)
        return count

    def children_item_count(self, user):
        if self.has_children():
            count = 0
            for child in self.subcats.all():
                count += child.item_count(user)
            return count
        return 0

    def merge_with_category(self, cat2):
        for item in self.items.all():
            item.category = cat2
            item.save()
        self.delete()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(max_length=500, null=True, blank=True)

    def merge_with_company(self, comp2):
        for item in self.items.all():
            item.company = comp2
            item.save()
        self.delete()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']


class Item(models.Model):
    name = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, related_name="items", null=True, blank=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, related_name="items", null=True, blank=True, on_delete=models.SET_NULL)
    purchased_from = models.CharField(max_length=500, null=True, blank=True)
    size = models.CharField(max_length=200, null=True, blank=True)
    colorway = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    purchase_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User, related_name="items", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    owned = models.BooleanField(default=True)
    images = GenericRelation(ImageUpload)
    default_image = models.ForeignKey(ImageUpload, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    def purchase_link(self):
        if self.purchased_from:
            try:
                return urlparse(self.purchased_from).geturl()
            except:
                pass
        return False

    def get_wear_count(self):
        return self.dates_worn.all().count()

    def get_dates_worn(self):
        return self.dates_worn.dates('date', 'day', order='DESC')

    def get_latest_date_worn(self):
        objs = self.get_dates_worn()
        if objs:
            return objs[0].replace(tzinfo=None)
        return None

    def value(self):
        if self.cost:
            if self.quantity > 1:
                return Decimal(self.cost * self.quantity).quantize(Decimal('.01'), rounding=ROUND_DOWN)
            else:
                return self.cost.quantize(Decimal('.01'), rounding=ROUND_DOWN)
        else:
            return 0

    def __str__(self):
        if self.company and self.colorway:
            return '%s - %s in %s' % (self.company.name, self.name, self.colorway)
        elif self.company and not self.colorway:
            return '%s - %s' % (self.company.name, self.name)
        else:
            return self.name

    class Meta:
        ordering = ['name']

    def delete(self, *args, **kwargs):
        for iu in self.images.iterator():
            iu.delete()
        super(Item, self).delete(*args, **kwargs)


class Outfit(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Item, related_name='outfits')
    notes = models.CharField(max_length=1000, null=True, blank=True)
    owner = models.ForeignKey(User, related_name="outfits", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    images = GenericRelation(ImageUpload)

    def get_items_count(self):
        return self.items.all().count()

    def get_wear_count(self):
        return self.dates_worn.all().count()

    def get_worn_plural(self):
        count = self.get_wear_count()
        if count == 0:
            return ''
        elif count == 1:
            return ', worn once'
        elif count == 2:
            return ', worn twice'
        elif count == 3:
            return ', worn thrice'
        elif count > 3:
            return ', worn %s times' % count

    def get_dates_worn(self):
        return self.dates_worn.dates('date', 'day', order='DESC')

    def get_latest_date_worn(self):
        objs = self.get_dates_worn()
        if objs:
            return objs[0]
        return None

    def value(self):
        value = 0
        for item in self.items.all():
            value += item.value()
        return value

    def get_absolute_url(self):
        return "/outfit/%s/" % self.id

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ItemWornDate(models.Model):
    item = models.ForeignKey(Item, related_name='dates_worn', on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return '%s worn on %s' % (self.item, self.date)

    class Meta:
        ordering = ['-date']
        unique_together = ('item', 'date')


class OutfitWornDate(models.Model):
    outfit = models.ForeignKey(Outfit, related_name='dates_worn', on_delete=models.CASCADE)
    date = models.DateField()

    def save(self, *args, **kwargs):
        super(OutfitWornDate, self).save(*args, **kwargs)
        for item in self.outfit.items.all():
            ItemWornDate.objects.create(item=item, date=self.date)

    def __str__(self):
        return '%s worn on %s' % (self.outfit, self.date)

    class Meta:
        ordering = ['-date']
        unique_together = ('outfit', 'date')
