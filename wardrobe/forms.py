from django import forms
from models import Item, UserPrefs, ImageUpload
from timezone_field import TimeZoneFormField
from random import choice


item_names = ['Tweed Blazer', 'V-Neck Tee', 'Club Shorts', 'Wingtoe Dress Shoes', 'Wool Peacoat']
company_names = ['Uniqlo', 'American Eagle', 'Forever 21', 'GAP', 'Old Navy']
colorways = ['Navy', 'Heather Gray', 'White', 'Black']
costs = ['89.95', '59.50', '20', '15.90', '73.98']
purchased_froms = ['http://www.uniqlo.com/...', 'http://www.target.com/...', 'http://www.blueowl.us/...']
purchase_dates = ['10/05/2013', '12/10/2010', '04/10/2012']
sizes = ['Medium', '30', 'X-Small', 'Large', '42']


class ItemForm(forms.ModelForm):
	purchase_date = forms.DateField(input_formats=['%d/%m/%Y', '%m/%d/%Y',], required=False)
	# image = forms.ImageField(required=False)
	company_name = forms.CharField(required=False)

	def __init__(self, *args, **kwargs):
		date_format = kwargs.pop('date_format')
		super(ItemForm, self).__init__(*args, **kwargs)
		self.fields['purchase_date'].widget = forms.widgets.DateInput(format=date_format)
		self.fields['name'].widget.attrs = {'placeholder': choice(item_names)}
		self.fields['image_url'].widget.attrs = {'placeholder': 'http://i.imgur.com/...'}
		self.fields['company_name'].widget.attrs = {'placeholder': choice(company_names)}
		self.fields['colorway'].widget.attrs = {'placeholder': choice(colorways)}
		self.fields['cost'].widget.attrs = {'placeholder': choice(costs)}
		self.fields['purchased_from'].widget.attrs = {'placeholder': choice(purchased_froms)}
		self.fields['purchase_date'].widget.attrs = {'placeholder': choice(purchase_dates)}
		self.fields['size'].widget.attrs = {'placeholder': choice(sizes)}
		if self.instance and self.instance.company:
			self.fields['company_name'].initial = self.instance.company.name

	class Meta:
		model = Item
		exclude = ('owner','company')



class ProfileForm(forms.ModelForm):
	class Meta:
		model = UserPrefs
		fields = ('gender', 'birth_year', 'public_wardrobe')


class UserPrefsForm(forms.ModelForm):
	time_zone = TimeZoneFormField()
 
	class Meta:
		model = UserPrefs
		fields = ('currency', 'time_zone', 'date_format')


class ImageUploadForm(forms.ModelForm):
	class Meta:
		model = ImageUpload
		fields = ('image',)
