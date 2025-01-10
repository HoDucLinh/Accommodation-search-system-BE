from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from .serializers import *

# Create your views here.

def index(request):
    return render(request, template_name='index.html', context={'name':'Accomodation App'})

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.filter(active = True)
    serializer_class = AccommodationSerializer

    #xem ds thi ai cung xem duoc , nhung cac action khac thi phai dang nhap
    def get_permissions(self):
        if self.action == 'list':
            return  [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active = True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(active = True)
    serializer_class = PostSerializer

    @action(detail=True, methods=['get', 'post'])
    def hide_post(self, request, pk=None):
        if request.method == 'POST':
            try:
                p = Post.objects.get(pk=pk)
                p.active = False
                p.save()
                serializer = self.get_serializer(p, context={'request' : request})
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

