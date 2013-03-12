# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Section'
        db.create_table('section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('survey', ['Section'])

        # Adding model 'Category'
        db.create_table('category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2056)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Section'])),
            ('widget', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('for_user', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('multiple_answers', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('survey', ['Category'])

        # Adding model 'Language'
        db.create_table('language', (
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=3, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('survey', ['Language'])

        # Adding model 'Survey'
        db.create_table('survey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Category'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countries.Country'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tach.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('english_title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('parts_considered', self.gf('django_hstore.fields.DictionaryField')(db_index=True, null=True, blank=True)),
            ('transport_modes', self.gf('django_hstore.fields.DictionaryField')(db_index=True, null=True, blank=True)),
            ('climate_change_impacts', self.gf('django_hstore.fields.DictionaryField')(db_index=True, null=True, blank=True)),
            ('responsible_organisation', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Language'], null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('focus', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('section_a_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_a_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_b_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_b_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_c2', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_d_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_c_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('section_e_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('area_of_expertise', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('adaptation_strategy', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('transport_information', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('trans_national_cooperation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('stakeholders_cooperaton', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('integration_of_climate_change', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('funding', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('revision_of_design', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('climate_proof', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('development_methodologies', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('data_collection', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('transport_research', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lack_of_awareness', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('knowledge_gaps', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('data_gaps', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lack_of_training', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lack_of_capacities', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lack_of_resources', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('access_to_funding', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lack_of_coordination', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('awareness_lack_eu_level', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('relevance', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('d1_comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('d2_comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Survey'])


    def backwards(self, orm):
        # Deleting model 'Section'
        db.delete_table('section')

        # Deleting model 'Category'
        db.delete_table('category')

        # Deleting model 'Language'
        db.delete_table('language')

        # Deleting model 'Survey'
        db.delete_table('survey')


    models = {
        'countries.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country', 'db_table': "'country'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'survey.category': {
            'Meta': {'ordering': "['pk']", 'object_name': 'Category', 'db_table': "'category'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2056'}),
            'for_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple_answers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Section']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'widget': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'survey.language': {
            'Meta': {'object_name': 'Language', 'db_table': "'language'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '3', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'survey.section': {
            'Meta': {'object_name': 'Section', 'db_table': "'section'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey', 'db_table': "'survey'"},
            'access_to_funding': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'adaptation_strategy': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'area_of_expertise': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'awareness_lack_eu_level': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Category']"}),
            'climate_change_impacts': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'climate_proof': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countries.Country']"}),
            'd1_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'd2_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'data_collection': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'data_gaps': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'development_methodologies': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'english_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'focus': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'funding': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integration_of_climate_change': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'knowledge_gaps': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'lack_of_awareness': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'lack_of_capacities': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'lack_of_coordination': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'lack_of_resources': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'lack_of_training': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Language']", 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'parts_considered': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'relevance': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'responsible_organisation': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'revision_of_design': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'section_a_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_a_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_b_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_b_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_c2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_c_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_d_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'section_e_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stakeholders_cooperaton': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'trans_national_cooperation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'transport_information': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'transport_modes': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'transport_research': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tach.User']"}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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

    complete_apps = ['survey']