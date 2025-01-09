from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models.functions import TruncMonth, TruncYear, TruncQuarter

from .models import Accommodation,Post,User,ImageOfAccommodation, ImageOfPost, CommentPost, Follow, Notification

# Register your models here.

class AccommodationAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'created_date', 'description', 'address', 'price', 'is_rented', 'owner_id']
    search_fields = ['description', 'address', 'price', 'owner__username' ]
    list_filter = ['district', 'city', 'number_of_people']


class AccommodationAppAdminSite(admin.AdminSite):
    site_header = 'HE THONG TIM KIEM NHA TRO TL'

    def get_urls(self):
        return [
            path('accommodation-stats/', self.my_stats)
        ] + super().get_urls()

    def my_stats(self, request):
        # Thống kê tổng số lượng nhà trọ
        count = Accommodation.objects.filter(active=True).count()

        # Thống kê theo người dùng, bao gồm thống kê theo tháng, năm và quý
        user_stats = list(Accommodation.objects \
                          .annotate(accommodation_count=Count('owner__accommodation')) \
                          .values('owner__username', 'address', 'price', 'accommodation_count'))

        # Thống kê theo quận
        district_stats = list(Accommodation.objects
                              .values('district')
                              .annotate(accommodation_count=Count('id')))

        # Thống kê theo tháng, quý và năm
        monthly_stats = list(Accommodation.objects.annotate(month=TruncMonth('created_date'))
                             .values('month')
                             .annotate(accommodation_count=Count('id'))
                             .order_by('month'))
        yearly_stats = list(Accommodation.objects.annotate(year=TruncYear('created_date'))
                            .values('year')
                            .annotate(accommodation_count=Count('id'))
                            .order_by('year'))
        quarterly_stats = list(Accommodation.objects.annotate(quarter=TruncQuarter('created_date'))
                               .values('quarter')
                               .annotate(accommodation_count=Count('id'))
                               .order_by('quarter'))

        # Chuyển đổi dữ liệu thành JSON
        user_stats_json = json.dumps(user_stats, cls=DjangoJSONEncoder)
        district_stats_json = json.dumps(district_stats, cls=DjangoJSONEncoder)
        monthly_stats_json = json.dumps(monthly_stats, cls=DjangoJSONEncoder)
        yearly_stats_json = json.dumps(yearly_stats, cls=DjangoJSONEncoder)
        quarterly_stats_json = json.dumps(quarterly_stats, cls=DjangoJSONEncoder)

        return TemplateResponse(request, 'admin/accommodation_stats.html', {
            'user_stats_json': user_stats_json,
            'district_stats_json': district_stats_json,
            'monthly_stats_json': monthly_stats_json,
            'yearly_stats_json': yearly_stats_json,
            'quarterly_stats_json': quarterly_stats_json
        })

admin_site = AccommodationAppAdminSite('myadmin')

admin_site.register(Accommodation , AccommodationAdmin)
admin_site.register(Post)
admin_site.register(User, UserAdmin)
admin_site.register(ImageOfPost)
admin_site.register(ImageOfAccommodation)
admin_site.register(CommentPost)
admin_site.register(Follow)
admin_site.register(Notification)