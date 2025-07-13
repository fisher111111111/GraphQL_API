# app.py
from flask import Flask
from strawberry.flask.views import GraphQLView
from schema import schema

app = Flask(__name__)

# Используем GraphQLView от Strawberry
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql_view', # Имя функции
        schema=schema,
        graphiql=True # Включаем GraphiQL для удобного тестирования
    )
)

if __name__ == '__main__':
    print("GraphQL API запущен на http://127.0.0.1:5000/graphql")
    print("Откройте этот адрес в браузере для использования GraphiQL.")
    app.run(debug=True)
