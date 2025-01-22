from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import requests

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
        filter_accommodation = []
        longitude = self.request.query_params.get("longitude")
        latitude = self.request.query_params.get("latitude")
        key = 'AhKaL22nil7f0VevfVpYLr0hEEFmMQ_YaQ3dlIfTJYOfRv3Jbdufdyj0NSF6PVqr'
        if longitude and latitude:
            for item in query:
                reponse = requests.get(
                    f"https://dev.virtualearth.net/REST/v1/Routes/Driving?o=json&wp.0={latitude},{longitude}&wp.1={item.latitude},{item.longitude}&key={key}")
                data = reponse.json()
                if data.get("resourceSets")[0].get("resources")[0].get("travelDistance") < 10:
                    filter_accommodation.append(item)
            return filter_accommodation
        return query

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
                    rent_cost=data.get('rent_cost'),
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
        if self.action == 'list':
            return  [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        return {'request': self.request}


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active = True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'retrieve':
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

    # @action(methods=['POST'], detail=False, url_path='follow')
    # def follow(self, request):
    #     try:
    #         queries = self.queryset
    #         username_follow = request.query_params.get('username')
    #         user_follow = queries.get(username=username_follow)
    #         user = request.user
    #         follow, followed = Follow.objects.get_or_create(user=user, follow=user_follow)
    #         if followed:
    #             NotificationsViewSet.create_notification_follow(f'{user} started following {user_follow.username}', sender=user, user_receive=user_follow)
    #         if not followed:
    #             follow.delete()
    #             return Response(status=status.HTTP_204_NO_CONTENT)
    #         return Response(data=FollowSerializer(follow).data, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         print(f"Error: {str(e)}")
    #         return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    # @action(methods=['GET'], detail=False, url_path='follower')
    # def follower(self, request):
    #     try:
    #         user = request.user
    #         userid = User.objects.get(username=user).id
    #         followers = Follow.objects.filter(follow_id=userid)
    #         follower_array = []
    #         for follower in followers:
    #             follower_array.append(follower.user_id)
    #         dataUser = {
    #             'user': str(user),
    #             'followers': follower_array
    #         }
    #         return Response(dataUser, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print(f"Error: {str(e)}")
    #         return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    # @action(methods=['GET'], detail=False, url_path='following')
    # def following(self, request):
    #     try:
    #         user = request.user
    #         userid = User.objects.get(username=user).id
    #         following_user = Follow.objects.filter(user_id=userid)
    #         following_array = []
    #         for follower in following_user:
    #             following_array.append(follower.follow_id)
    #         dataUser = {
    #             'user': str(userid),
    #             'following': following_array
    #         }
    #         return Response(dataUser, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print(f"Error: {str(e)}")
    #         return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_context(self):
        return {'request': self.request}


class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list']:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(methods=['POST'], detail=False, url_path='create')
    def create_post(self, request):
        try:
            user = request.user
            data = request.data
            post_instance = Post.objects.create(
                content=data.get('content'),
                user=user,
                caption=data.get('caption'),
                description=data.get('description'),
            )
            image_instance = None
            for file in request.FILES.getlist('image'):
                res = cloudinary.uploader.upload(file)
                image_url = res['secure_url']
                image_instance = ImageOfPost.objects.create(
                    image=image_url,
                    post=post_instance
                )
            # NotificationsViewSet.create_notification_post_accommodation(f'{user} added new post', user_send=user),
            return Response(data=PostSerializer(post_instance).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"Error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='post_user')
    def get_post_of_user(self, request):
        try:
            user = request.user
            userid = User.objects.get(username=user).id
            posts = Post.objects.filter(user_id=userid)
            return Response(data=PostSerializer(posts, many=True).data, status=status.HTTP_200_OK)
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

    def get_serializer_context(self):
        return {'request': self.request}

