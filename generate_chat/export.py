from jinja2 import Environment, FileSystemLoader

# Указываем папку, где лежат шаблоны
env = Environment(loader=FileSystemLoader('../templates'))

# Загружаем шаблон
template = env.get_template('index.html')

# Передаем данные для подстановки
html_output = template.render(title="Главная страница", username="Иван")
print(html_output)