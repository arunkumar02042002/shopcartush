from django.db import models
from django.db.models.query import QuerySet
from authentication.models import User

class CustomerSupportManager(models.Manager):
    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(is_custumer_support_user=True)

# Create your models here.
class CustomerSupportUser(User):
    '''
    This class inherits the property from the User model and it uses everything from the user itself.
    '''
    # It will use the above 'CustomerSupportManager' to query the database.
    objects = CustomerSupportManager()

    class Meta:
        '''
        This model will act as a proxy model.
        The table for this model will not be created in the database.
        '''
        proxy = True

    @property
    def showAdditional(self):
        '''
        If we want to add some extra logics. Add here!
        '''
        return self.customer_support_additional

class CustomerSupportUserDetail(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_support_additional")
    # add any other extra field here related to customer support user