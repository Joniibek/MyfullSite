from control.models import Profile


class ProfileCreationHandler:
    def __init__(self, name, user_id, avatar, currency_id):
        self.name = name
        self.user_id = user_id
        self.avatar = avatar
        self.currency_id = currency_id

    def handle(self) -> Profile:
        profile = Profile.objects.create(
            name=self.name,
            user_id=self.user_id,
            avatar=self.avatar,
            currency_id=self.currency_id,
        )
        return profile


class ProfileUpdateHandler:
    def __init__(self, instance, name, avatar, currency_id):
        self.instance = instance
        self.new_name = name
        self.new_avatar = avatar
        self.new_currency_id = currency_id
    
    def handle(self):
        self.instance.name = self.new_name or self.instance.name
        self.instance.avatar = self.new_avatar or self.instance.avatar
        self.instance.currency_id = self.new_currency_id or self.instance.currency_id
        self.instance.save()
        return self.instance
