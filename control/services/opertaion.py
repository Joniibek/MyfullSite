from control.models import Operation

class OperationCreationHandler:
      def __init__(self, profile_id: int, amount: int, comment: str, category_id: int):
            self.amount = amount
            self.profile_id = profile_id
            self.comment = comment
            self.category_id = category_id

      def handle(self) -> Operation:
        operation = Operation.objects.create(
            profile_id=self.profile_id,
            category_id= self.category_id,
            amount=self.amount,
            comment=self.comment,
        )
        return operation


class OperationUpdateHandler:
      def __init__(self, instance, new_amount: int, new_comment: str):
            self.instance = instance
            self.new_amount = new_amount
            self.new_comment = new_comment

      def handle(self) -> Operation:
            self.instance.amount = self.new_amount or self.instance.amount
            self.instance.comment = self.new_comment or self.instance.comment
            self.instance.save()
            return self.instance
      

    

        