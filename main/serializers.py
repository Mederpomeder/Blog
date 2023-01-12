from rest_framework import serializers
from .models import Category, Post, Comment, PostImages, Like, Favorites


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = '__all__'


class PostDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    # images = PostImageSerializer(many=True) # 2nd way
    # comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        rep['comments_count'] = instance.comments.count()
        # rep['comments_count'] = len(rep['comments'])
        rep['images'] = PostImageSerializer(instance.images.all(), many=True).data
        rep['likes_count'] = instance.likes.count()
        rep['liked_users'] = LikeSerializer(instance=instance.likes.all(), many=True).data
        return rep


class PostListSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    def create(self, validated_data):
        # print(self, '!!!')
        # print(validated_data, '!!!!')
        request = self.context.get('request')
        post = Post.objects.create(**validated_data)
        # print(request.FILES.getlist('images'), '!!!!!!!!!!!!!')
        images_data = request.FILES.getlist('images')
        for image in images_data:
            PostImages.objects.create(image=image, post=post)
        return post

    class Meta:
        model = Post
        fields = ('id', 'title', 'owner', 'owner_username', 'category_name', 'preview', 'images')

    def is_liked(self, post, user):
        return user.liked_posts.filter(post=post).exists()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['likes_count'] = instance.likes.count()
        user = self.context['request'].user
        if user.is_authenticated:
            rep['is_liked'] = self.is_liked(instance, user)
        return rep


class PostCreateSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'preview', 'images')


class CommentSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = '__all__'


class UsersCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'body', 'post', 'created_at')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['post_title'] = instance.post.title
        return repr


class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Like
        fields = '__all__'

    def validate_data(self, attrs):
        request = self.context['request']
        user = request.user
        post = attrs['post']
        if post.likes.filter(owner=user).exists():
            raise serializers.ValidationError('You already liked post!')
        # if user.liked_posts.filter(post=post).exists():
        #    raise serializers.ValidationError('You already liked post!')
        return attrs


class LikedPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['post_title'] = instance.post.title
        # repr['post_preview'] = Like.post.preview
        preview = instance.post.preview
        # print(preview.url, '!!!!!!!!!!!!')
        repr['post_preview'] = preview.url
        return repr


class FavoritePostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ('id', 'post')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['post_title'] = instance.post.title
        # repr['post_preview'] = Like.post.preview
        preview = instance.post.preview
        # print(preview.url, '!!!!!!!!!!!!')
        repr['post_preview'] = preview.url
        return repr