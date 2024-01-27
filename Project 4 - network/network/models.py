from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return self.username

class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.TextField(max_length = 500)
    # timestamp is the field used to sort posts in the database (raw data from datetime.now() is stored); fmtTime is the formatted timestamp that the end user will see, only hours & minutes are stored
    timestamp = models.CharField(max_length=24)
    fmtTime = models.CharField(max_length=24)

    def __str__(self):
        return self.post
    
    def sortCriteria(self):
        return self.timestamp
    
    def serialize(self):
        return {'id':self.id, 'author':self.user_id.username, 'body':self.post, 'time':self.fmtTime}

class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Follow(models.Model):
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'{self.follower_id} follows {self.following_id}'