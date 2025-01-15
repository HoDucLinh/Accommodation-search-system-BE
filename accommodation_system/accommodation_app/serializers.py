from rest_framework.serializers import ModelSerializer
from .models import *
import cloudinary.uploader
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'avatar_url']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        u = User(**validated_data)
        u.set_password(validated_data['password'])
        u.save()
        return u

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if self.context.get('action') == 'create':
            self.fields.pop('avatar_url')
        else:
            self.fields.pop('avatar') # ẩn field avatar


class ImageAccommodationSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageOfAccommodation
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            # Nếu image đã lưu là path, bạn cần thêm domain Cloudinary vào
            full_url = request.build_absolute_uri(obj.image.url)
            return full_url
        return None



class AccommodationSerializer(ModelSerializer):
    accommodation_images = ImageAccommodationSerializer(many=True, read_only=True, source='accommodation_image')

    class Meta:
        model = Accommodation
        fields = ['id', 'owner', 'address', 'created_date', 'price', 'description', 'is_rented', 'accommodation_images']


class ImageOfPostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageOfPost
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class PostSerializer(serializers.ModelSerializer):
    post_images = ImageOfPostSerializer(many=True, read_only=True, source='post_image')

    class Meta:
        model = Post
        fields = ['id', 'caption', 'content', 'created_date', 'user_id', 'post_images']
