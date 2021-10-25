import PySimpleGUI as sg
import numpy as np
import pandas as pd
from PIL import Image, ImageFont, ImageDraw
import io
from os import path, makedirs, chdir
import os
import json
import copy


class App():
    path = os.path.dirname(os.path.realpath(__file__))
    path_csv = path + '\\Csvs'
    path_banner = path + '\\Banners'
    path_json = path + '\\Jsons'

    def __init__(self,root='.',size = (1200,600),fontsize = 11, banner_size = (800,600)):
        chdir(root)
        self.size = size
        self.fontsize = fontsize
        self.banner_size = banner_size
        
        sg.theme('Light Grey 3')

        self.seed = []
        self.idx_of_selected_element = -1
        self.list_of_elements = []

        panel_menu = [
            ['&Arquivo',['&Abrir',['&csv::open','&json::open'],'&Salvar',['&csv::save','&json::save'],'&Resetar','Sai&r']],
            ['&Ferramentas',['&Gerar']],
            ['A&juda',['&Em construção...']],
        ]

        panel_1 = sg.Column([
            [sg.Text("Elementos")],
            [sg.Listbox(values=self.list_of_elements_name,size=(23,27),font=('Arial',fontsize),key='element-list',enable_events=True,no_scrollbar=True,expand_x=True)],
            [sg.Button("Adicionar",key='element-add'),sg.Button("Remover",key='element-remove')],
            [sg.Button("Subir",key='element-moveup'),sg.Button("Descer",key='element-movedown'),sg.Button("Duplicar",key='element-copy')]
        ],size=(200,self.size[1]),key='panel-1')

        tab_elements = [
            [sg.Text("Nome do elemento: "),sg.Input('',size=(30,1),key='element-name',enable_events=True)],
            [sg.Text("Tipo de elemento: "),sg.Combo(['texto','imagem'],key='element-type',enable_events=True,readonly=True)],
            [sg.Text("Conteúdo do elemento: ")],
            [sg.Multiline(expand_x=True,size=(7,27),key='element-content')],
            [sg.Button('Salvar',key='element-content-save')],
            
            # [sg.Button("Ler csv"),sg.Button("Salvar csv")]
        ]

        image_styles = [

            # adiciona o botão na interface
            [sg.Frame("Palavras por linha",[
                [sg.Text("Quantidade"),sg.Spin(list(range(1,self.banner_size[0])),initial_value=5,size=(10,1),enable_events=True,key='style-words')]
            ])], #new_add

            [sg.Frame("Posição",[
                [sg.Text("x"),sg.Spin(list(range(-self.banner_size[0],self.banner_size[0])),initial_value=1,size=(10,1),enable_events=True,key='style-position-x'),
                sg.Text("y"),sg.Spin(list(range(-self.banner_size[1],self.banner_size[1])),initial_value=1,size=(10,1),enable_events=True,key='style-position-y')]
            ])],
            [sg.Frame("Tamanho",[
                [
                    sg.Spin(list(range(10000)),initial_value=1,size=(10,1),enable_events=True,key='style-size-value'),
                    sg.Radio('Largura','style-size-type',default=True,enable_events=True,key='style-size-width'),
                    sg.Radio('Altura','style-size-type',enable_events=True,key='style-size-height')
                ],
                # [sg.Frame('Valor',[
                #     [sg.Radio('Largura','tipo-tamanho',key='style-size-width'),sg.Radio('Altura','tipo-tamanho',key='style-size-height')]
                # ])]
                # [sg.Text("largura"),sg.Spin(list(range(self.size[0])),initial_value=1,size=(10,1),enable_events=True,key='style-size-width'),
                # sg.Text("altura"),sg.Spin(list(range(self.size[0])),initial_value=1,size=(10,1),enable_events=True,key='style-size-height')]
            ])],
            [sg.Text("Fonte"),sg.Input(size=(20,1),enable_events=True,key='style-font')],
            [sg.Frame("Cor",[
                [sg.Text("RGB"),sg.Spin(list(range(256)),size=(6,1),enable_events=True,key='style-color-r'),sg.Spin(list(range(256)),size=(6,1),enable_events=True,key='style-color-g'),sg.Spin(list(range(256)),size=(6,1),enable_events=True,key='style-color-b')],
                [sg.Text("HEX"),sg.Input(size=(8,1),enable_events=True,key='style-color-hex')]
            ])],
            [sg.Frame("Opacidade",[
                [sg.Slider(range=(0,1),default_value=1,resolution=0.01,orientation='horizontal',trough_color='gray',enable_events=True,key='style-opacity')]
            ])],
            # [sg.Frame("Opcionais",[
            #     [sg.Checkbox(" Multiline",key='style-multiline')],
            #     [sg.Spin(range(1,11), initial_value=1,size=(10,1)), sg.Text('Volume level')]
            # ])],
        ]

        tab_style = [
            *image_styles
        ]

        panel_2 = sg.Column([
            [sg.TabGroup([
                [sg.Tab('Conteúdo',tab_elements),sg.Tab('Estilo',tab_style,key='tab-styles')]
            ])]
        ],size=(self.size[0]//2-200,self.size[1]),key='panel-2')

        self.available_banner_size = (self.size[0]//3-10,self.size[1]-100)
        self.create_preview()

        panel_3 = sg.Column([
            [sg.Frame("Dimensões",[
                [sg.Text("Largura"),sg.Spin([i for i in range(1,10000)],initial_value=self.banner_size[0],size=(15,1),key='banner-width',enable_events=True),
                sg.Text("Altura") ,sg.Spin([i for i in range(1,10000)],initial_value=self.banner_size[1],size=(15,1),key='banner-height',enable_events=True)],
            ],element_justification='center',expand_x=True)],
            [sg.Image(self.preview_img,key='banner-image',size=self.available_banner_size,background_color="gray")],
            [sg.Column([[sg.Button('Gerar',key='gerar-seed')]],justification='center'),sg.Input('',key='banner-seed',enable_events=True)]
        ],size=(self.size[0]//2-200,self.size[1]),element_justification='center',key='panel-3')

        layout = [
            [sg.Menu(panel_menu)],
            [panel_1,sg.VerticalSeparator(),panel_2,sg.VerticalSeparator(),panel_3],
        ]

        self.window = sg.Window("Main Window",layout,finalize=True,element_justification='c')

        # binding events
        # self.window['element-content'].bind('<FocusOut>','-out')
        # self.window['element-content'].bind('<Leave>','-out')
        for label in ['position-x','position-y','size-width','size-height','size-value','font','color-r','color-g','color-b','color-hex','opacity', 'words']:
            self.window['style-'+label].bind('<Key>','-enter')
        self.window['banner-width'].bind('<Key>','-enter')
        self.window['banner-height'].bind('<Key>','-enter')
        self.window['tab-styles'].bind('<FocusOut>','-changed')
        
        # disabling contents by default
        self.disable_contents_and_styles()

    def run(self):
        while True:
            self.event, self.value = self.window.read()
            print(self.event, self.value)
            if self.check_win_close(): break
            # menu
            if self.event == 'Resetar': self.reset()
            elif self.event == 'csv::open': self.read_csv()
            elif self.event == 'json::open': self.read_json()
            elif self.event == 'csv::save': self.save_csv()
            elif self.event == 'json::save': self.save_json()
            elif self.event == 'Gerar': self.generate_banner_images()
            elif self.event == 'Em construção...': sg.popup_ok("Em breve, uma descrição do uso.")
            # panel_1
            elif self.event == 'element-add': self.add_element()
            elif self.list_of_elements == [] or self.idx_of_selected_element == None: continue
            # panel_2
            # content
            elif self.event == 'element-type': self.set_prop('type')
                # self.window['style-font'].update(disabled=self.selected_element['type'] == 'imagem')
            elif self.event == 'element-content-save': self.set_prop('content',key='element-content',transform=lambda text: list(filter(lambda t: t!='',text.split('\n'))))
            elif self.event == 'element-name': self.set_prop('name',transform=lambda name: name.replace(' ','_'))
            elif self.event == 'element-list': self.select_element()
            elif self.event == 'element-remove': self.remove_element()
            elif self.event == 'element-copy': self.copy_element()
            elif self.event == 'element-moveup': self.move_element('up')
            elif self.event == 'element-movedown': self.move_element('down')
            # style
            self.event = self.event.replace('-enter','').replace('-changed','')
            try:
                
                if self.event == 'style-words': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else int(number)) #new_add
                elif self.event == 'style-position-x': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else int(number))
                elif self.event == 'style-position-y': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else int(number))
                elif self.event == 'style-color-r': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else min(255,int(number)))
                elif self.event == 'style-color-g': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else min(255,int(number)))
                elif self.event == 'style-color-b': self.set_prop(self.event.split('-'),transform=lambda number: 0 if number == '' else min(255,int(number)))
                elif self.event == 'style-color-hex' and len(self.value['style-color-hex']) == 7:
                    self.set_prop(['style','color','r'],transform=lambda hex: int(hex[1:3],16))
                    self.set_prop(['style','color','g'],transform=lambda hex: int(hex[3:5],16))
                    self.set_prop(['style','color','b'],transform=lambda hex: int(hex[5:7],16))
                elif self.event == 'style-opacity': self.set_prop(self.event.split('-'))#,transform=lambda number: 0 if number == '' else max(0,min(1,float(number))))
                elif self.event == 'style-font': self.set_prop(self.event.split('-'))
                elif self.event == 'style-size-value': self.set_prop(self.event.split('-'))
                elif self.event == 'style-size-width': self.set_prop('style-size-type'.split('-'),transform=lambda d: 'width')
                elif self.event == 'style-size-height': self.set_prop('style-size-type'.split('-'),transform=lambda d: 'height')
                # panel_3
                elif self.event == 'banner-width' or self.event == 'banner-height': self.resize_preview()
                elif self.event == 'banner-seed': self.set_seet_from_window(); self.update_seed(); self.refresh_preview()
                elif self.event == 'gerar-seed': self.generate_seed(); self.update_seed(); self.refresh_preview()
            except ValueError:
                pass

    @property
    def selected_element(self):
        return None if self.idx_of_selected_element == -1 else self.list_of_elements[self.idx_of_selected_element]

    @property
    def list_of_elements_name(self):
        return [el['name'] for el in self.list_of_elements]

    @property
    def banner_reduced_size(self):
        width = self.size[0]//3-10
        height = self.size[1]-20
        available_ratio = width/height
        banner_ratio = self.banner_size[0]/self.banner_size[1]
        if banner_ratio > available_ratio:
            height = width / banner_ratio
        elif banner_ratio < available_ratio:
            width = height * banner_ratio
        available_ratio = width/height
        return width,height

    def set_prop(self,prop,key=None,element=None,update_window=True,transform=lambda x:x):
        element = element or self.selected_element
        if not isinstance(prop,list):
            prop = [prop]
        aux = element
        for p in prop[:-1]:
            aux = aux[p]
        key = key or self.event
        aux[prop[-1]] = transform(self.value[key])
        if update_window:
            self.update_window()
    
    def has_selected(self):
        return self.selected_element is not None

    def update_window(self):
        self.update_content()
        self.update_style()
        self.update_list()
        # self.window['banner-width'].update(value=self.size[0])
        # self.window['banner-height'].update(value=self.size[1])
        self.window['banner-width'].update(value=self.banner_size[0])
        self.window['banner-height'].update(value=self.banner_size[1])
        self.update_seed()
        self.refresh_preview()

    def select_element(self):
        if self.has_selected():
            self.enable_contents_and_styles()
            self.idx_of_selected_element = [i for i,n in enumerate(self.list_of_elements_name) if n == self.value['element-list'][0].split(' ')[0]][0]
            self.update_content()
            self.update_style()
        else:
            self.disable_contents_and_styles()
    
    def disable_contents_and_styles(self):
        self.disable(['element-name','element-type','element-content','element-content-save','style-position-x','style-position-y','style-size-value','style-size-width','style-size-height','style-font','style-color-r','style-color-g','style-color-b','style-color-hex'])
    
    def enable_contents_and_styles(self):
        self.enable(['element-name','element-type','element-content','element-content-save','style-position-x','style-position-y','style-size-value','style-size-width','style-size-height','style-font','style-color-r','style-color-g','style-color-b','style-color-hex'])

    def disable(self,widgets):
        if not isinstance(widgets,list): widgets = [widgets]
        for w in widgets: self.window[w].update(disabled=True)

    def enable(self,widgets):
        if not isinstance(widgets,list): widgets = [widgets]
        for w in widgets: self.window[w].update(disabled=False)

    def copy_element(self):
        if self.has_selected():
            copy_of_element = copy.deepcopy(self.selected_element)
            name = copy_of_element['name'] + '_copy'
            if name in self.list_of_elements_name:
                i = 1
                while name + f'_{i}' in self.list_of_elements_name: i+=1
                name = name + f'_{i}'
            copy_of_element['name'] = name
            self.list_of_elements.insert(self.idx_of_selected_element+1,copy_of_element)
        self.update_window()
        self.window['element-list'].set_focus(force=True)
        self.window['element-list'].update(set_to_index=self.idx_of_selected_element)

    def move_element(self,movement):
        if movement == 'up' and self.idx_of_selected_element > 0:
            self.list_of_elements = self.list_of_elements[:self.idx_of_selected_element-1] + [self.list_of_elements[self.idx_of_selected_element]] + [self.list_of_elements[self.idx_of_selected_element-1]] + self.list_of_elements[self.idx_of_selected_element+1:]
            self.idx_of_selected_element = self.idx_of_selected_element - 1
        elif movement == 'down' and self.idx_of_selected_element < len(self.list_of_elements)-1:
            self.list_of_elements = self.list_of_elements[:self.idx_of_selected_element] + [self.list_of_elements[self.idx_of_selected_element+1]] + [self.list_of_elements[self.idx_of_selected_element]] + self.list_of_elements[self.idx_of_selected_element+2:]
            self.idx_of_selected_element = self.idx_of_selected_element + 1
        self.update_window()
        self.window['element-list'].set_focus(force=True)
        self.window['element-list'].update(set_to_index=self.idx_of_selected_element)
        
    def reset(self):
        self.list_of_elements = []
        self.idx_of_selected_element = -1
        self.update_window()

    def read_csv(self):
        csv_file = sg.popup_get_file("Escolha o arquivo CSV com o conteúdo dos elementos.\nO separador será ';'.",file_types=(('ALL Files', '*.csv'),),)
        if not csv_file: return
        df = pd.read_csv(csv_file,sep=';', encoding='cp1252')
        df.fillna('',inplace=True)
        elements_name = self.list_of_elements_name
        for name,value in df.items():
            if name.startswith('t_'):
                el_type = 'texto'
                name = name[2:]
            elif name.startswith('i_'):
                el_type = 'imagem'
                name = name[2:]
            else:
                el_type = 'text'
            if name in elements_name:
                elem = list(filter(lambda el: el['name'] == name, self.list_of_elements))[0]
            else:
                self.list_of_elements.append(self.__create_raw_element(name=name,type=el_type))
                self.idx_of_selected_element = len(self.list_of_elements)-1
                elem = self.selected_element
            print(name,value)
            for v in value:
                if v == '': continue
                elem['content'].append(v if type(v) == str else str(v))
        self.update_window()
    
    def read_json(self):
        json_file = sg.popup_get_file("Escolha o arquivo JSON com os estilos dos elementos.",file_types=(('ALL Files', '*.json'),),)
        if not json_file: return
        global_styles = json.load(open(json_file,'r'))
        elements_name = self.list_of_elements_name

        #self.size = tuple(global_styles['size'])
        self.banner_size = tuple(global_styles['size'])#####-------------------

        for el_type,elements in zip(['texto','imagem'],[global_styles['texts'].items(),global_styles['images'].items()]):
            for name,style in elements:
                style_default = dict(
                    position=style.get('position',dict(x=0,y=0)),
                    size=style.get('size',dict(value=self.size[0] if el_type == 'imagem' else 100,type='width')),
                    font=style.get('font','arial.ttf'),
                    color=style.get('color',dict(r=0,g=0,b=0)),
                    opacity=style.get('opacity',1.0),
                    words=style.get('words',5) #new_add
                )
                if name in elements_name:
                    elem = list(filter(lambda el: el['name'] == name, self.list_of_elements))[0]
                    elem['style'] = style_default
                else:
                    self.list_of_elements.append(self.__create_raw_element(name=name,type=el_type,**style_default))
                    self.idx_of_selected_element = len(self.list_of_elements)-1
        new_list_of_elements = []
        order_of_elements = global_styles['z-order'] + list(set(self.list_of_elements_name).difference(global_styles['z-order']))
        for i_name in order_of_elements:
            for elem in self.list_of_elements:
                if elem['name'] == i_name:
                    new_list_of_elements.append(elem)
        self.list_of_elements = new_list_of_elements
        self.idx_of_selected_element = 0
        self.update_window()
    
    def save_csv(self):
        csv_file = sg.popup_get_file("Escolha o arquivo CSV para salvar",save_as=True,file_types=(('ALL Files', '*.csv'),),)
        if not csv_file: return
        if len(self.list_of_elements) == 0:
            sg.popup_ok("Salvamento não realizado: Não há elementos presentes.")
            return
        df = pd.DataFrame({})
        index_size = max([len(element['content']) for element in self.list_of_elements])
        for element in self.list_of_elements:
            name = element['name']
            el_type = element['type']
            content = element['content']
            key = ("i_" if el_type == "imagem" else "t_") + name
            df[key] = content + [''] * (index_size - len(content))
        df.to_csv(csv_file,sep=';',index=False, encoding='cp1252')
    
    def save_json(self):
        json_file = sg.popup_get_file("Escolha o arquivo JSON com os estilos dos elementos.",save_as=True,file_types=(('ALL Files', '*.json'),),)
        if not json_file: return
        if len(self.list_of_elements) == 0:
            sg.popup_ok("Salvamento não realizado: Não há elementos presentes.")
            return
        global_styles = {
            'size': self.banner_size,
            'z-order': self.list_of_elements_name,
            'texts':{},
            'images':{}, 
        }
        for element in self.list_of_elements:
            if element['type'] == 'texto':
                global_styles['texts'][element['name']] = element['style']
            elif element['type'] == 'imagem':
                global_styles['images'][element['name']] = element['style']
        json.dump(global_styles,open(json_file,'w'),indent=4)
    
    def __prepare_text(self, text, style): #new_add
        sample = str()
        text = text.split(' ')
        breaks = list()
        words = style['words']
        for i in range(0, len(text)):
            j = i * words
            k = j + words
            if len(text[j:k]) >> 0:
                breaks.append((j, k))
            else:
                break

        for i in breaks:
            j, k = i
            __text = text[j:k]
            __text = ' '.join(__text)
            sample = sample + __text + '\n'
        return sample
    
    def generate_banner_images(self):
        if len(self.list_of_elements) == 0:
            sg.popup_ok("Banners não gerados: Não há elementos presentes.")
            return
        directory_file = 'banner_' + str(np.random.randint(100000,999999))

        path_ = os.path.join(self.path_banner, directory_file)
        makedirs(path_)

        # '''Pega todos os content dos elementos e cria uma lista com sua quantidade'''
        # seeds_range = [list(range(len(elem['content']))) for elem in self.list_of_elements]

        # '''Cria lista mesclando todos os content dos elementos'''
        # all_seeds = np.array(np.meshgrid(*seeds_range)).T.reshape(-1,len(seeds_range))

        all_seeds = list()
        seeds_range = [len(elem['content']) for elem in self.list_of_elements]

        for c in range(seeds_range[0]):
            all_seeds.append([c for i in range(len(seeds_range))])

        all_seeds  = np.array(all_seeds)
        
        for seed in all_seeds:
            img = Image.new('RGBA',self.banner_size,(255,255,255,255))
            for i,e in zip(seed,self.list_of_elements):
                style = e['style']
                if e['type'] == 'texto':
                    self.__paste_text(img,self.__prepare_text(e['content'][i], style),style)
                elif e['type'] == 'imagem':
                    self.__paste_image(img,e['content'][i],style)

            fname = path.join(path_,'image_' + '_'.join(seed.astype(str).tolist())+'.png')
            img.save(fname)
        sg.popup_ok("Banners salvos no diretório: "+directory_file)

    def update_list(self):
        self.window['element-list'].update(values=[f"{el['name']} ({el['type']})" for el in self.list_of_elements])

    def update_content(self):
        if self.has_selected():
            self.enable_contents_and_styles()
            self.window['element-name'].update(value=self.selected_element['name'])
            self.window['element-type'].update(set_to_index=dict(texto=0,imagem=1)[self.selected_element['type']])
            self.window['element-content'].update(value='\n'.join(self.selected_element['content']))
        else:
            self.disable_contents_and_styles()
        
    def update_style(self):
        if self.has_selected():
            self.enable_contents_and_styles()
            style = self.selected_element['style']
            """
            atualize o valor do campo clicando no botão
            """
            self.window['style-words'].update(value=style['words']) #new_add
            self.window['style-position-x'].update(value=style['position']['x'])
            self.window['style-position-y'].update(value=style['position']['y'])
            self.window['style-size-value'].update(value=style['size']['value'])
            self.window['style-size-width'].update(value=style['size']['type'] == 'width')
            self.window['style-size-height'].update(value=style['size']['type'] == 'height')
            self.window['style-opacity'].update(value=style['opacity'])
            self.window['style-font'].update(value=style['font'])
            self.window['style-font'].update(disabled=self.selected_element['type'] == 'imagem')
            self.window['style-color-r'].update(value=style['color']['r'])
            self.window['style-color-g'].update(value=style['color']['g'])
            self.window['style-color-b'].update(value=style['color']['b'])
            color = style['color']['r'],style['color']['g'],style['color']['b']
            self.window['style-color-hex'].update(value='#{:02x}{:02x}{:02x}'.format(*color))
        else:
            self.disable_contents_and_styles()

    def set_seet_from_window(self):
        self.seed = self.value['banner-seed'].split('-')

    def generate_seed(self):
        self.seed = filter_numeric([str(np.random.randint(len(elem['content']))) for elem in self.list_of_elements])

    def update_seed(self):
        self.seed = self.seed[:len(self.seed)] + ['0'] * max(0,len(self.list_of_elements) - len(self.seed))
        self.seed = self.seed[:len(self.list_of_elements)]
        self.seed = [str(max(0,min(int(seed),len(elem['content'])-1))) for elem,seed in zip(self.list_of_elements,self.seed)]
        self.window['banner-seed'].update(value='-'.join(self.seed))

    def __create_raw_element(self,**kwargs):

        if 'name' in kwargs.keys():
            element_name = kwargs['name']
        else:
            counter = 1
            while 'elemento-'+str(counter) in self.list_of_elements_name:
                counter += 1
            element_name = 'elemento-'+str(counter)
        return dict(
            name=element_name,
            type=kwargs.get('type','texto'),
            style=dict(
                position=kwargs.get('position',dict(x=0,y=0)),
                size=kwargs.get('size',dict(value=100,type='width')),
                font=kwargs.get('font','arial.ttf'),
                color=kwargs.get('color',dict(r=0,g=0,b=0)),
                opacity=kwargs.get('opacity',1.0),
                words=kwargs.get('words',5)  #new_add adicione mais um parâmetro ao arquivo json exportado
            ),
            content=[]
        )

    def add_element(self):
        self.list_of_elements.append(self.__create_raw_element())
        self.idx_of_selected_element = len(self.list_of_elements)-1
        self.update_window()
        self.window['element-list'].update(set_to_index=self.idx_of_selected_element)
        self.window['element-list'].set_focus(force=True)
    
    def remove_element(self):
        if self.window['element-list'].get() == []: return
        select_element = self.selected_element['name']
        for i,name in enumerate(self.list_of_elements_name):
            if name == select_element:
                del self.list_of_elements[i]
                break
        self.idx_of_selected_element = min(max(0,self.idx_of_selected_element-1),len(self.list_of_elements)-1)
        self.update_window()
        self.window['element-list'].update(set_to_index=self.idx_of_selected_element)
        self.window['element-list'].set_focus()
    
    def __paste_text(self, img, text, style):
        xy = style['position']['x'],style['position']['y']
        fill_color = style['color']['r'], style['color']['g'], style['color']['b'], int(255*style['opacity'])
        font_size = points_to_pixel(size=int(style['size']['value']),text=text,font=style['font'],fix=style['size']['type'])
        try:
            font = ImageFont.truetype(style['font'],size=font_size)
        except:
            print(f"Fonte não \"{style['font']}\" encontrada")
            font = ImageFont.truetype('arial.ttf',size=font_size)
        size = get_multiline_size(font,text)
        # img_sub = Image.new('RGBA',font.getsize(text),color=(0,0,0,0))
        img_sub = Image.new('RGBA',size,color=(0,0,0,0)) #new_add
        img_draw = ImageDraw.Draw(img_sub)
        img_draw.text((0,0),text,font=font,fill=fill_color)
        if img_sub.mode == 'RGBA':
            img.paste(img_sub,xy,mask=img_sub)
        else:
            img.paste(img_sub,xy)
    
    def __paste_image(self,img,url,style):
        try:
            img_sub = Image.open(url)
            width,height = img_sub.size[0],img_sub.size[1]
            if style['size']['type'] == 'width':
                width = int(style['size']['value'])
                height = int(img_sub.size[1] * width / img_sub.size[0])
            else:
                height = int(style['size']['value'])
                width = int(img_sub.size[0] * height / img_sub.size[1])
            img_sub = img_sub.resize((width,height))
        except FileNotFoundError:
            text = 'Imagem não encontrada'+url
            font_size = points_to_pixel(size=int(style['size']['value']),text=text,font='arial.ttf',fix=style['size']['type'])
            font = ImageFont.truetype('arial.ttf',size=font_size)
            # size = get_multiline_size(font,text)
            img_sub = Image.new('RGBA',font.getsize(text),(255,200,200,255))
            img_draw = ImageDraw.Draw(img_sub)
            img_draw.text((0,0),text,font=font,fill=(0,0,0,255))
        xy = style['position']['x'],style['position']['y']
        if img_sub.mode == 'RGBA':
            img.paste(img_sub,xy,mask=img_sub)
        else:
            img.paste(img_sub,xy)

    def create_preview(self):
        if len(self.list_of_elements) != 0:
            img = Image.new('RGBA',self.banner_size,(255,255,255,255))
            for i,elem in zip(self.seed,self.list_of_elements):
                name = elem['name']
                style = elem['style']
                xy = (style['position']['x'],style['position']['y'])
                content = elem['content'][int(i)] if len(elem['content']) != 0 else ''
                if elem['type'] == 'texto' and content != '':
                    self.__paste_text(img,self.__prepare_text(content, style),style)
                    # self.__paste_text(img,content,style)
                    # img.paste(img_sub,xy,mask=img_sub)
                elif elem['type'] == 'imagem' and content != '':
                    self.__paste_image(img,content,style)
                    # if img_sub.mode == 'RGBA':
                    #     img.paste(img_sub,xy,mask=img_sub)
                    # else:
                    #     img.paste(img_sub,xy)
        else:
            # img = Image.open('images\default.jpg')).crop((0,0,*self.banner_size))
            img = Image.new('RGBA',self.banner_size,(255,255,255,255))
            # style = self.__create_raw_element()['style']
            # style['size']['type'] = "width"
            # style['size']['value'] = (3*self.banner_size[0])//5
            # style['position']['x'] = (1*self.banner_size[0])//5
            # style['position']['y'] = (1*self.banner_size[0])//5
            # style['color']['r'],style['color']['g'],style['color']['b'] = 222,222,222
            # self.__paste_text(img,'',style)
            # img.paste(img_sub,xy,mask=img_sub)
        img.thumbnail(self.available_banner_size)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        self.preview_img = bio.getvalue()
        del img

    def check_win_close(self):
        return self.event == sg.WIN_CLOSED or self.event == 'Exit' or self.event == 'Sair'

    def refresh_preview(self):
        self.create_preview()
        self.window['banner-image'].update(self.preview_img)

    def resize_preview(self):
        width = max(1,int(self.value['banner-width'] or 1))
        height = max(1,int(self.value['banner-height'] or 1))
        self.banner_size = width,height
        self.refresh_preview()
        # self.create_preview()
        # self.window['banner-image'].set_size(size=self.banner_reduced_size)

def get_multiline_size(font,text):
    multiline_text = text.split('\n')
    size = [0,0]
    for line in multiline_text:
        _size = font.getsize(line)
        size[0] = max(size[0],_size[0])
        size[1] += _size[1]
    size[1]+= len(multiline_text)*4
    size[0]+=4
    return size

def filter_numeric(value: list) -> list:
    for i,val in enumerate(value):
        value[i] = ''.join([c for c in val if c in '0123456789'])
        value[i] = '0' if value[i] == '' else value[i]
    return value

def points_to_pixel(size,text,font,fix='width'):
    try:
        if fix == 'width':
            coef = (ImageFont.truetype(font,size=10).getsize(text)[0] - 1) / 10
        else:
            coef = (ImageFont.truetype(font,size=10).getsize(text)[1] - 2) / 10
    except:
        coef = 2.1
    font_size = int(size / coef)
    return font_size

if __name__ == '__main__':
    app = App(root=path.dirname(path.abspath(__file__)))
    app.run()