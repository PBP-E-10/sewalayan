from django.contrib import admin
from review.models import Review, Report

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'order', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'order', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('description', 'reporter__username')
    actions = ['tandai_ditinjau', 'ban_terlapor', 'tolak_dan_aktifkan_barang']

    @admin.action(description='Tandai sedang ditinjau')
    def tandai_ditinjau(self, request, queryset):
        queryset.update(status='in_review')

    @admin.action(description='Ban pengguna yang dilaporkan & selesaikan laporan')
    def ban_terlapor(self, request, queryset):
        for report in queryset:
            user = report.reported_user
            user.is_active = False
            user.save()
            report.status = 'resolved'
            report.save()

    @admin.action(description='Tolak laporan & aktifkan kembali barang')
    def tolak_dan_aktifkan_barang(self, request, queryset):
        for report in queryset:
            report.status = 'rejected'
            report.save()
            item = report.order.item
            item.is_available = True
            item.save()