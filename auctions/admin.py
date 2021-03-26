from django.contrib import admin

# Register your models here.
from . models import User, Product, Bid, Comment, UserWatchlist

admin.site.register(Product)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(UserWatchlist)
admin.site.register(User)