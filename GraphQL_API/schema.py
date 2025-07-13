# schema.py
import strawberry
from typing import List, Optional

# Имитация базы данных в памяти
USERS_DATA = {}
next_user_id = 1
POSTS_DATA = {}
next_post_id = 1

@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: Optional[str] = None

    @strawberry.field
    def posts(self) -> List["Post"]:
        # В реальном приложении здесь был бы запрос к БД
        return [Post(**post) for post in POSTS_DATA.values() if post['author_id'] == int(self.id)]

@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    published: bool
    link: Optional[str] = None
    author: User # Strawberry автоматически разрешит связанный объект

    # Дополнительное поле для хранения author_id, которое не отображается в GraphQL-схеме
    # но используется для внутренних связей
    author_id: strawberry.Private[int]

    @strawberry.field
    def author(self) -> User:
        # В реальном приложении здесь был бы запрос к БД
        author_data = USERS_DATA.get(self.author_id)
        return User(**author_data) if author_data else None

# --- QUERY (Запросы на чтение) ---
@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[User]:
        """Возвращает список всех пользователей."""
        return [User(**user) for user in USERS_DATA.values()]

    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[User]:
        """Возвращает пользователя по ID."""
        user_data = USERS_DATA.get(int(id))
        return User(**user_data) if user_data else None

# --- MUTATIONS (Запросы на изменение) ---

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
    @strawberry.mutation
    def create_user(self, name: str, email: Optional[str] = None) -> CreateUserResult:
        global next_user_id
        user_id = next_user_id
        next_user_id += 1

        new_user_data = {
            'id': user_id,
            'name': name,
            'email': email
        }
        USERS_DATA[user_id] = new_user_data
        return CreateUserResult(user=User(**new_user_data))

    @strawberry.mutation
    def update_user(self, id: strawberry.ID, name: Optional[str] = None, email: Optional[str] = None) -> UpdateUserResult:
        user_id = int(id)
        user_data = USERS_DATA.get(user_id)
        if not user_data:
            raise Exception(f"Пользователь с ID {id} не найден.")

        if name is not None:
            user_data['name'] = name
        if email is not None:
            user_data['email'] = email

        # Обновлять словарь не обязательно, так как мы изменили user_data по ссылке,
        # но для ясности оставим:
        USERS_DATA[user_id] = user_data
        return UpdateUserResult(user=User(**user_data))

    @strawberry.mutation
    def delete_user(self, id: strawberry.ID) -> DeleteUserResult:
        user_id = int(id)
        if user_id in USERS_DATA:
            del USERS_DATA[user_id]
            # Также удаляем посты этого пользователя для целостности
            posts_to_delete = [pid for pid, post in POSTS_DATA.items() if post['author_id'] == user_id]
            for pid in posts_to_delete:
                del POSTS_DATA[pid]
            return DeleteUserResult(success=True)
        return DeleteUserResult(success=False)

# Создаем финальную схему GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation)

# --- Добавление начальных данных для тестирования ---
def init_data():
    global next_user_id, next_post_id

    # User 1
    user1_id = next_user_id
    next_user_id += 1
    USERS_DATA[user1_id] = {'id': user1_id, 'name': 'Alice', 'email': 'alice@example.com'}

    # User 2
    user2_id = next_user_id
    next_user_id += 1
    USERS_DATA[user2_id] = {'id': user2_id, 'name': 'Bob', 'email': 'bob@example.com'}

    # Post 1 (by Alice)
    post1_id = next_post_id
    next_post_id += 1
    POSTS_DATA[post1_id] = {
        'id': post1_id, 'title': 'My First Post', 'published': True,
        'link': 'http://example.com/post1', 'author_id': user1_id
    }

    # Post 2 (by Bob)
    post2_id = next_post_id
    next_post_id += 1
    POSTS_DATA[post2_id] = {
        'id': post2_id, 'title': 'Bob\'s Amazing Story', 'published': False,
        'link': 'http://example.com/post2', 'author_id': user2_id
    }

init_data()
