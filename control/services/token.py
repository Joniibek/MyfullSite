from rest_framework_simplejwt.tokens import RefreshToken



class TokenCreationHandle:
    def __init__(self, user):
        self.user = user

    def handle(self) -> tuple[str, str]:
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        return str(access), str(refresh)        

    def h(self):
        re = self.handle()
        re[3]

