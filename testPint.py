from loguru import logger
from textblob import TextBlob 
from googletrans import Translator
import googletrans
from raspisanie import raspisanie
from google_trans_new import google_translator  
from localDataBase import SqlLite

"""
pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
print(pytesseract.image_to_string(Image.open('test.png')))
#image = cv2.imread("test.png")
image = Image.open("test.png")
string = pytesseract.image_to_string(image)
print(string)

1/0
"""
sql = SqlLite('Users.db','')

@logger.catch
def string_to_format(line:str):
    tempLine =''
    enLine=''

    line = line.replace('\n','')
    lineSplit = line.split(' ') #replace('\n', None)
    time = lineSplit[0]
    #if lineSplit == '\n':
    #    lineSplit.pop(-1)

    name = lineSplit[-1]
    lineSplit.pop(0)
    lineSplit.pop(-1)
    zanatie = ' '.join(lineSplit)
     
    translator = Translator()
    translation = translator.translate(line, dest='en')
    
    enLine = translation.text
    testLine = enLine.replace(':','_').replace(' ', '_')
    #print(testLine) 

    #line = line.replace(':','_').replace(' ', '_')
    #print(googletrans.LANGUAGES)
    #result = translator.translate('привет', src='ru')
    #print(time, name, zanatie)
    return str(testLine), str(line)
# Понедельник 12 мая
# 12:00 Люба спина и ноги
def main():    
    with open('pin.txt', 'r') as f:
        with open ('raspisanie.py', 'w') as f1:
            f1.write('raspisanie={ \n')
            sufix=''   
            
            for line in f:
        
                if line =='\n':
                    continue
                l = line.split(' ')

                a = string_to_format(str(line))[0].lower() # aEN
                aRU = string_to_format(str(line))[1]
                print(aRU)
                try:
                    #print(int(l[0].split(':')[0])/2)
                    int(l[0].split(':')[0])/2
                except:
                    sufix = 'btn_'+a.split('_')[0]
                    sufix = sufix.lower()
                    f1.write(f"    'btnm_{a}': '{aRU}', \n")
                    continue

                f1.write(f"    '{sufix}_{a}': '{aRU}', \n")
                #print(f"'{sufix}_{a}:' '{aRU}'")
            f1.write('}')

    create_keyboard_file()
        

def create_keyboard_file():
    days = ['понедельник','вторник','среда','четверг','пятница','суббота','воскресенье']
    with open('tg_keyboardTest.py', 'w') as f:
        string =''
        f.write('from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton \n')
        f.write('keyboard_main = InlineKeyboardMarkup()')
        for call, name in raspisanie.items():
            name=name.lower()  
            call=call.lower()
            tempName = name.split(' ')
            tempCall = call.split('_')
            if tempName[0] in days:
                f.write(f"\nkeyboard_main.add(InlineKeyboardButton(text='{name}',callback_data='{call}'))\n")
                f.write(string) 
                string = f"""\nkeyboard_{tempCall[1]} = InlineKeyboardMarkup()"""   
            else:
                string += f".add(InlineKeyboardButton(text='{name}',callback_data='{call}'))"
        f.write(string) 
    insert_db()

def insert_db():
    sql.clear_all_zanatia_table()
    for call, name in raspisanie.items():
        callSplit = call.split('_')
        sql.send(f"insert into {callSplit[1]} (zanatiy) values ('{call}')")         
        print(call)
        


if __name__ == "__main__":
    main()
    #create_keyboard_file()



