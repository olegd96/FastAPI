
from app.dao.base import BaseDAO
from app.users.models import RefreshSessionModel, Users

class UsersDAO(BaseDAO):
   models = Users

class RefreshSessionDAO(BaseDAO):
   models = RefreshSessionModel


               
