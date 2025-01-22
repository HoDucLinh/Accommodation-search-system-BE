from rest_framework.serializers import ModelSerializer
from .models import *
import cloudinary.uploader
from rest_framework import serializers
from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'avatar_url']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # def create(self, validated_data):
    #     password = validated_data.pop('password')  # Lấy và xóa mật khẩu khỏi validated_data
    #     user = User(**validated_data)  # Tạo đối tượng User mà chưa có mật khẩu
    #     user.set_password(password)  # Băm mật khẩu trước khi lưu
    #     user.save()  # Lưu người dùng với mật khẩu đã băm
    #     return user

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.get_avatar_url()
        return None


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
