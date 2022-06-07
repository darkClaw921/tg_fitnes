import traceback
import asyncio
import sqlite3
from loguru import logger
import time

daysSlov={'понедельник' : 'monday',
        'вторник' : 'tuesday',
        'среда' : 'wednesday',
        'четверг' : 'thursday',
        'пятница' : 'friday',
        'суббота' : 'saturday',
        'воскресенье':'sunday' }

class SqlLite:
    
    @logger.catch
    def __init__(self, nameDB: str, tableQuery: str):
        self.nameDB = nameDB
        self.conn = sqlite3.connect(nameDB)
        self.cur  = self.conn.cursor()
        
        try:
            self.cur.execute(tableQuery)
        except Exception as e :
            print('База данных уже создана [выполняеться подключение]', traceback.print_exc())
        self.conn.commit()

    @logger.catch
    def create_zanatia_table(self):
        days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            self.send(f"""create table {day}(
                id integer primary key,
                zanatiy text default '0',
                users_name text default '0',
                users_id text default '0',
                no_go text default '0',
                no_go_phone text default '0');""")
    
    @logger.catch
    def clear_all_zanatia_table(self):
        days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            self.send(f"""delete from {day} where 1""")    
    
    @logger.catch
    def create_raspisanie(string: str):
        string = string.split('\n')
        tableName = ''
        for line in string:
            line = line.lower()
            if line in daysRU:
                tableName = daysSlov[line]
            
    


    def send_values(self, query, values):
        """
            [query]: str - Запрос 
            [values]: list - Данные в томже порядке что и в запросе 
        """
        strVal = "values("    
        for _ in range(len(values)):
                strVal += "?,"
        strVal = strVal[0: -1]
        strVal += ')'
        #strDuplucate = f'ON CONFLICT(id_user) UPDATE set payload = {values[1]}, goloss = {values[2]}'
        self.cur.execute(query + strVal, values)
        self.conn.commit()
    
    @logger.catch
    def send_array(self, arr: list, nameTable:str, where:str, setName:str ):
        """
            записывает в базу list в формате "asdas\nasdf\n"

            [arr]: list - Список значений который нужно отправить
            [nameTable]: str - Имя таблицы 
            [where]: str - Условие встаки "id = 2"
            [setName]: str - В какой слобец вставить "user_id"
        """
        string = ''
        for value in arr:
            if value == ['']:
                continue
            string += f'{value};'
        string = string.replace(';;',';')
       #print(string)
        quer= f"""update {nameTable} set {setName}="{string}" where {where}""" 
        print(quer)
        self.cur.execute(quer)
        self.conn.commit()
    
#    @asyncio.coroutine
    #@logger.catch
    def send(self, query):
        self.cur.execute(query)
        self.conn.commit()
  #      print('start')
 #       time.sleep(60)
        #print('end')

    @logger.catch
    def update(self, query):
        self.cur.execute(query)
        self.conn.commit()

    @logger.catch
    def isHe(self, value, nameTable) -> bool:
        """Проверяет есть ли в базе строка с таким значение"""
        tempVal = self.get(f"select * from {nameTable} where id_user = {value}")
        if tempVal == []:
            return False
        else: 
            return True

    @logger.catch
    def get(self, query):
        
        a = self.conn.execute(query)
        return list(a)[0][0]
    
    @logger.catch
    def get_array(self, nameTable:str, nameColumn:str, where:str):
        query = f"select {nameColumn} from {nameTable} where {where}"
        a = self.conn.execute(query)
        #print('tyt',list(a))
        tempList = list(a)[0][0]
        #print('te',tempList)
        return tempList.replace(';;',';').split(';')


    @logger.catch
    def get_last_payload(self, user_id, nameTable):
        lastPayload = self.get(f"select payload from {nameTable} where user_id = {user_id}")
        try:
            a = list(lastPayload)[0][0]
        except:
            a = None
        return a

    def clear_column(self, nameTable):
        self.conn.execute(
        f"""
        DELETE FROM {nameTable} WHERE 1
        """)
   
