from django.contrib.auth import get_user_model
from utils.exceptions import CustomException


def get_user(user_id):
    try:
        user = get_user_model().objects.get(pk=user_id)
    except get_user_model().DoesNotExist:
        raise CustomException(detail="User does not exist")
    return user
