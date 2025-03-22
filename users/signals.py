from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        try:
            profile = UserProfile.objects.create(user=instance)
            logger.info(f"Created UserProfile for user {instance.email}, profile ID: {profile.id}")
        except Exception as e:
            logger.error(f"Failed to create UserProfile for user {instance.email}: {str(e)}")
            raise