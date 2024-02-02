import telebot
import requests
from LxmlSoup import LxmlSoup
from keyboa.keyboard import Keyboa

bot = telebot.TeleBot('6718842522:AAG-6v47XZwZp99jgtSsUIPCxo8UHOw2xoM')

@bot.message_handler(content_types=['text'])
def start(message):

    global user_id
    if message.text == '/start':
        user_id = message.from_user.id
        keyboard = Keyboa(items=[{'Хочу': 'yes'}, {'Не хочу': 'no'}])
        bot.send_message(user_id, reply_markup=keyboard(), text="Привет, я бот в котором вы можете посмотреть актуальные \n"
                                                                "цены на некоторые акции. Вся информация взята с сайта: \n"
                                                                "<<www.banki.ru>>. Если ты хочешь посмотреть акции, нажми <<Хочу>>.")

    else:
        bot.send_message(user_id, "Извини, я тебя не понял. Попробуй написать /start")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    if call.data == "yes":
        bot.send_message(user_id, 'Окей, давай начнём')
        URL = "https://www.banki.ru/investment/shares/"
        parse(URL)
        bot.send_message(user_id, text="Выбирай и жми!", reply_markup=keyboard(names))
    elif call.data == "no":
        bot.send_photo(user_id, open(r'C:\Users\User\PycharmProjects\Banana_bot\sad banana.jpg', 'rb'))
        bot.send_message(user_id, 'Извини, в таком случае я ничем не могу тебе помочь')

    for i in range(len(names)):
        if call.data == str(i):
            bot.send_message(user_id, text=prices[i])

    if call.data == 'next':
        URL = 'https://www.banki.ru/investment/shares/?page=2'
        parse(URL)
        bot.send_message(user_id, text="Выбирай и жми!", reply_markup=keyboard(names))
    elif call.data == 'back':
        URL = "https://www.banki.ru/investment/shares/"
        parse(URL)
        bot.send_message(user_id, text="Выбирай и жми!", reply_markup=keyboard(names))

def parse(URL):
    html = requests.get(URL).text #передаём в переменную "html" HTML код страницы при помощи GET запроса к сайту
    soup = LxmlSoup(html) #создаём экземпляр объекта LxmlSoup в который передаём переменную html. Это нужно,
    #так как LxmlSoup является классом хранящим в себе нужные нам методы для извлечения информации из html кода.
    links = soup.find_all('a', class_='link-simple') #передаём в переменную все ссылки с подходящим нам тегом и классом

    #создаём два глобальных списка, которые будут содержать названия и цены акций
    global names
    global prices
    prices = []
    names = []

    price = soup.find_all('div', class_='FlexboxGrid__sc-akw86o-0 gIaOTc') #передаём в переменную все ссылки с
    # подходящим тегом и классом

    #формируем список цен
    #так на сайте кроме цены на акцию есть её изменение, пойдём с шагом 2
    for i in range(0, len(price), 2):
        prices.append(price[i].text()[:13] + ' ' + price[i].text()[13:]) #срезами добавим пробел между текстом и ценой

    #формируем список названий
    for link in links:

        #проверяем что link это точно ссылка на товар(она должна начинаться с "/")
        if link.get('href')[0] != '/':
            break
        else:
            names.append(link.text())

def keyboard(names):
    names_for_keyboard = [] #создаём список в который будем добавлять словари(кнопки)

    #заполняем список именами акций и их номерами(str(i))
    for i in range(len(names)):
        names_for_keyboard.append({names[i]: str(i)})

    names_for_keyboard.append([{'Назад': 'back'}, {'Ещё': 'next'}]) #добавим кнопки для перелистывания списка акций
    keyboard1 = Keyboa(items=names_for_keyboard) #создаём клавиатуру
    return keyboard1() #эта функция будет возвращать нам готовую клавиатуру с названиями акций

bot.polling(none_stop=True, interval=0)