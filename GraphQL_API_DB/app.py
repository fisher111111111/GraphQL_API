# app.py
from flask import Flask, request, g
from strawberry.flask.views import GraphQLView
from schema import schema
from models import SessionLocal, create_tables, seed_data  # Импортируем из models.py

app = Flask(__name__)

# Функция для получения сессии базы данных
def get_db_session():
    # Если сессия уже существует для текущего контекста запроса, используем её
    if not hasattr(g, 'db_session'):
        g.db_session = SessionLocal()  # Иначе создаем новую сессию
    return g.db_session

# Функция для закрытия сессии базы данных после каждого запроса
@app.teardown_appcontext
def teardown_db_session(exception=None):
    db = g.pop('db_session', None)
    if db is not None:
        db.close()

class CustomGraphQLView(GraphQLView):
    def get_context(self, request, response) -> dict:
        return {"db": get_db_session(), "request": request}


app.add_url_rule(
    '/graphql',
    view_func=CustomGraphQLView.as_view(
        'graphql_view',
        schema=schema,
        graphiql=True,  # Включаем GraphiQL для удобного тестирования
        )
)

if __name__ == '__main__':
    # При запуске приложения убедимся, что таблицы созданы
    create_tables()
    # И добавим начальные данные, если их нет
    seed_data()

    print("GraphQL API запущен на http://127.0.0.1:5000/graphql")
    print("Откройте этот адрес в браузере для использования GraphiQL.")
    app.run(debug=True)