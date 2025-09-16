from django.db.models.signals import post_migrate
from django.dispatch import receiver
from account.models import Role, UserGroup, User
from django.contrib.auth.hashers import make_password

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    # Check if the Admin Role exists
    admin_role, created = Role.objects.get_or_create(
        name='Admin',
        code='ADMIN',
        defaults={
            'privileges': ['is_admin'],
        }
    )
    
    # Check if the UserGroup exists
    admin_group, group_created = UserGroup.objects.get_or_create(
        name='Admin Group',
        code='ADMIN_GROUP',
    )
    
    # Check if an Admin user exists, if not, create one
    if not User.objects.filter(email='admin@udsm.ac.tz').exists():
        admin_user = User.objects.create(
            email='admin@udsm.ac.tz',
            first_name='Admin',
            last_name='User',
            gender=User.MALE,
            is_active=True,
            is_staff=True,
            is_admin=True,
            is_verified=True,
            role=admin_role,
            group=admin_group,
            password=make_password('123@qwe@')  # Default admin password
        )
        print("Default Admin user created and assigned the Admin role and Admin Group.")
    else:
        print("Admin user already exists.")
