from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import requests
import cloudinary
import cloudinary.uploader
from django.db.models import Q
from .utils import sendEmail

# Create your views here.

def index(request):
    return render(request, template_name='index.html', context={'name':'Accomodation App'})

class AccommodationViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Accommodation.objects.all().order_by('-id')
    serializer_class = AccommodationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        query = self.queryset
        district = self.request.query_params.get("district")
        city = self.request.query_params.get("city")
        longitude = self.request.query_params.get("longitude")
        latitude = self.request.query_params.get("latitude")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        number_of_people = self.request.query_params.get("number_of_people")
        key = 'AhKaL22nil7f0VevfVpYLr0hEEFmMQ_YaQ3dlIfTJYOfRv3Jbdufdyj0NSF6PVqr'

        # Lọc theo quận/huyện và thành phố
        if district:
            query = query.filter(district__icontains=district)
        if city:
            query = query.filter(city__icontains=city)

        # Lọc theo số người
        if number_of_people:
            query = query.filter(number_of_people=number_of_people)

        # Lọc theo giá
        if min_price and max_price:
            query = query.filter(price__gte=min_price, price__lte=max_price)
        elif min_price:
            query = query.filter(price__gte=min_price)
        elif max_price:
            query = query.filter(price__lte=max_price)

        # Lọc theo khoảng cách nếu có tọa độ
        if longitude and latitude:
            filter_accommodation = []
            for item in query:
                response = requests.get(
                    f"https://dev.virtualearth.net/REST/v1/Routes/Driving?o=json&wp.0={latitude},{longitude}&wp.1={item.latitude},{item.longitude}&key={key}"
                )
                data = response.json()
                if data.get("resourceSets")[0].get("resources")[0].get("travelDistance") < 10:
                    filter_accommodation.append(item)
            return filter_accommodation

        return query

    @action(methods=['GET'], detail=False, url_path='search')
    def search_accommodation(self, request):
        queryset = self.get_queryset()

        # Áp dụng phân trang
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AccommodationSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = AccommodationSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='create')
    def create_accommodation(self, request):
        try:
            user = request.user
            data = request.data
            if user.role in ['HOST']:
                if len(request.FILES.getlist('image')) < 3:
                    return Response({"Error": "You must upload at least THREE image"}, status=status.HTTP_400_BAD_REQUEST)
                accommodation = Accommodation.objects.create(
                    owner=user,
                    address=data.get('address'),
                    district=data.get('district'),
                    city=data.get('city'),
                    number_of_people=data.get('number_of_people'),
                    description = data.get('description'),
                    price=data.get('price'),
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude'),
                )
                for file in request.FILES.getlist('image'):
                    res = cloudinary.uploader.upload(file)
                    image_url = res['secure_url']
                    ImageOfAccommodation.objects.create(
                        image=image_url,
                        accommodation=accommodation
                    )
                return Response(data=AccommodationSerializer(accommodation, context={'request': request}).data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'Error': 'You must be HOST'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=True, url_path='detail')
    def detail_accommodation(self, request, pk):
        try:
            return Response(data=AccommodationSerializer(Accommodation.objects.get(pk=pk), context={'request': request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='accommodation_user')
    def get_accommodations_user(self, request):
        try:
            user = request.user
            userid = User.objects.get(username=user).id
            accommodations = Accommodation.objects.filter(owner=userid)
            return Response(data=AccommodationSerializer(accommodations, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='verified')
    def accommodation_is_verified(self, request):
        try:
            accommodation = self.queryset.filter(is_verified=True)
            return Response(data=AccommodationSerializer(accommodation, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='not_verified')
    def accommodation_not_verified(self, request):
        try:
            accommodation = self.queryset.filter(is_verified=False)
            return Response(data=AccommodationSerializer(accommodation, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #xem ds thi ai cung xem duoc , nhung cac action khac thi phai dang nhap
    def get_permissions(self):
        if self.action in ['list','search_accommodation']:
            return  [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        return {'request': self.request}


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active = True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in [ 'follow', 'unfollow']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


    def get_serializer_context(self):
        return {'request': self.request}

    @action(methods=['PATCH'], detail=True, url_path='update')
    def update_user(self, request, pk):
        try:
            data = request.data
            user_instance = self.get_object()

            for key, value in data.items():
                setattr(user_instance, key, value)
            if data.get('avatar_user') is None:
                pass
            else:
                avatar_file = data.get('avatar_user')
                res = cloudinary.uploader.upload(avatar_file)
                user_instance.avatar_user = res['secure_url']
            user_instance.save()
            return Response(data=UserSerializer(user_instance, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], url_path='current_user', url_name='current_user', detail=False)
    def current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_path='follow')
    def follow(self, request):
        try:
            queries = self.queryset
            username_follow = request.query_params.get('username')
            user_follow = queries.get(username=username_follow)
            user = request.user
            follow, followed = Follow.objects.get_or_create(user=user, follow=user_follow)
            if followed:
                NotificationsViewSet.create_notification_follow(f'{user} started following {user_follow.username}', sender=user, user_receive=user_follow)
            if not followed:
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(data=FollowSerializer(follow).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path='unfollow')
    def unfollow(self, request):
        try:
            username_unfollow = request.query_params.get('username')
            if not username_unfollow:
                return Response({"Error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

            user_unfollow = self.queryset.get(username=username_unfollow)
            user = request.user

            follow = Follow.objects.filter(user=user, follow=user_unfollow).first()
            if follow:
                follow.delete()
                return Response({"message": f"You have unfollowed {user_unfollow.username}"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='follower')
    def follower(self, request):
        try:
            user = request.user
            userid = User.objects.get(username=user).id
            followers = Follow.objects.filter(follow_id=userid)
            follower_array = []
            for follower in followers:
                follower_array.append(follower.user_id)
            dataUser = {
                'user': str(user),
                'followers': follower_array
            }
            return Response(dataUser, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='following')
    def following(self, request):
        try:
            user = request.user
            userid = User.objects.get(username=user).id
            following_user = Follow.objects.filter(user_id=userid)
            following_array = []
            for follower in following_user:
                following_array.append(follower.follow_id)
            dataUser = {
                'user': str(userid),
                'following': following_array
            }
            return Response(dataUser, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search_posts', 'get_comments']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]  # Thêm phần này để xử lý các trường hợp khác
        return [permission() for permission in permission_classes]

    @action(methods=['POST'], detail=False, url_path='create')
    def create_post(self, request):
        try:
            user = request.user
            data = request.data

            if not data.get('content'):
                return Response({"Error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

            post_instance = Post.objects.create(
                content=data.get('content'),
                user=user,
                caption=data.get('caption'),
                description=data.get('description'),
            )

            image_files = request.FILES.getlist('image')
            if not image_files:
                return Response({"Error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

            uploaded_images = []  # Danh sách lưu ảnh đã tải lên

            for file in image_files:
                try:
                    res = cloudinary.uploader.upload(file)
                    image_url = res['secure_url']
                    image_instance = ImageOfPost.objects.create(image=image_url, post=post_instance)
                    uploaded_images.append(image_instance)

                except Exception as e:
                    print(f"Cloudinary upload error: {str(e)}")
                    return Response({"Error": "Image upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Gọi hàm gửi thông báo (chỉ gọi một lần sau khi hoàn thành vòng lặp)
            notification_result = NotificationsViewSet.create_notification_post_accommodation(
                f'{user} added new post', user_send=user
            )

            return Response(
                {
                    "post": PostSerializer(post_instance, context={'request': request}).data,
                    "notification": notification_result
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(methods=['GET'], detail=False, url_path='post_user')
    def get_post_of_user(self, request):
        try:
            user = request.user
            userid = User.objects.get(username=user).id
            posts = Post.objects.filter(user_id=userid)
            return Response(data=PostSerializer(posts, many=True, context={'request': request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='approved')
    def get_approved_posts(self, request):
        try:
            posts = self.queryset.filter(is_approved=True)
            return Response(data=PostSerializer(posts, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='not_approved')
    def get_posts_not_approved(self, request):
        try:
            posts = self.queryset.filter(is_approved=False)
            return Response(data=PostSerializer(posts, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['PUT'],detail=True,url_path="edit_approved")
    def edit_approved(self, request, pk):
        try:

            instance = self.get_object()
            instance.is_approved = True
            instance.save()

            return Response({"message": "Successfully updated"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get', 'post'])
    def hide_post(self, request, pk=None):
        if request.method == 'POST':
            try:
                p = Post.objects.get(pk=pk)
                p.active = False
                p.save()
                serializer = self.get_serializer(p, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Post.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            try:
                p = Post.objects.get(pk=pk)
                serializer = self.get_serializer(p)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Post.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=False, url_path='search')
    def search_posts(self, request):
        try:
            query = request.query_params.get('search', '').strip()
            if not query:
                return Response({"Error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)

            posts = self.queryset.filter(
                Q(content__icontains=query) | Q(user__username__icontains=query)
            ).distinct()

            # Áp dụng phân trang mặc định từ settings.py
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = PostSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=True, url_path='comment')
    def add_comment(self, request, pk):
        try:
            post_instance = self.get_object()
            user = request.user
            content = request.data.get('content')
            if user != post_instance.user:
                NotificationsViewSet.create_notification_comment_post_accommodation(post_or_accommodation=post_instance, sender=user)

            if not content:
                return Response({"Error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

           # Tạo bình luận mới
            comment = CommentPost.objects.create(
                user=user,  # Đảm bảo sử dụng đúng tên field
                post=post_instance,
                content=content
            )

            # Trả về bình luận vừa tạo
            return Response(CommentPostSerializer(comment).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        try:
            post_instance = self.get_object()
            comments = post_instance.post_comment.filter(parent_comment__isnull=True)  # Lấy bình luận gốc

            return Response(CommentPostSerializer(comments, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_serializer_context(self):
        return {'request': self.request}

class CommentPostViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = CommentPost.objects.filter(parent_comment__isnull=True)
    serializer_class = CommentPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]  # Thêm phần này để xử lý các trường hợp khác
        return [permission() for permission in permission_classes]

    @action(methods=['POST'], detail=True, url_path='reply')
    def add_reply_comment(self, request, pk):
        try:
            user = request.user
            parent_comment = CommentPost.objects.get(pk=pk)
            post_instance = Post.objects.get(pk=parent_comment.post_id)
            if user != post_instance.user_post:
                NotificationsViewSet.create_notification_comment_post_accommodation(post_or_accommodation=post_instance, sender=user)
            return Response(data=CommentPostSerializer(
                CommentPost.objects.create(
                    user_comment=user,
                    post=post_instance,
                    text=request.data.get('content'),
                    parent_comment=parent_comment
                )
            ).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationsViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        try:
            user = self.request.user
            userid = user.id  # Assuming user is already an instance of User model
            notifications = self.queryset.filter(recipient_id=userid)
            return notifications
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_notification_follow(notification, sender, user_receive):
        try:
            Notification.objects.create(message=notification, sender=sender, recipient=user_receive)
            sendEmail(notification, recipients=[user_receive.email])
            return Response({"message": "Notification created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_notification_post_accommodation(notification, user_send):
        try:
            user_send = User.objects.get(username=user_send)
            user_follow_user_send = Follow.objects.filter(follow_id=user_send.id)
            recipients_array = []

            for user in user_follow_user_send:
                recipient = User.objects.get(pk=user.user_id)
                Notification.objects.create(message=notification, sender=user_send, recipient=recipient)
                recipients_array.append(recipient.email)

            sendEmail(notification, recipients=recipients_array)

            # Ghi log kết quả để debug
            print("Notification created successfully")
            return {"message": "Notification created successfully"}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {"Error": "Server error"}

    def create_notification_comment_post_accommodation(post_or_accommodation, sender):
        try:
            user_send = User.objects.get(username=sender)
            notification = None
            user_receive = None
            if isinstance(post_or_accommodation, Post):
                notification = f'{sender} commented your post'
                user_receive = Post.objects.get(id=post_or_accommodation.id).user_post
            elif isinstance(post_or_accommodation, Accommodation):
                notification = f'{sender} commented your post accommodation'
                user_receive = Accommodation.objects.get(id=post_or_accommodation.id).owner
            Notification.objects.create(message=notification, sender=user_send, recipient=User.objects.get(username=user_receive))
            return Response({"message": "Notification created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path="notification_user")
    def user_notifications(self, request):
        try:
            user = self.request.user
            userid = User.objects.get(username=user).id
            notifications = self.queryset.filter(recipient_id=userid)
            serializer = self.serializer_class(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
