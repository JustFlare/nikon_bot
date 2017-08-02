
contacts = '''
username @nikon_rus_bot

✅ Официальный сайт
www.nikon.ru
✅ Интернет-магазин Nikon
nikonstore.ru 
✅ Амбассадоры Nikon
nikonpro.ru 

Предложения и замечания по боту - just1flare@gmail.com
'''

start_message = '''
Привет! 
Это официальный бот от Nikon Russia. 
Работает в тестовом режиме.

{0}

Используте клавиатуру ниже, чтобы вызывать команды.
'''.format(contacts)

help_message = '''
Список команд:
/question - ответы на вопрос
/photo - поиск фотографий по различным категориям
/articles - статьи 
/guides - обучающие материалы
/contacts - контакты

Предложения и замечания по боту - just1flare@gmail.com
'''

PHOTO_PRINT_PATTERN = "Камера: {0}\nОбъектив: {1}\nДиафрагма: {2}\nВыдержка: {3}\nISO: {4}\nФокусное расстояние: {5}\nАвтор: {6}\n{7}"