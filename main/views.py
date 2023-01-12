from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Category, Post, Comment, Like, Favorites
from . import serializers
from .permissions import IsAuthorOrAdmin, IsAuthor, IsAuthorOrAdminOrPostOwner


class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class CommentCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def get_permissions(self):

        if self.request.method in ('PUT', 'PATCH'):
            return [permissions.IsAuthenticated(), IsAuthor()]
        elif self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsAuthorOrAdminOrPostOwner()]
        return [permissions.AllowAny()]


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('title',)
    filterset_fields = ('owner', 'category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateSerializer
        return serializers.PostDetailSerializer

    def get_permissions(self):
        # Удалять может только админ или автор поста
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]
        # Обновлять может только автор поста
        elif self.action in ('update', 'partial_update'):
            return [permissions.IsAuthenticated(), IsAuthor()]
        # Просматривать могут все, но создавать только аутентифицированный пользователь
        return [permissions.IsAuthenticatedOrReadOnly()]

    # ...api/v1/posts/<id>/favorites/
    @action(['POST', 'DELETE'], detail=True)
    def favorites(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.favorites.filter(post=post).exists():
                return Response('This post is already in favorites!', status=400)
            Favorites.objects.create(owner=user, post=post)
            return Response('Added to favorites!', status=201)
        else:
            if user.favorites.filter(post=post).exists():
                user.favorites.filter(post=post).delete()
                return Response('Deleted from favorites!', status=204)
            return Response('Post is not found!', status=404)

    # ...api/v1/posts/5/comments/
    @action(['GET'], detail=True)
    def comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.all()
        serializer = serializers.CommentSerializer(instance=comments, many=True)
        return Response(serializer.data, status=200)

    @action(['GET'], detail=True)
    def get_likes(self, request, pk):
        post = self.get_object()
        likes = post.likes.all()
        serializer = serializers.LikeSerializer(instance=likes, many=True)
        return Response(serializer.data, status=200)

    # ...api/v1/posts/<int:pk>/like/
    @action(['POST', 'DELETE'], detail=True)
    def like(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.liked_posts.filter(post=post).exists():
                return Response('This post is already liked!', status=400)
            Like.objects.create(owner=user, post=post)
            return Response('You liked the post!', status=201)
        elif request.method == 'DELETE':
            if not user.liked_posts.filter(post=post).exists():
                return Response('You didn\'t like this post!', status=400)
            user.liked_posts.filter(post=post).delete()
            return Response('Your like is deleted!', status=204)


class LikeCreateView(generics.CreateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.LikeSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LikeDeleteView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    permissions_classes = (permissions.IsAuthenticated, IsAuthor)


class FollowedUserPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandartResultPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        followings = request.user.followers.all()
        users = [user.following for user in followings]
        res = queryset.filter(owner__in=users)
        # for post in queryset:
        #     if post.owner in users:
        #         res.append(post)
        serializer = serializers.PostListSerializer(instance=res, many=True, context={'request': request})
        return Response(serializer.data, status=200)


# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return serializers.PostListSerializer
#         return serializers.PostCreateSerializer
#
#
# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#
#     def get_permissions(self):
#         if self.request.method == 'DELETE':
#             return permissions.IsAuthenticated(), IsAuthorOrAdmin()
#         elif self.request.method in ('PUT', 'PATCH'):
#             return permissions.IsAuthenticated(), IsAuthor()
#         return permissions.AllowAny(),
#
#     def get_serializer_class(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return serializers.PostCreateSerializer
#         return serializers.PostDetailSerializer



