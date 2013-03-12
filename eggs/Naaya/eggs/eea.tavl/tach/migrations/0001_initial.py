# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('tach_user', (
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=128, primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countries.Country'], null=True, blank=True)),
            ('affiliation', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=256, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('tach', ['User'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('tach_user')


    models = {
        'countries.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country', 'db_table': "'country'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'tach.user': {
            'Meta': {'object_name': 'User'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countries.Country']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'})
        }
    }

    complete_apps = ['tach']