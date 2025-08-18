from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

# but this is not enough you have have to add the serializer to the setting part as well,
#  check out the setting:
# DJOSER = {
#     'SERIALIZERS': {
#         'user_create': 'store_custom.serializer.UserCreateSerializer',
#         'current_user': 'store_custom.serializer.UserSerializer',
#     }
#   }
class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields=['id','username','password','email','first_name','last_name']


class UserSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields=['id','username','email','first_name','last_name']
