from django.contrib import admin
from django.utils.text import Truncator

from survey import models as survey_models
from tach import models as tach_models
from countries import models as country_models


def category_title(survey):
    return Truncator(survey.category.title).chars(100)


def survey_title(survey):
    return Truncator(survey.title).chars(100)


class UserAdmin(admin.ModelAdmin):

    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('first_name', 'last_name', 'email')


class CountryAdmin(admin.ModelAdmin):

    search_fields = ('name', )


class SectionAdmin(admin.ModelAdmin):

    search_fields = ('name', )


class CategoryAdmin(admin.ModelAdmin):

    search_fields = ('title', )
    list_display = ('title', 'section', 'for_user', 'multiple_answers')


class SurveyAdmin(admin.ModelAdmin):

    search_fields = ('category', 'country', 'user', 'title')
    list_display = (category_title, 'country', 'user', 'title')


admin.site.register(tach_models.User, UserAdmin)

admin.site.register(survey_models.Section, SectionAdmin)

admin.site.register(survey_models.Category, CategoryAdmin)

admin.site.register(survey_models.Survey, SurveyAdmin)

