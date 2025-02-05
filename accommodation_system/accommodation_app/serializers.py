from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'avatar_url', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        # Sử dụng URL đầy đủ từ phương thức model nếu không có request
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
        fields = '__all__'


class ImageOfPostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageOfPost
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)  # Tạo URL đầy đủ nếu có image
        return None  # Hoặc có thể trả về URL mặc định nếu không có hình ảnh

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentPostSerializer(ModelSerializer):
    reply_comment = serializers.SerializerMethodField()  # Lấy danh sách reply
    user_comment = serializers.PrimaryKeyRelatedField(source='user.id', read_only=True)  # Trả về id của người dùng bình luận
    comment_count = serializers.SerializerMethodField()  # Đếm số lượng reply

    class Meta:
        model = CommentPost
        fields = ['id', 'user_comment', 'post', 'content', 'parent_comment', 'created_date', 'reply_comment', 'comment_count']

    def get_reply_comment(self, obj):
        replies = obj.reply_comment.all()  # Lấy danh sách reply từ related_name
        return CommentPostSerializer(replies, many=True).data  # Serialize danh sách reply

    def get_comment_count(self, obj):
        return obj.reply_comment.count()  # Đếm số lượng reply

class PostSerializer(serializers.ModelSerializer):
    post_images = ImageOfPostSerializer(many=True, read_only=True, source='post_image')
    comment_count = serializers.SerializerMethodField()  # Đếm số lượng bình luận gốc
    comments = serializers.SerializerMethodField()  # Lấy danh sách bình luận gốc

    class Meta:
        model = Post
        fields = ['id', 'caption', 'content', 'created_date', 'user_id', 'post_images', 'comment_count', 'comments']

    def get_comment_count(self, obj):
        return obj.post_comment.filter(parent_comment__isnull=True).count()  # Đếm số lượng bình luận gốc

    def get_comments(self, obj):
        comments = obj.post_comment.filter(parent_comment__isnull=True)  # Lấy danh sách bình luận gốc
        return CommentPostSerializer(comments, many=True).data  # Serialize danh sách bình luận


class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class SenderSerializer(ModelSerializer):
    avatar_user = SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.get_avatar_url()
        return None
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_user']

class NotificationSerializer(ModelSerializer):
    sender = SenderSerializer()

    class Meta:
        model = Notification
        fields = '__all__'



