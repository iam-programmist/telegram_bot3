import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from random import shuffle
from context import *
from secret import *
bot = telebot.TeleBot(api_key, parse_mode=None)

def get_random_question():
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("select country, capital from quiz order by random() limit 1")
    question = cur.fetchone()
    close_connection(conn, cur)
    return question

def get_random_capitals(exclude_capital):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("select capital from quiz where capital != %s order by random() limit 3", (exclude_capital,))
    capitals = [row[0] for row in cur.fetchall()]
    close_connection(conn, cur)
    return capitals

create_tables()
insert_data()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to QuizBot! Use the /quiz command to start the quiz.")

@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    chat_id = message.chat.id
    question_data = get_random_question()
    if question_data:
        country, correct_capital = question_data        
        wrong_capitals = get_random_capitals(correct_capital)        
        answers = [correct_capital] + wrong_capitals
        shuffle(answers)        
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for answer in answers:
            markup.add(KeyboardButton(answer))
        bot.send_message(chat_id, f"What is the capital of {country}❓", reply_markup=markup)        
        bot.register_next_step_handler(message, check_answer, correct_capital)
    else:
        bot.send_message(chat_id, "No questions available. Try again later.")

def check_answer(message, correct_capital):
    chat_id = message.chat.id
    user_answer = message.text
    if user_answer == correct_capital:
        bot.send_message(chat_id, "Correct! ✅")
    else:
        bot.send_message(chat_id, f"Incorrect! ❎ The correct answer was: {correct_capital}.")    
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("Another question"))
    bot.send_message(chat_id, "Would you like to try again❓", reply_markup=markup)    
    bot.register_next_step_handler(message, start_quiz)

bot.infinity_polling()
