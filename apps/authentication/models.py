from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g. PRODUCT_OWNER, SCRUM_MASTER, DEVELOPER
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('PO', 'Product Owner'),
        ('DEV', 'Developer'),
        ('SM', 'Scrum Master'),
    ]
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='DEV'
    )
    role_relation = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return self.email or self.username

    def __setattr__(self, name, value):
        if name == 'role':
            role_map = {
                'PO': 'PRODUCT_OWNER',
                'DEV': 'DEVELOPER',
                'SM': 'SCRUM_MASTER',
                'PRODUCT_OWNER': 'PRODUCT_OWNER',
                'DEVELOPER': 'DEVELOPER',
                'SCRUM_MASTER': 'SCRUM_MASTER',
            }
            target_role_name = role_map.get(value, 'DEVELOPER')
            self.__dict__['_role_changed_to'] = target_role_name
        super().__setattr__(name, value)

    def save(self, *args, **kwargs):
        # Resolve pending role changes if any
        pending_role = getattr(self, '_role_changed_to', None)
        if pending_role:
            role_obj, _ = Role.objects.get_or_create(name=pending_role)
            self.role_relation = role_obj
            self._role_changed_to = None
        elif not self.role_relation:
            # Fallback for initial user creation where role_relation is not set
            role_map = {
                'PO': 'PRODUCT_OWNER',
                'DEV': 'DEVELOPER',
                'SM': 'SCRUM_MASTER',
            }
            target_role_name = role_map.get(self.role, 'DEVELOPER')
            role_obj, _ = Role.objects.get_or_create(name=target_role_name)
            self.role_relation = role_obj

        # Sync CharField role string to match role_relation name
        reverse_map = {
            'PRODUCT_OWNER': 'PO',
            'DEVELOPER': 'DEV',
            'SCRUM_MASTER': 'SM',
        }
        if self.role_relation:
            mapped_str = reverse_map.get(self.role_relation.name, 'DEV')
            if self.role != mapped_str:
                self.role = mapped_str

        super().save(*args, **kwargs)

class AuditLog(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Sistema"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {username} - {self.action}: {self.description[:50]}"
