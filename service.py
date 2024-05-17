from time import sleep
from jnius import autoclass
from kvdroid.jclass.android import Color
from kvdroid.tools import get_resource
from kvdroid.tools.notification import create_notification
import requests
from oscpy.server import OSCThreadServer
from datetime import datetime
from datetime import timedelta
import ast

def handle_message(*values):
    dec = values[0].decode('utf-8')
    global listlembrete
    msg = ast.literal_eval(dec)
    listlembrete = msg
    
    
    
def discover_day(*args):
    #roda 1x por dia
    dia= datetime.now().weekday() #retorna o dia da semana 0 é segunda 6 é domingo
    if dia == 0:
        hoje = "SEG"
    elif dia == 1:
        hoje = 'TER'
    elif dia == 2:
        hoje = 'QUA'
    elif dia == 3:
        hoje = 'QUI'
    elif dia == 4:
        hoje = 'SEX'
    elif dia == 5:
        hoje = 'SAB'
    elif dia == 6:
        hoje = 'DOM'    
    #print("hoje: ", hoje)
        
def update_clock(*args):
    nomelem = []
    horariolem = []
    frequencialem = []
    ativarlem = 0
    global listlembrete
    global now
    now = datetime.now()
    global contL
    #print("list:", listlembrete)
        
    for i in range(0, len(listlembrete), 3): #pega o nome
        nomelem.append(listlembrete[i]) 
    for i in range(1, len(listlembrete), 3): #pega o horario
        horariolem.append(listlembrete[i])
    for i in range(2, len(listlembrete), 3): #pega a frequencia
        frequencialem.append(listlembrete[i]) 

    #print("nome: " + str(nomelem) + " horario: "+ str(horariolem) + " freq: " + str(frequencialem))

    for i in range(0, len(frequencialem), 1):
        if hoje in frequencialem[i]: 
            ativarlem = 1

    for i in range(0, len(horariolem), 1):
        if horariolem[i] == now.strftime('%H:%M') and ativarlem == 1: 
            if now.strftime('%S') > '00' and  now.strftime('%S') < '15':
                ativarlem = 0
                contL = contL + 1
                #mandar pro servidor
                URL_lemb = "https://api.thingspeak.com/update?api_key=7W0X2I3EH36FNNPB&field1=" + str(contL)  
                requestLem = requests.get(URL_lemb) 
                create_notification(
                    	small_icon=get_resource("mipmap").icon,
                    	channel_id="3",
                    	title="ALERTA!",
                    	text="Você tem um lembrete: " + nomelem[i],
                    	ids=contL,
                    	channel_name=f"ch1",
                    	large_icon="icon.png",
                    	small_icon_color=Color().parseColor("#BFDDF3"),
                    	big_picture="icon.png"
                 )
                    
                    


now = datetime.now()
PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)
Q_global = []
S_global = []
anteriorS = 0
anteriorQ = 0
requestQ = ""
requestS = ""
hoje = ''
listlembrete = []
contL = 2


server = OSCThreadServer()
server.listen(address='localhost', port=5005, default=True)
server.bind(b'/path', handle_message)


while True:
    print("service running...")
    URL_queda = "https://api.thingspeak.com/channels/2423871/feeds.json?api_key=9CWWQKBE29OI6L5N&results=1" 
    URL_sos = "https://api.thingspeak.com/channels/2422645/feeds.json?api_key=IQDQ48W2WNWS1TE5&results=1"
        
    update_clock()
    discover_day()
    requestQ = requests.get(URL_queda)
    requestS= requests.get(URL_sos)
    #print(requestQ.text)
    Q_global.append(requestQ.text)
    string=' '.join([str(item) for item in Q_global])
    Q_global.clear()
    if "[" in string:
        nova_string = string.split("}") 
        #print("nova string: ", nova_string[1])
        if "field" in nova_string[1]:
            last_string = nova_string[1].split("field") 
            #print("last string: ", last_string[1]) 
            if '"' in last_string[1]:
                result_string = last_string[1].split(":") 
                #print("result string: ", result_string[1])
                specific_char_trimmed1 = result_string[1].rstrip('"')
                specific_char_trimmed2 = specific_char_trimmed1.lstrip(" ")
                specific_char_trimmed3 = specific_char_trimmed2.lstrip('"')
                #specific_char_trimmed4 = specific_char_trimmed3.lstrip(" ")
                print("Result:", specific_char_trimmed3)
                
                atualQ = int(specific_char_trimmed3)
                  
                if(atualQ != anteriorQ):
                    print("entrou no ifQ")
                    anteriorQ = atualQ
                    create_notification(
                                small_icon=get_resource("mipmap").icon,
                        	channel_id="1",
                        	title="ALERTA!",
                        	text="Uma queda foi detectada!",
                        	ids=1,
                        	channel_name=f"ch1",
                        	large_icon="icon.png",
                        	small_icon_color=Color().parseColor("#BFDDF3"),
                        	big_picture="icon.png"
                     )
                     
                 
                    
    #print(requestS.text)
    S_global.append(requestS.text)
    stringS=' '.join([str(item) for item in S_global])
    #print('stringS: ', stringS)
    S_global.clear()
    if "[" in stringS:
        nova_stringS = stringS.split("}") 
        #print("nova string: ", nova_stringS[1])
        if "field" in nova_stringS[1]:
            last_stringS = nova_stringS[1].split("field") 
            #print("last string: ", last_stringS[1]) 
            if '"' in last_stringS[1]:
                result_stringS = last_stringS[1].split(":") 
                #print("result string: ", result_stringS[1])
                specific_char_trimmed1S = result_stringS[1].rstrip('"')
                specific_char_trimmed2S = specific_char_trimmed1S.lstrip(" ")
                specific_char_trimmed3S = specific_char_trimmed2S.lstrip('"')
                #specific_char_trimmed4S = specific_char_trimmed3S.lstrip(" ")
                print("Result:", specific_char_trimmed3S)
                
                atualS = int(specific_char_trimmed3S)
                
                if(atualS != anteriorS):
                    print("entrou no ifS")
                    anteriorS = atualS 
                    create_notification(
                        	small_icon=get_resource("mipmap").icon,
                        	channel_id="2",
                        	title="ALERTA!",
                        	text="O botão SOS foi acionado!",
                        	ids=2,
                        	channel_name=f"ch1",
                        	large_icon="icon.png",
                        	small_icon_color=Color().parseColor("#BFDDF3"),
                        	big_picture="icon.png"
                    )
                            
        
    sleep(10)
    

