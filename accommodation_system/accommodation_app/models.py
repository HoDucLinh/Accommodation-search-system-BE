from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db import models


class Role(models.TextChoices):
    TENANT = "TENANT", ('Người thuê')
    ADMIN = 'ADMIN', ('Quản trị viên')
    HOST = 'HOST', ('Chủ nhà')


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    description = models.TextField(null=True , blank=True)

    class Meta:
        abstract = True

class Interaction(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = CloudinaryField('avatar', null = False)
    role = models.CharField(max_length=6, choices=Role.choices, null=False)

class Accommodation(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='accommodation' , null=True)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    number_of_people = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveIntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, choices=[(True, 'Verified'), (False, 'Not Verified')])
    is_rented = models.BooleanField(default=False, choices=[(True, 'Rented'), (False, 'Not Rent')])
    def __str__(self):
        return f'Accommodation_{self.owner.username}'


class ImageOfAccommodation(BaseModel):
    image = CloudinaryField('imageOfAccommodation', null=True, blank=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="accommodation_image")

    def __str__(self):
        return f'Image_of_{self.accommodation_id}'

class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post')
    content = models.TextField()
    caption = models.TextField(null=True)

    def __str__(self):
        return f'Post_user_{self.user.id}'

class ImageOfPost(BaseModel):
    image = CloudinaryField('image', null=True, blank=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="post_image")

    def __str__(self):
        return f'Image_of_{self.post_id}'

class CommentPost(Interaction):
    content = models.TextField()
    parent_comment = models.ForeignKey('CommentPost', on_delete=models.CASCADE, related_name='reply_comment', null=True, blank=True)

    def __str__(self):
        return f'Comment_post_{self.post.id}'


class Follow(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='follower')
    follow = models.ForeignKey('User', on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'{self.user} follow {self.follow}'

class Notification(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification_for_{self.recipient.username}'