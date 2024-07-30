from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your model here.

@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('name', 'title','creator', 'status','occupation','date')
    search_fields = ('name', 'title', 'status', 'creator')
    list_filter = ('status', 'occupation', 'postgraduate_type', 'is_secure','creator')
    readonly_fields = ('creator','date',)

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('project', 'description')
    search_fields = ('project__name', 'description')

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'email')
    search_fields = ('name', 'project__name', 'email')


@admin.register(NewsAndEvents)
class NewsAndEventsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'news_item', 'event_item')
    search_fields = ('title',)
    list_filter = ('news_item', 'event_item')
    
@admin.register(PayPalPayment)
class PayPalPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'amount', 'status', 'created_at')
    search_fields = ('payment_id', 'user__username', 'status')
    list_filter = ('status', 'created_at')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'is_active')
    search_fields = ('user__username',)
    list_filter = ('end_date',)
    readonly_fields = ('is_active',)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    

class FeaturedResearcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'image_thumbnail')
    search_fields = ('name', 'specialization')
    list_filter = ('specialization',)
    readonly_fields = ('image_thumbnail',)
    fields = ('name', 'specialization', 'image', 'image_thumbnail')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius:50%;" />'.format(obj.image.url))
        return ""
    image_thumbnail.short_description = 'Image'

admin.site.register(FeaturedResearcher, FeaturedResearcherAdmin)