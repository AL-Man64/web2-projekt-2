from django.db import models

from w2p2_app import vulnerability


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self) -> str:
        return self.username

    @staticmethod
    def find_by_username_and_password(username: str, password: str) -> User | None:
        if vulnerability.app_is_vulnerable():
            users = list(
                User.objects.raw(f"""
                    SELECT *
                    FROM w2p2_app_user
                    WHERE username = '{username}'
                        AND password = '{password}'
                """)  # noqa: S608
            )

            if not users:
                return None

            user = users[0]

        else:
            try:
                user = User.objects.get(username=username, password=password)
            except User.DoesNotExist:
                return None

        return user


class BookmarkedAlbum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album_title = models.CharField(max_length=100)
    album_author = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'album_title', 'album_author'],
                name='unique_user_album_title_album_author',
            )
        ]

    def __str__(self) -> str:
        return f'{self.album_title} - {self.album_author}'
