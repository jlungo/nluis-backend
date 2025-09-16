from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self,gender, email, first_name, last_name, user_type):
        if not email:
            raise ValueError('user Must have an email')
        if not first_name:
            raise ValueError('User must have first name')
        if not last_name:
            raise ValueError('User Must have last name')
        if not user_type:
            raise ValueError('User Must have a user type')
       
       

        user = self.model(
            email=self.normalize_email(email=email),
            first_name=first_name,
            last_name=last_name,
            gender = gender,
            user_type=user_type,
        )
        
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password, gender, user_type):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            password=password,
            gender=gender
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
