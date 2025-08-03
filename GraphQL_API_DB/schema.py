from __future__ import annotations

import strawberry
from typing import List, Optional
from models import User as UserModel, Post as PostModel


def to_dict(model_instance):
    return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

@strawberry.type
class UserSummary:
    id: strawberry.ID
    name: str
    email: Optional[str] = None

@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    published: bool
    link: Optional[str] = None
    author_id: strawberry.Private[int]

    @strawberry.field()
    def author(self, info) -> UserSummary:
        user = info.context['db'].query(UserModel).filter(UserModel.id == self.author_id).first()
        return UserSummary(**to_dict(user)) if user else None

@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: Optional[str] = None

    @strawberry.field()  # Добавлены скобки
    def posts(self, info) -> List[Post]:
        posts = info.context['db'].query(PostModel).filter(PostModel.author_id == int(self.id)).all()
        return [Post(**to_dict(post)) for post in posts]

@strawberry.type
class Query:
    @strawberry.field()  # Добавлены скобки
    def users(self, info) -> List[User]:
        db = info.context['db']
        users = db.query(UserModel).all()
        return [User(**to_dict(user)) for user in users]

    @strawberry.field()  # Добавлены скобки
    def user(self, info, id: strawberry.ID) -> Optional[User]:
        db = info.context['db']
        user = db.query(UserModel).filter(UserModel.id == int(id)).first()
        return User(**to_dict(user)) if user else None

@strawberry.type
class CreateUserResult:
    user: User

@strawberry.type
class UpdateUserResult:
    user: User

@strawberry.type
class DeleteUserResult:
    success: bool

@strawberry.type
class Mutation:
    @strawberry.mutation() # Добавлены скобки
    def create_user(self, info, name: str, email: Optional[str] = None) -> CreateUserResult:
        db = info.context['db']
        new_user_data = UserModel(name=name, email=email)
        db.add(new_user_data)
        db.commit()
        db.refresh(new_user_data)

        user_data = to_dict(new_user_data)  # конвертация в словарь
        return CreateUserResult(user=User(**user_data))

    @strawberry.mutation()  # Добавлены скобки
    def update_user(self, info, id: strawberry.ID, name: Optional[str] = None, email: Optional[str] = None) -> UpdateUserResult:
        db = info.context['db']
        user = db.query(UserModel).filter(UserModel.id == int(id)).first()
        if not user:
            raise Exception(f"Пользователь с ID {id} не найден.")
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        db.commit()
        db.refresh(user)
        return UpdateUserResult(user=User(**to_dict(user)))


    @strawberry.mutation()  # Добавлены скобки
    def delete_user(self, info, id: strawberry.ID) -> DeleteUserResult:
        db = info.context['db']
        user = db.query(UserModel).filter(UserModel.id == int(id)).first()
        if user:
            db.delete(user)
            db.commit()
            return DeleteUserResult(success=True)
        return DeleteUserResult(success=False)

schema = strawberry.Schema(query=Query, mutation=Mutation)
