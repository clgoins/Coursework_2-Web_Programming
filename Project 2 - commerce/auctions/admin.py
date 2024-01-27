from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["title", "creator_id", "winner_id", "category_id", "open"]
    list_filter = ["creator_id", "winner_id", "category_id", "open"]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ["listing_id", "bid", "user_id"]
    list_filter = ["bid", "user_id"]

@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ["user_id", "listing_id"]
    list_filter = ["user_id", "listing_id"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["listing_id", "comment", "user_id"]
    list_filter = ["listing_id", "user_id"]

