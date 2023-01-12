from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey('auth.User', related_name='followers', on_delete=models.CASCADE)
    following = models.ForeignKey('auth.User', related_name='followings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower} ---> {self.following}'
