from django import forms
from django.contrib import admin
from django.contrib.sites.models import Site
from django.db.models import Count

from wardrobe.models import Item, Category, Company, Outfit, SystemMessage, UserPrefs, ImageUpload


# class ItemImageInline(admin.TabularInline):
# 	model = ItemImage
# 	extra = 0


class ItemForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea, required=False, max_length=1000)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'name',
            'colorway',
            'quantity',
            'size',
            'cost',
            'category',
            'company',
            'purchased_from',
            'purchase_date',
            'notes'
        ]

    class Meta:
        model = Item
        exclude = ()


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_display', 'colorway_display', 'cost_display')
    list_filter = ('company', 'category')
    # inlines = [ItemImageInline,]
    form = ItemForm
    save_as = True

    # list_per_page = 30

    def company_display(self, obj):
        if obj.company:
            return '<a href="/admin/wardrobe/company/%s/">%s</a>' % (obj.company.id, obj.company.name)
        else:
            return "None"

    company_display.short_description = 'Company'
    company_display.allow_tags = True
    company_display.admin_order_field = 'company'

    def cost_display(self, obj):
        if obj.cost:
            return "$%s" % obj.cost
        else:
            return "<span style='color:#aaa;font-style:italic;'>unknown</span>"

    cost_display.short_description = "Cost"
    cost_display.admin_order_field = 'cost'
    cost_display.allow_tags = True

    def colorway_display(self, obj):
        if obj.colorway:
            return obj.colorway
        else:
            return "<span style='color:#aaa;font-style:italic;'>n/a</span>"

    colorway_display.short_description = 'Colorway'
    colorway_display.admin_order_field = 'colorway'
    colorway_display.allow_tags = True


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryInline, ]


class OutfitAdmin(admin.ModelAdmin):
    list_display = ('name', 'items_count', 'value')

    @staticmethod
    def value(obj):
        return obj.value()

    def items_count(self, obj):
        return len(obj.items.all())

    items_count.short_description = 'Items'

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset().annotate(item_count=Count('items'))
        qs = qs.order_by('name', 'item_count')
        return qs

    class Meta:
        model = Outfit


admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Company)
admin.site.register(Outfit, OutfitAdmin)
admin.site.unregister(Site)
admin.site.register(SystemMessage)
admin.site.register(UserPrefs)
admin.site.register(ImageUpload)
