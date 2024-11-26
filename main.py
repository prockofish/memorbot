import asyncio, random, json
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton

from database import DataBase
from keyboards import inline, reply
from states import UserForm, EducationForm

TOKEN = ""    # Укажите свой токен
LINE_IN_PAGE = 8

bot = Bot(TOKEN)
disp = Dispatcher()
storage = MemoryStorage()
users_db = DataBase("bot.db", "users")
dicts_db = DataBase("bot.db", "dicts")

def get_word(select_dict, param, old_words=[]):
    words = select_dict.split('&')
    if len(old_words) == len(words):
        old_words = []
    if param == 'random':
        word_id = random.choice(list(set(range(len(words))) - set(old_words)))
        return words[word_id].split('|'), old_words + [word_id]
    if param == 'memoriz':
        word_id = 10**10
        result = []
        for word in words:
            if int(word.split('|')[-2]) < word_id:
                word_id = int(word.split('|')[-2])
                result = word.split('|')
        return result, []
    if param == 'time':
        word_id = 10**10
        result = []
        for word in words:
            if int(word.split('|')[-1]) < word_id:
                word_id = int(word.split('|')[-1])
                result = word.split('|')
        return result, []
    if param =='mem-time':
        word_id = 10**10
        result = []
        for word in words:
            if (int(word.split('|')[-1])**2 + int(word.split('|')[-2])**2)**0.5 < word_id:
                word_id = (int(word.split('|')[-1])**2 + int(word.split('|')[-2])**2)**0.5
                result = word.split('|')
        return result, []

def update_select_dict(result, dict_selected, word):
    if len(word) == 3:
        old_word = '|'.join(word)
        new_word = '|'.join(word) + '|' +  f'{result[0]}|{result[1]}'
    else:
        old_word = '|'.join(word)
        new_word = '|'.join(word[:-2]) + '|' +  f'{int(word[-2]) + result[0]}|{int(word[-1]) + result[1]}' 
    dict_selected[2] = dict_selected[2].replace(old_word, new_word, 1)
    return dict_selected

def update_dicts(selected_dict, dicts, delete_flag=False):
    result = []
    for one_dict in dicts:
        if selected_dict != None:
            if not delete_flag:
                if selected_dict[0] == one_dict[0]:
                    result += [selected_dict]
                else:
                    result += [one_dict]
            else:
                if selected_dict != one_dict[0]:
                    result += [one_dict]
    return result

def compare_data(word1, word2):
    if word1.lower().replace(' ', '') == word2.lower().replace(' ', ''):
        return True
    return False

#
# text
#
@disp.message(lambda m: m.text == "/start")
async def command_start_handler(message) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(message.chat.id)
    if STEP_REG == 0:
        users_db.create(message.chat.id)
        await message.answer("Здравствуйте! Это бот для изучения слов.\n\n" \
                             "Чтобы начать пользоваться его функциями вы должны согласиться " \
                             "с тем, что результаты использования этого бота будут анонимно " \
                             "использоваться в моём исследовательском проекте.", reply_markup=inline.agree)
    elif STEP_REG < 4:
        await message.answer("Уже идёт процесс регистрации")
    else:
        await message.answer("Вы уже зарегистрированы", reply_markup=reply.main)

@disp.message(lambda m: m.text == "Выбрать словарь")
async def choosing_dict_handler(message) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(message.chat.id)
    if STEP_REG >= 4:
        dicts = dicts_db.get_all()
        inButtons = [[InButton(text=select_dict[1], callback_data=f"open-public-dict:{select_dict[0]}:0")] for select_dict in dicts[:8]]
        if len(inButtons) >= LINE_IN_PAGE and len(inButtons) != len(dicts):
            inButtons += [[InButton( text='--->', callback_data=f'view-public-page:{LINE_IN_PAGE}')]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await message.answer("Вот доступные словари:", reply_markup=keyboard)
    else:
        await message.answer("Вы не зарегистрированы")

@disp.message(lambda m: m.text == "Начать обучение")
async def person_dict_handler(message) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(message.chat.id)
    if STEP_REG >= 4:
        if STEP_REG == 5:
            dicts = json.loads(users_db.get(message.chat.id, 'dicts')[0])
            inButtons = [[InButton(text=select_dict[1], callback_data=f"open-dict:{select_dict[0]}:0")] for select_dict in dicts[:8]]
            if len(inButtons) >= LINE_IN_PAGE and len(inButtons) != len(dicts):
                inButtons += [[InButton( text='--->', callback_data=f'view-page:{LINE_IN_PAGE}')]]
            keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await message.answer("Вот ваши словари:" if STEP_REG == 5 and dicts != [] else "У вас нет словарей", reply_markup=keyboard if STEP_REG == 5 and dicts != [] else None)
    else:
        await message.answer("Вы не зарегистрированы")

@disp.message(lambda m: m.text == "Настройки")
async def settings_handler(message) -> None:
    await message.answer( "Выберите принцип обучения:\n\n" \
            "1) Случайность - при обучении будут предлогаться слова в случайном порядке\n\n" \
            "2) По забываемости - будут предлогаться слова с наихудшим качеством запоминания\n\n" \
            "3) По времени - будут предлогаться слова, которые были последние в обучении\n\n" \
            "4) По забываемости и времени - объединение 2 и 3 техники", reply_markup=inline.params )

@disp.message(lambda m: m.text == "Помощь")
async def help_handler(message) -> None:
    await message.answer("Реализация помощи")

@disp.message(lambda m: m.text == "Добавить словарь")
async def dict_add_handler(message) -> None:
    await message.answer("Скоро функция добавления своих словарей будет реализована.\n" \
                         "На данный момент, чтобы добавить новый словарь обратитесь к нам по кнопке ниже.", reply_markup=inline.help_button)

#
# Отслеживание callback-ов
#
@disp.callback_query(lambda c: c.data == 'agree')
async def callback_agree_handler(call, state) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG == 1:
        await call.message.delete()
        await call.message.answer("Сколько вам лет?")
        await state.set_state(UserForm.age)

@disp.callback_query(lambda c: c.data in ['M', 'W'])
async def callback_gender_handler(call) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG == 2:
        users_db.enter( call.message.chat.id, "gender", call.data )
        await call.message.edit_text( "Выберите принцип обучения (Позже его можно изменить в настройках):\n\n" \
            "1) Случайность - при обучении будут предлогаться слова в случайном порядке\n\n" \
            "2) По забываемости - будут предлогаться слова с наихудшим качеством запоминания\n\n" \
            "3) По времени - будут предлогаться слова, которые были последние в обучении\n\n" \
            "4) По забываемости и времени - объединение 2 и 3 техники", reply_markup=inline.params )

@disp.callback_query(lambda c: c.data in ['random', 'memoriz', 'time', 'mem-time'])
async def callback_param_handler(call) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG == 3:
        users_db.enter(call.message.chat.id, "param", call.data)
        await call.message.delete()
        await call.message.answer("Регистрация окончена!")
        await call.message.answer("Все функции находяться в меню над клавиатурой", reply_markup=reply.main)
    elif STEP_REG > 4:
        users_db.enter(call.message.chat.id, "param", call.data)
        await call.message.delete()
        await call.message.answer('Параметр обновлён')

@disp.callback_query(lambda c: 'view-public-page' in c.data)
async def callback_view_public_handler(call) -> None:  #view-public-page:page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        page = int(call.data.split(":")[1])
        dicts = dicts_db.get_all()
        inButtons = [[InButton(text=select_dict[1], callback_data=f'open-public-dict:{select_dict[0]}:{page}')] for select_dict in dicts[page:page + LINE_IN_PAGE]] + [[]]
        if page != 0:
            inButtons[-1] += [InButton(text='<---', callback_data=f'view-public-page:{page - LINE_IN_PAGE}')]
        if len(inButtons) >= LINE_IN_PAGE and len(inButtons) != len(dicts):
            inButtons[-1] += [InButton(text='--->', callback_data=f'view-public-page:{page + LINE_IN_PAGE}')]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text(f"Вот доступные словари:", reply_markup=keyboard)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'open-public-dict' in c.data)
async def callback_open_public_handler(call) -> None:  #open-public-dict:dict_id:back_page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        dict_id, back_page = map(int, call.data.split(":")[1:])
        dicts = dicts_db.get_all()
        for select_dict in dicts:
            if select_dict[0] == dict_id:  break
        inButtons = [[InButton(text='Добавить в личные словари', callback_data=f"add-dict:{select_dict[0]}:{back_page}")], \
                     [InButton(text="Назад", callback_data=f"view-public-page:{back_page}")]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text(f"Вы выбрали словарь: \"{select_dict[1]}\"", reply_markup=keyboard)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'add-dict' in c.data)
async def callback_add_dict_handler(call) -> None:  #add-dict:dict_id:page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        dict_id, page = map(int, call.data.split(':')[1:])
        dicts = dicts_db.get_all()
        for select_dict in dicts:
            if select_dict[0] == dict_id:  break
        users_dicts = users_db.get(call.message.chat.id, 'dicts')
        if None not in users_dicts:
            users_dicts = json.loads(users_dicts[0]) + [select_dict]
        else:
            users_dicts = [select_dict]
        users_db.enter(call.message.chat.id, 'dicts', json.dumps(users_dicts))
        inButtons = [[InButton( text="Назад", callback_data=f"view-public-page:{page}")]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text("Словарь добавлен!", reply_markup=keyboard)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'view-page' in c.data)
async def callback_view_handler(call) -> None:  #view-page:page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        if STEP_REG == 5:
            page = int(call.data.split(":")[1])
            dicts = json.loads(users_db.get(call.message.chat.id, 'dicts')[0])
            inButtons = [[InButton(text=select_dict[1], callback_data=f'open-dict:{select_dict[0]}:{page}')] for select_dict in dicts[page:page + LINE_IN_PAGE]] + [[]]
            if page != 0:
                inButtons[-1] += [InButton(text='<---', callback_data=f'view-page:{page - LINE_IN_PAGE}')]
            if len(inButtons) >= LINE_IN_PAGE and len(inButtons) + 1 != len(dicts):
                inButtons[-1] += [InButton(text='--->', callback_data=f'view-page:{page + LINE_IN_PAGE}')]
            keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text("Вот ваши словари:" if STEP_REG == 5 and dicts != [] else "У вас нет словарей", reply_markup=keyboard if STEP_REG == 5 and dicts != [] else None)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'open-dict' in c.data)
async def callback_open_handler(call) -> None:  #open-dict:dict_id:back_page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        dict_id, back_page = map(int, call.data.split(":")[1:])
        dicts = json.loads(users_db.get(call.message.chat.id, 'dicts')[0])
        for select_dict in dicts:
            if select_dict[0] == dict_id:  break
        inButtons = [[InButton(text='Начать обучение', callback_data=f"education:{select_dict[0]}:{back_page}")],
                     [InButton(text="Удалить", callback_data=f"delete:{dict_id}:{back_page}")], 
                     [InButton(text="Назад", callback_data=f"view-page:{back_page}")]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text(f"Вы выбрали словарь: \"{select_dict[1]}\"", reply_markup=keyboard)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'education' in c.data)
async def callback_education_handler(call, state) -> None:  #education:dict_id:back_page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        dict_id, back_page = map(int, call.data.split(':')[1:])
        dicts = json.loads(users_db.get(call.message.chat.id, 'dicts')[0])
        for select_dict in dicts:
            if select_dict[0] == dict_id:  break
        inButtons = [[InButton(text="Назад", callback_data=f"view-page:{back_page}")]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        param = users_db.get(call.message.chat.id, 'param')[0]
        words, old_words = get_word(select_dict[2], param)
        await state.set_state(EducationForm.step1)
        await state.update_data(words=words, select_dict=select_dict, old_words=old_words, back_page=back_page, param=param, keyboard=keyboard)
        await call.message.edit_text(f"Начнём обучение!\n{words[0]} - ?", reply_markup=keyboard)
    else:
        await call.message.answer("Вы не зарегистрированы")

@disp.callback_query(lambda c: 'ball' in c.data)
async def callback_education_handler(call, state) -> None:  #ball:num
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        ball = int(call.data.split(':')[1])
        data = await state.get_data()
        if len(data['old_words']) == len(data['select_dict'][2].split('&')):  
            old_words = []
        select_dict = update_select_dict([ball, 0], data['select_dict'], data['words'])
        dicts = update_dicts(select_dict, json.loads(users_db.get(call.message.chat.id, 'dicts')[0]))
        users_db.enter(call.message.chat.id, 'dicts', json.dumps(dicts))
        words, old_words = get_word(select_dict[2], data['param'], data['old_words'])
        await state.update_data(words=words, select_dict=select_dict, old_words=old_words)
        await call.message.edit_text(f"Продолжим обучение!\n{words[0]} - ?", reply_markup=data['keyboard'])

@disp.callback_query(lambda c: 'delete' in c.data)
async def callback_education_handler(call, state) -> None:  #delete:dict_id:page
    STEP_REG = users_db.get_count_not_empty_in_page(call.message.chat.id)
    if STEP_REG >= 4:
        dicts = json.loads(users_db.get(call.message.chat.id, 'dicts')[0])
        dict_id, page = map(int, call.data.split(':')[1:])
        dicts = update_dicts(dict_id, dicts, True)
        users_db.enter(call.message.chat.id, 'dicts', json.dumps(dicts))
        inButtons = [[InButton( text="Назад", callback_data=f"view-page:{page}")]]
        keyboard = InMarkup(inline_keyboard=inButtons, resize_keyboard=True)
        await call.message.edit_text("Словарь удалён", reply_markup=keyboard)

@disp.callback_query(lambda c: c.data == 'help')
async def callback_help_handler(call) -> None:
    await call.message.edit_text("Реализация помощи")
#
# Обработка state-ов
#
@disp.message(UserForm.age)
async def user_form_age(message, state) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(message.chat.id)
    if STEP_REG == 1:
        users_db.enter(message.chat.id, "age", message.text)
        await message.answer("Ваш пол:", reply_markup=inline.gender)
        await state.clear()

@disp.message(EducationForm.step1)
async def education_form_step1(message, state) -> None:
    STEP_REG = users_db.get_count_not_empty_in_page(message.chat.id)
    if STEP_REG >= 4:
        data = await state.get_data()
        if not compare_data(message.text, data['words'][1]):
            keyboard = InMarkup(inline_keyboard=[
                [InButton(text="1", callback_data=f"ball:-5"), InButton(text="2", callback_data=f"ball:-4"),
                InButton(text="3", callback_data=f"ball:-3"), InButton(text="4", callback_data=f"ball:-2"),
                InButton(text="5", callback_data=f"ball:-1")]], resize_keyboard=True)
            await message.answer(f"Не правильно, нужно { data['words'][1] }, { 'потому что ' + data['words'][2] if data['words'][2] != 'None' else '' }\nКак вы оцените, насколько хорошо помните это слово?\n0 - вы совсем не помните слово\n5 - вы отлично его помните, а ошиблись случайно", reply_markup=keyboard)
        else:
            keyboard = InMarkup(inline_keyboard=[
                [InButton(text="1", callback_data=f"ball:1"), InButton(text="2", callback_data=f"ball:2"),
                InButton(text="3", callback_data=f"ball:3"), InButton(text="4", callback_data=f"ball:4"),
                InButton(text="5", callback_data=f"ball:5")]], resize_keyboard=True)
            await message.answer(f"Вы правы!\nКак вы оцените, насколько хорошо помните это слово?\n0 - вы совсем не помните слово, выбрали наугад\n5 - вы отлично его помните", reply_markup=keyboard)
    else:
        await message.answer("Вы не зарегистрированы")

async def main() -> None:
    with open('dicts.txt', encoding='utf-8') as file:
        dicts = file.read().split('\n')
    for i in range(len(dicts)):
        dicts_db.create(i)
        dicts_db.enter(i, 'name', dicts[i].split('&')[0])
        dicts_db.enter(i, 'dict', '&'.join(dicts[i].split('&')[1:]))

    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, skip_updates=True)

    users_db.close()
    dicts_db.close()

if __name__ == "__main__":
    asyncio.run( main() )