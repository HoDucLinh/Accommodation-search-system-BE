from rest_framework.serializers import ModelSerializer
from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id' , 'first_name', 'last_name', 'username', 'password', 'email', 'avatar']
        extra_kwargs = {
            'password': {'write_only':'true'}
        }

    def create(self, validated_data):
        u = User(**validated_data)
        u.set_password(validated_data['password'])
        u.save()
        return u


class ImageAccommodationSerializer(ModelSerializer):
    class Meta:
        model = ImageOfAccommodation
        fields = ['id', 'image']


class AccommodationSerializer(ModelSerializer):
    accommodation_images = ImageAccommodationSerializer(many=True, read_only=True, source='accommodation_image')

    class Meta:
        model = Accommodation
        fields = ['id', 'owner', 'address', 'created_date', 'price', 'description', 'is_rented', 'accommodation_images']


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'caption', 'content', 'created_date', 'user_id']


