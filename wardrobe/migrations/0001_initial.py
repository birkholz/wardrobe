# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'wardrobe_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'wardrobe', ['Category'])

        # Adding model 'Item'
        db.create_table(u'wardrobe_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['wardrobe.Category'])),
            ('purchased_from', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'wardrobe', ['Item'])

        # Adding model 'ItemImage'
        db.create_table(u'wardrobe_itemimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['wardrobe.Item'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'wardrobe', ['ItemImage'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'wardrobe_category')

        # Deleting model 'Item'
        db.delete_table(u'wardrobe_item')

        # Deleting model 'ItemImage'
        db.delete_table(u'wardrobe_itemimage')


    models = {
        u'wardrobe.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'wardrobe.item': {
            'Meta': {'object_name': 'Item'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['wardrobe.Category']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'purchased_from': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'wardrobe.itemimage': {
            'Meta': {'object_name': 'ItemImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['wardrobe.Item']"})
        }
    }

    complete_apps = ['wardrobe']