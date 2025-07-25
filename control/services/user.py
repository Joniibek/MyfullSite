from control.models import User

class UserCreationHandler:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def handle(self) -> User:
        user = User.objects.create(login=self.login, password=self.password)
        return user
    
    
class UserUpdateHandler:
    def __init__(self, instance, password):
        self.instance = instance
        self.new_password = password
    
    def handle(self) -> User:
        self.instance.password = self.new_password or self.instance.password
        self.instance.save()
        return self.instance

