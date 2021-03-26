from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Product(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64, default="None")
    image_url = models.TextField(default="None")
    starting_bid = models.FloatField(default=0)
    highest_bid = models.FloatField(default=0)
    # username_created = models.CharField(max_length=64, default="None")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status_of_listing = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}: {self.title}: {self.description} : {self.category} : {self.image_url} : {self.starting_bid}: {self.highest_bid}: {self.user.username}: {self.status_of_listing}"
     

class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bid_product")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    bid_price = models.FloatField()
    
    def __str__(self):
        return f"{self.id} : {self.product.title} : {self.bid_price}: {self.user}"


class Comment(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comment_product")
    comment = models.TextField()
    commented_on = models.IntegerField(default=-1)
    commented_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")

    def __str__(self):
        return f"{self.id}: {self.user.username} :{self.product.title}: {self.comment}: {self.commented_on} :{self.commented_time}"

# class Watchlist(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    item = models.ManyToManyField(Product)
#    def __str__(self):
#        return f"{self.user}'s WatchList"

class UserWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist", default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_watchlist")
    # item_id = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} : {self.product.title}"