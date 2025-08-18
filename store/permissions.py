from rest_framework import permissions
from rest_framework.permissions import  IsAdminUser,IsAuthenticated,AllowAny,BasePermission

class IsAdminOrReadonly(BasePermission):
    def has_permission(self, request, view):
    # if user is asking for safe methods such as option and get they can have it wether they're admin or whatever 
       if request.method in permissions.SAFE_METHODS:
        #as you can see it is true which means they have the permission
           return True 
    # but if they are asking for methods other than the safe ones they should be admin users    
       return bool(request.user and request.user.is_staff)
    
class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')