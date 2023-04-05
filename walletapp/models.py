from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    user_data = ((1,"Premium_User"), (2, "Non-Premium_User"))
    user_type = models.CharField(max_length=20, choices=user_data,)

    class Meta:
        verbose_name_plural = 'User Detail'

class Premium_User(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
   

    class Meta:
        verbose_name_plural = 'Premium User'

    def __str__(self):
        return self.user.username
    
class Non_Premium_User(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
   

    class Meta:
        verbose_name_plural = 'Non-Premium User'

    def __str__(self):
        return self.user.username

class Wallet(models.Model):
    """Model definition for Wallet."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Wallet."""

        verbose_name_plural = 'Wallet'

    def __str__(self):
        """Unicode representation of Wallet."""
        return self.user.username


class Transaction(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=200, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    trans_types = (('Credited', 'Credited'),
                   ('Debited', 'Debited')) 
    transaction_type = models.CharField(max_length=20, choices=trans_types, default='Credited')
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status_type = (('Accepted', 'Accepted'),
                   ('Rejected', 'Rejected'),
                   ('N/A', 'N/A'),
                   ('Success', 'Success'))
    status = models.CharField(max_length=20, choices=status_type, default='Success')
    is_request = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Transaction."""

        verbose_name_plural = 'Transactions'

    def __str__(self):
        """Unicode representation of Transaction."""
        return self.user.username






@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type==1:
            Premium_User.objects.create(user=instance)
            Wallet.objects.create(user=instance, balance=2500)
        if instance.user_type==2:
            Non_Premium_User.objects.create(user=instance)
            Wallet.objects.create(user=instance, balance=1000)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type==1:
        instance.premium_user.save()
    if instance.user_type==2:
        instance.non_premium_user.save()
