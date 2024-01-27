from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=24, unique=True)

    def __str__(self):
        return self.category

class Listing(models.Model):
    title = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=280)
    startingBid = models.FloatField()
    image = models.CharField(max_length=120, blank=True)
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    open = models.BooleanField()
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ownedListings")
    winner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wonListings", null=True, blank=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="placedBid")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="price")
    bid = models.FloatField()

    def __str__(self):
        return f"${self.bid:.2f}"

class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")
    comment = models.CharField(max_length=140)

    def __str__(self):
        return self.comment
    
class WatchList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)


