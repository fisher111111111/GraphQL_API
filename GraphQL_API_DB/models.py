# models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Настройка подключения к базе данных SQLite
# users.db будет создан в той же директории, где находится app.py
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)

# Базовый класс для всех декларативных моделей
Base = declarative_base()

# Определение модели User
class User(Base):
    __tablename__ = "users"  # Имя таблицы в БД

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)

    # Определение связи один-ко-многим с постами
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"&lt;User(id={self.id}, name='{self.name}', email='{self.email}')&gt;"


# Определение модели Post (для демонстрации связей)
class Post(Base):
    __tablename__ = "posts"  # Имя таблицы в БД

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    link = Column(String)

    # Внешний ключ для связи с таблицей users
    author_id = Column(Integer, ForeignKey("users.id"))

    # Определение связи многие-к-одному с пользователем
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"&lt;Post(id={self.id}, title='{self.title}', author_id={self.author_id})&gt;"

# Создание фабрики сессий
# SessionLocal будет использоваться для создания новых сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция для создания таблиц в базе данных
def create_tables():
    print("Создание таблиц базы данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы базы данных созданы.")


# Функция для добавления начальных данных (для тестирования)
def seed_data():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            print("Добавление начальных данных...")
            user1 = User(name="Alice", email="alice@example.com")
            user2 = User(name="Bob", email="bob@example.com")
            db.add_all([user1, user2])
            db.commit()

            # Обновим user1 и user2, чтобы получить их ID после коммита
            db.refresh(user1)
            db.refresh(user2)

            post1 = Post(title="First Post by Alice", published=True, author=user1)
            post2 = Post(title="Bob's Great Story", published=False, author=user2)
            db.add_all([post1, post2])
            db.commit()
            print("Начальные данные добавлены.")
        else:
            print("База данных уже содержит данные. Пропуск инициализации.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении начальных данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()
