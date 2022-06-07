from config import TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bitrix24 import Bitrix24
from pprint import pprint
import tg_keyboard as kb
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.builtin import Text

from tg_keyboardTest import *
from localDataBase import SqlLite
webhook = 'hok'
bit = Bitrix24(webhook)
#get UF_CRM_1651395108854  прошло занятий
#get UF_CRM_1650628121798  вид абонимента 
#list 'STAGE_ID': 'C2:PREPAYMENT_INVOICE',  занимается
#list 'STAGE_ID': 'C2:EXECUTING', до конца абонимента 5 дней

VID_ABONIMENTA = {'50': '16 занятий (45 дней)',
                  '46': '8 занятий (31 день)',
                  '48': '12 занятий (45 день)',
                  '44': '4 занятий (31 день)',
                  '52': 'Безлимит (30 дней)',
                  }
SQL = SqlLite("Users.db","""
        create table users(
        id integer primary key,
        user_id int unique,
        title text,
        payload text,
        status text default 'user',
        phone text);
        """)

bot = Bot(token=TOKEN) 
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

vote_cb = CallbackData('vote', 'action', 'amount')

def get_aboniment(phone:str):
    """
    Возвращает 2 значения [количество занятий], [вид абонимента] 
    """
    ID = bit.callMethod('crm.contact.list', FILTER= {'PHONE':int(phone)}, select=['ID'])
    deal_id = bit.callMethod('crm.deal.list', FILTER= {'CONTACT_ID':ID[0]['ID']}, select=['ID'])
    aboniment = bit.callMethod('crm.deal.get', ID= deal_id[0]['ID'])
    count_zanatie = aboniment['UF_CRM_1651395108854']
    vid_aboniment = aboniment['UF_CRM_1650628121798']
    return count_zanatie, vid_aboniment

def create_zanatia_db():
    SQL.create_zanatia_table()
    #SQL.send("""create table settings(
    #    id integer primary key,
    #    raspisanie text,""")       


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler(commands=['adminasd'])
async def process_admin_command(message: types.Message):
    try:
        SQL.send(f"""insert into users (status, user_id) values("admin", "{message.from_user.id}") """)
    except:
        SQL.send(f"""update users set status="admin" where user_id="{message.from_user.id}" """)
    await message.reply("Вы добавлены в список администраторов")


@dp.message_handler(state='aboniment') 
async def aboniment_state(msg: types.Message):
    message = msg.text
    user_id = msg.from_user.id
    try:
        phone = SQL.get(f'select phone from users where user_id={user_id}')[0][0]
        if phone == None:
            count_zanatie, vid_aboniment = get_aboniment(message)
            SQL.send(f"update users set payload = 'MAIN', phone={message} where user_id = {user_id}")
            #lis = [1,2,3]
            #SQL.send_array(lis,'users',f'user_id ={user_id}','title')      
        else:
            count_zanatie, vid_aboniment = get_aboniment(phone)
            #a = SQL.get_array('users','title',f'user_id={user_id}')
            #pprint(a)
    except Exception as e :
        print(e)
        await bot.send_message(msg.from_user.id, f'Такой телефон не привязан к абонименту, проверьте правильность телефона')
        return 0

    count_aboniment = VID_ABONIMENTA[vid_aboniment].split(' ')[0]
    await bot.send_message(msg.from_user.id, f'Ваш вид абонимента: {VID_ABONIMENTA[vid_aboniment]}\nКоличество прошедших занятий: {count_zanatie}/{count_aboniment}')   
    state = dp.current_state(user=msg.from_user.id)
    await state.finish()

#@dp.callback_query_handler('btn_aboniment')
#async def process_callback_button1(callback_query: types.CallbackQuery):
#    await bot.answer_callback_query(callback_query.id)
#    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')

@dp.callback_query_handler(Text(startswith="btnm_"))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    code = callback_query.data.split('_')
    print(code)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Доступные тренировки 🗒', reply_markup=eval(f'keyboard_{code[1]}'))

@dp.callback_query_handler(Text(startswith='btn_'))
async def process_callback_zapis(callback_query: types.CallbackQuery):
    zanatie = callback_query.data
    user_id = callback_query.from_user.id
    furstName= callback_query.from_user.first_name
    lastName= callback_query.from_user.last_name

    codeSplit = callback_query.data.split('_')
    statusUser = SQL.get(f"""select status from users where user_id="{user_id}" """)
    if statusUser == 'admin':

    users = SQL.get_array(nameTable=codeSplit[1], nameColumn='users_id', where=f"""zanatiy="{zanatie}" """)
    if users == ['0']:
        users=[]
    users.append(user_id)
    SQL.send_array(users, nameTable=codeSplit[1], where= f"""zanatiy="{zanatie}" """, setName = 'users_id')
    
    await bot.answer_callback_query(
            callback_query.id,
            text='Вы записаный на это занятие 😉', show_alert=True)
    

@dp.message_handler()
async def echo_message(msg: types.Message):
    message = msg.text.lower()
    user_id = msg.from_user.id
    state = dp.current_state(user=msg.from_user.id)
    lastPayload = SQL.get_last_payload(user_id , 'users')
    if message == 'абонимент':
        try:
            phone = SQL.get(f'select phone from users where user_id={user_id}')[0][0]
        except:
            phone = None

        if phone == None:
            await bot.send_message(msg.from_user.id, 'Пожалуйста введите ваш номер телефона \nНапример: 89190072351', reply_markup=kb.markup_aboniment)
            SQL.send_values(f"insert into users (payload, user_id)", ['REG', user_id])
            await state.set_state('aboniment')
            return 0
        elif phone != None:
            await aboniment_state(msg)
            return 0  
    if message == 'записаться на занятие':
        await bot.send_message(user_id, 'На какой день хотите записаться?',reply_markup=keyboard_main)
        return 0    
    await bot.send_message(msg.from_user.id, 'Какайто не известный вопрос напишите нам в вк', reply_markup=keyboard_tuesday)
   

def main():
    #PHONE = '89004777472'
    #count_zanatie, vid_aboniment = get_aboniment(PHONE)
    #a = bit.callMethod('crm.deal.fields')# select=['ID','TITILE'])
    #print(count_zanatie, vid_aboniment)
    create_zanatia_db()   


if __name__ == '__main__':
    main()
    executor.start_polling(dp)
