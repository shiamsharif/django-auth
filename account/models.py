from django.db import models
from django.utils import timezone

        
#Email OTP Verification
class EmailOTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=60)

    def __str__(self):
        return f"{self.email} - {self.code}"
 