# -*- coding: utf-8 -*-
from telemeta.models import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.conf.urls import url
from telemeta.views.admin import AdminView

admin.site.unregister(User)

class MediaFondsAdmin(admin.ModelAdmin):
    search_fields = ['title', 'code']
    ordering = ['code']
    filter_horizontal = ['children']

class MediaCorpusAdmin(admin.ModelAdmin):
    search_fields = ['title', 'code']
    ordering = ['code']
    filter_horizontal = ['children']

class MediaCollectionRelatedInline(admin.StackedInline):
    model = MediaCollectionRelated

class MediaCollectionIdentifierInline(admin.StackedInline):
    model = MediaCollectionIdentifier
    max_num = 1

class MediaCollectionAdmin(admin.ModelAdmin):
    search_fields = ['title', 'code']
    ordering = ['code']
    inlines = [MediaCollectionIdentifierInline,
                MediaCollectionRelatedInline]

class MediaItemRelatedInline(admin.StackedInline):
    model = MediaItemRelated

class MediaItemMarkerInline(admin.StackedInline):
    model = MediaItemMarker

class MediaItemTranscodedInline(admin.StackedInline):
    model = MediaItemTranscoded

class MediaItemIdentifierInline(admin.StackedInline):
    model = MediaItemIdentifier
    max_num = 1

class MediaItemAdmin(admin.ModelAdmin):
    search_fields = ['title', 'code']
    ordering = ['code']
    exclude = ('copied_from_item', )
    inlines = [MediaItemIdentifierInline,
                MediaItemRelatedInline,
                MediaItemTranscodedInline,
                MediaItemMarkerInline]

    def get_urls(self):
        urls = super(MediaItemAdmin, self).get_urls()
        my_urls = [
            url(r'^gener_csv/$', AdminView().generate_items_csv, name="telemeta-items-csv"),
            url(r'^gener_csv/apply/$', AdminView().valid_attr_form, name="telemeta-items-csv-apply"),
            url(r'^gener_csv/progress/(?P<task_id>[A-Za-z0-9-]+)/$', AdminView().progress_task, name="telemeta-items-csv-progress"),
            url(r'^gener_csv/correction/$', AdminView().get_correction_form, name="telemeta-items-csv-correction"),
            url(r'^gener_csv/correction/apply/$', AdminView().apply_correction, name="telemeta-items-csv-correction-apply"),
        ]
        return my_urls + urls

class MediaPartAdmin(admin.ModelAdmin):
    search_fields = ['title', 'item__code']
    ordering = ['title']

class InstrumentAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

class InstrumentAliasAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

class InstrumentRelationAdmin(admin.ModelAdmin):
    search_fields = ['instrument__name', 'parent_instrument__name']
    ordering = ['parent_instrument__name']

class InstrumentAliasRelationAdmin(admin.ModelAdmin):
    search_fields = ['alias__name', 'instrument__name']
    ordering = ['alias__name']

class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

class LocationAliasAdmin(admin.ModelAdmin):
    search_fields = ['location__name', 'alias']
    ordering = ['alias']

class LocationRelationAdmin(admin.ModelAdmin):
    search_fields = ['location__name', 'ancestor_location__name']
    ordering = ['ancestor_location__name']

class LanguageAdmin(admin.ModelAdmin):
    search_fields = ['name', 'identifier']
    ordering = ['name']

class RevisionAdmin(admin.ModelAdmin):
    search_fields = ['element_id', 'user']
    ordering = ['-time']

class FormatAdmin(admin.ModelAdmin):
    search_fields = ['original_code', 'tape_reference']

class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]

class PlaylistAdmin(admin.ModelAdmin):
    search_fields = ['title', 'public_id']

admin.site.register(MediaFonds, MediaFondsAdmin)
admin.site.register(MediaCorpus, MediaCorpusAdmin)
admin.site.register(MediaCollection, MediaCollectionAdmin)
admin.site.register(MediaItem, MediaItemAdmin)
admin.site.register(MediaPart, MediaPartAdmin)

admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(InstrumentAlias, InstrumentAliasAdmin)
admin.site.register(InstrumentRelation, InstrumentRelationAdmin)
admin.site.register(InstrumentAliasRelation, InstrumentAliasRelationAdmin)

admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
admin.site.register(LocationAlias, LocationAliasAdmin)
admin.site.register(LocationRelation, LocationRelationAdmin)

admin.site.register(Language, LanguageAdmin)

admin.site.register(Revision, RevisionAdmin)

admin.site.register(Format, FormatAdmin)

admin.site.register(User, UserProfileAdmin)

admin.site.register(PublisherCollection)
admin.site.register(Playlist, PlaylistAdmin)
