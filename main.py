import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from multiprocessing import Process
from kivy.clock import Clock
from kivy.uix.widget import Widget 
from kivy.uix.textinput import TextInput 
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarker
from kivy.resources import resource_find
from datetime import datetime
from datetime import timedelta
from jnius import autoclass

from kvdroid.jclass.android import Color
from kvdroid.tools import get_resource
from kvdroid.tools.notification import create_notification

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

import pickle



Q_global = []
S_global = []
L_global = []
show_string = []
contL = 0
freq = ""
controlspinner = 0
listlembrete = []
lembrete_time = ''
lembrete_freq = ''
hoje = ''
all_lembretes=[]
aux_lembretes=[]

    	
class MyWidget(BoxLayout):
    anteriorS = 0
    atualS = 0
    anteriorQ = 0
    atualQ = 0
    flagLocs = 1

    anteriorL = MapMarker(lat= float(0), lon= float(0))
    def __init__(self,**kwargs):
        super(MyWidget, self).__init__(**kwargs)

        self.now = datetime.now()
        
       
        self.start_service()
       
        Clock.schedule_once(self.loop, 1)
        Clock.schedule_interval(self.loop, 10)
        Clock.schedule_interval(self.updateQUEDA, 180) #retem valor por 3min
        Clock.schedule_interval(self.updateSOS, 180)
        
    
      
    def save_data(self):
        pickle_data = listlembrete
        file_name = "mypickle.pickle"
        pickle_out = open(file_name, "wb")
        pickle.dump(pickle_data, pickle_out)
        pickle_out.close()
            
       
        
        
        
    def start_service(self):
        SERVICE_NAME=u'{packagename}.Service{servicename}'.format(packagename=u'org.test.myapp', servicename=u'Myapp')
        service = autoclass(SERVICE_NAME)
        mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
        service.start(mActivity, '')
        return service
        

    def loop(self, dt):
        URL_queda = "https://api.thingspeak.com/channels/2423871/feeds.json?api_key=9CWWQKBE29OI6L5N&results=1" 
        URL_sos = "https://api.thingspeak.com/channels/2422645/feeds.json?api_key=IQDQ48W2WNWS1TE5&results=1"
        URL_loc = "https://api.thingspeak.com/channels/2422646/feeds.json?api_key=AL8HYPIZRWCSY8AT&results=1"

        self.requestQ = UrlRequest(URL_queda, self.resQ)
        self.requestS = UrlRequest(URL_sos, self.resS)
        self.requestL = UrlRequest(URL_loc, self.resL)
       
    def send_variable(self):
        global listlembrete
        print("send variable")
        client = OSCClient('localhost', 5005)
        teste = str(listlembrete)
        messageE = teste.encode('utf-8')
        client.send_message(b'/path', [messageE])
    
    def resQ(self, *args):
        #print ("ResultQ: ", self.requestQ.result)
        Q_global.append(self.requestQ.result)
        string=' '.join([str(item) for item in Q_global])
        #print('stringQ: ', string)
        Q_global.clear()
        if "[" in string:
            nova_string = string.split("}") 
            #print("nova string: ", nova_string[1])
            if "field" in nova_string[1]:
                last_string = nova_string[1].split("field") 
                #print("last string: ", last_string[1]) #1,2,3 ou 4 corresponde a field1 field2... = 1 : None
                if "'" in last_string[1]:
                    result_string = last_string[1].split(":") 
                    #print("result string: ", result_string[1])
                    specific_char_trimmed1 = result_string[1].rstrip("'")
                    specific_char_trimmed2 = specific_char_trimmed1.lstrip(" ")
                    specific_char_trimmed3 = specific_char_trimmed2.lstrip("'")

                     #logica de ser diferente do anterior
                    self.atualQ = int(specific_char_trimmed3)
                    
                    if(self.atualQ != self.anteriorQ):
                        self.ids.text11.text = "ATIVADO"
                        self.ids.text11.color = (1,0,0,1) 
                       
                    else:
                        self.ids.text11.text = "NÃO ATIVADO"
                        self.ids.text11.color = (0,100/255,0,1) 

    
    def resS(self, *args):
        #print ("ResultS: ", self.requestS.result)
        S_global.append(self.requestS.result)
        string=' '.join([str(item) for item in S_global])
        #print('stringS: ', string)
        S_global.clear()
        if "[" in string:
            nova_string = string.split("}") 
            #print("nova string: ", nova_string[1])
            if "field" in nova_string[1]:
                last_string = nova_string[1].split("field") 
                #print("last string: ", last_string[1]) #1,2,3 ou 4 corresponde a field1 field2... = 1 : None
                if "'" in last_string[1]:
                    result_string = last_string[1].split(":") 
                    #print("result string: ", result_string[1])
                    specific_char_trimmed1 = result_string[1].rstrip("'")
                    specific_char_trimmed2 = specific_char_trimmed1.lstrip(" ")
                    specific_char_trimmed3 = specific_char_trimmed2.lstrip("'")

                    #logica de ser diferente do anterior
                    self.atualS = int(specific_char_trimmed3)
                    
                    
                    if(self.atualS != self.anteriorS):
                        self.ids.text33.text = "ATIVADO"
                        self.ids.text33.color = (1,0,0,1) 
                        
                      
                    else:
                        self.ids.text33.text = "NÃO ATIVADO"
                        self.ids.text33.color = (0,100/255,0,1) 
    def updateSOS(self, dt):
        self.anteriorS = self.atualS
        
        
    def updateQUEDA(self, dt):
        self.anteriorQ = self.atualQ
        

    def resL(self, *args):
        #print ("ResultL: ", self.requestL.result)
        L_global.append(self.requestL.result)
        string=' '.join([str(item) for item in L_global])
        #print('stringL: ', string)
        L_global.clear()
        if "[" in string:
            nova_string = string.split("}") 
            #print("nova string: ", nova_string[1])
            if "field" in nova_string[1]:
                last_string = nova_string[1].split("field") 
                #print("last string: ", last_string[1]) #1,2,3 ou 4 corresponde a field1 field2... = 1 : None
                if "'" in last_string[1] and "'" in last_string[2]:
                    result_string1 = last_string[1].split(":") 
                    result_string2 = last_string[2].split(":") 
                    final_string = result_string1 + result_string2
                    #print("result string: ", final_string)
                    specific_char_trimmed1 = final_string[1].rstrip("'")
                    specific_char_trimmed2 = specific_char_trimmed1.rstrip(" ")
                    specific_char_trimmed3 = specific_char_trimmed2.rstrip(",")
                    specific_char_trimmed4 = specific_char_trimmed3.rstrip("'")
                    specific_char_trimmed5 = specific_char_trimmed4.lstrip(" ")
                    specific_char_trimmed6 = specific_char_trimmed5.lstrip("'")

                    specific_char_trimmed11 = final_string[3].rstrip(",")
                    specific_char_trimmed22 = specific_char_trimmed11.rstrip("'")
                    specific_char_trimmed33 = specific_char_trimmed22.lstrip(" ")
                    specific_char_trimmed44 = specific_char_trimmed33.lstrip("'")
                    
                    self.map = self.ids.mapview
                    atual = MapMarker(lat= float(specific_char_trimmed6), lon= float(specific_char_trimmed44))
                    if(atual == self.anteriorL or self.flagLocs == 1):  
                    	self.map.add_marker(atual) 
                    	self.map.center_on(float(specific_char_trimmed6), float(specific_char_trimmed44))
                    	self.anteriorL = atual
                    	self.flagLocs = 0
                    if(atual != self.anteriorL):
                    	self.map.remove_marker(self.anteriorL)
                    	self.map.add_marker(atual)
                    	self.map.center_on(float(specific_char_trimmed6), float(specific_char_trimmed44))
                    	self.anteriorL = atual
                    	
                    
                    	

    def resLem(self, *args):
        print("Lembrete posted!")

    def listb(self):
        app.screen_manager.current = "List"
   
    def add(self):
        global freq
        global controlspinner
        global listlembrete
        listlembrete.append(self.ids.input1.text)
        listlembrete.append(self.ids.input2.text)
        listlembrete.append(freq)
        app.list_page.update_info(listlembrete)
        self.ids.input1.text = ""
        self.ids.input2.text = ""
        self.ids.freq.text = "Clique para selecionar"
        MultiSelectSpinner().selected_values=[] 
        controlspinner = 1
        self.send_variable()
        
       
    pass



class MultiSelectSpinner(Button):
    
    """Widget allowing to select multiple text options."""

    dropdown = ObjectProperty(None)
    """(internal) DropDown used with MultiSelectSpinner."""

    values = ListProperty([])
    """Values to choose from."""

    selected_values = ListProperty([])
    """List of values selected by the user."""
    def __init__(self, **kwargs):
        self.bind(dropdown=self.update_dropdown)
        self.bind(values=self.update_dropdown)
        super(MultiSelectSpinner, self).__init__(**kwargs)
        self.bind(on_release=self.toggle_dropdown)
    def toggle_dropdown(self, *args):
        if self.dropdown.parent:
            self.dropdown.dismiss()
        else:
            self.dropdown.open(self)
            global controlspinner
            if controlspinner == 1:
                    self.selected_values.clear()
                    self.update_dropdown()
                    controlspinner = 0

    def update_dropdown(self, *args):
        if not self.dropdown:
            self.dropdown = DropDown()
        values = self.values
        if values:
            if self.dropdown.children:
                self.dropdown.clear_widgets()
            for value in values:
                b = Factory.MultiSelectOption(text=value)
                b.bind(state=self.select_value)
                self.dropdown.add_widget(b)
            

    def select_value(self, instance, value):
        if value == 'down':
            if instance.text not in self.selected_values:
                self.selected_values.append(instance.text)
        else:
            if instance.text in self.selected_values:
                self.selected_values.remove(instance.text)
        
    
    def on_selected_values(self, instance, value):
        global freq
        if value:
            self.text = ', '.join(value)
        else:
            self.text = ''
            
        freq = self.text
    
    
        

class ListPage(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.load_data()
        
        
    def update_info(self, message):
        app.main_page.save_data()
        self.gridLayout = GridLayout(size_hint_y=0.5)
        self.gridLayout.cols = 2
        self.gridLayout.padding = [0, 0, 0, 0]
        self.gridLayout.bind(minimum_height=self.gridLayout.setter('height'))
        self.add_widget(self.gridLayout)

        self.listof_label = Label(text="",
                font_size=35,
                font_name= 'Roboto',
                halign="center",
                valign="middle",
                markup= True,
                color= (0,0,0,1))
        self.gridLayout.add_widget(self.listof_label)
        self.active = CheckBox(active = False,
        size_hint_y= 0.1,
        size_hint_x= 0.1,)
        self.active.color=(0,0,0,1)
        self.active.group="lembretes"
        self.gridLayout.add_widget(self.active)
        self.active.bind(active = self.check_click)

        lista = ""
        global all_lembretes
        
        
        for i in range(0, len(message), 3):
            lista = message[i] + " " + message[i+1] + " " + message[i+2] 
            all_lembretes.append(message[i]) 
            all_lembretes.append(message[i+1]) 
            all_lembretes.append(message[i+2]) 
            
        self.listof_label.text = lista 
            
        all_lembretes.append(self.active) #checkbox
        
    def load_data(self):
        global listlembrete
        try:
            print("load")
            pickle_in = open("mypickle.pickle", 'rb')
            reloaded_list = pickle.load(pickle_in)
            lista = []
            for i in range(0, len(reloaded_list), 3):
                lista.append(reloaded_list[i])
                lista.append(reloaded_list[i+1])
                lista.append(reloaded_list[i+2])
                listlembrete.append(reloaded_list[i])
                listlembrete.append(reloaded_list[i+1])
                listlembrete.append(reloaded_list[i+2])
                #print("lista pra passar: ", lista)
                
                self.update_info(lista)
                
                
        except:
            print("error")
            
            
    def check_click(self, instance, value):
        global aux_lembretes
        if value == True:
            aux_lembretes.clear()
            for i in range(0, len(all_lembretes)):
                if instance == all_lembretes[i]:
                    aux_lembretes.append(all_lembretes[i-3])
                    aux_lembretes.append(all_lembretes[i-2])
                    aux_lembretes.append(all_lembretes[i-1])

                    self.newgrid = GridLayout(size_hint_y=None, height=120)
                    self.newgrid.cols = 1
                    self.newgrid.padding = [0, 0, 0, 0]
                    self.newgrid.bind(minimum_height=self.newgrid.setter('height'))
                    self.add_widget(self.newgrid)
                    self.delb = Button(text="Deletar",
                            font_size=35,
                            font_name= 'Roboto',
                            halign="center",
                            valign="middle",
                            markup= True,
                            color= (1,1,1,1),
                            background_color= (255/255, 0/255, 0/255, 0.8)
                            )
                    self.delb.bind(on_press = self.delete_item)
                    self.newgrid.add_widget(self.delb)
        if value == False:
            self.newgrid.remove_widget(self.delb)
            self.remove_widget(self.newgrid)

    def delete_item(self, *args):
        global aux_lembretes
            
        self.clear_widgets()
        self.add_widget(self.ids.box4)
        
        listlembrete.remove(aux_lembretes[0])
        listlembrete.remove(aux_lembretes[1])
        listlembrete.remove(aux_lembretes[2])

        self.newgrid.remove_widget(self.delb)
        self.remove_widget(self.newgrid)
        
        self.send_variable()
        listal = []

        for i in range(0, len(listlembrete), 3):
            listal.append(listlembrete[i])
            listal.append(listlembrete[i+1])
            listal.append(listlembrete[i+2])
            
            self.update_info(listal)
        
        
    def send_variable(self):
        global listlembrete
        print("send variable")
        client = OSCClient('localhost', 5005)
        teste = str(listlembrete)
        messageE = teste.encode('utf-8')
        client.send_message(b'/path', [messageE])



    def mainb(self):
        app.screen_manager.current = "Main"
        
    
    

class main(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        self.main_page = MyWidget()
        screen = Screen(name="Main")
        screen.add_widget(self.main_page)
        self.screen_manager.add_widget(screen)
        
      
        self.list_page = ListPage()
        screen = Screen(name="List")
        screen.add_widget(self.list_page)
        self.screen_manager.add_widget(screen)
        
        
        return self.screen_manager
        

if __name__ == '__main__':
    app = main()
    app.run()
