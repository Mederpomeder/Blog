from rest_framework import serializers
from django.contrib.auth.models import User

from account.models import Follow
from main.serializers import CommentSerializer, LikeSerializer, LikedPostsSerializer, UsersCommentSerializer, \
    FavoritePostsSerializer


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

    def is_followed(self, req_user, detail_user):
        return req_user.followers.filter(following=detail_user).exists()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # print(instance, '!!!!!!!')
        # print()
        # print(rep, '11111111')
        rep['comments'] = UsersCommentSerializer(instance.comments.all(), many=True).data
        rep['liked_posts'] = LikedPostsSerializer(instance=instance.liked_posts.all(), many=True).data
        rep['favorite_posts'] = FavoritePostsSerializer(instance=instance.favorites.all(), many=True).data
        user = self.context['request'].user
        rep['is_followed'] = self.is_followed(user, instance)
        return rep


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password_confirmation = serializers.CharField(min_length=8, write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirmation')

    def validate(self, attrs):
        password2 = attrs.pop('password_confirmation')
        if password2 != attrs['password']:
            raise serializers.ValidationError('Passwords didn\'t match!')
        if not attrs['first_name'].istitle():
            raise serializers.ValidationError('Name must start with uppercase letter!')
        if not attrs['last_name'].istitle():
            raise serializers.ValidationError('Lastname must start with uppercase letter!')
        return attrs

    def create(self, validated_data):
        #     user = User.objects.create(
        #         username=validated_data['username'],
        #         first_name=validated_data['first_name'],
        #         last_name=validated_data['last_name'],
        #         email=validated_data['email'],
        #     ) # вручную
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class FollowersSerializer(serializers.ModelSerializer):
    follower_username = serializers.ReadOnlyField(source='follower.username')

    class Meta:
        model = Follow
        exclude = ('following',)


class FollowingsSerializer(serializers.ModelSerializer):
    follower_username = serializers.ReadOnlyField(source='following.username')

    class Meta:
        model = Follow
        exclude = ('follower',)
