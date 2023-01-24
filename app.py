import os, json, time, math, random, uuid, copy, uuid
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.colorchooser import askcolor
from tkinter import ttk
import tkinter.font

import shutil

app_title = 'app_title'
for f in os.listdir(os.getcwd()):
    if 'title_' in f:
        app_title = f.partition('title_')[2].partition('.txt')[0]


# general functions

# string, starting_substring, ending_substring --> List(strings between substrings)
# basically for getting all the text between 2 given strings, in a big mess of a string, and putting them in a list
# plus an option to only get items with the strings in strings_list in it
def between2(mess,start, end, strings_list=None):
    #print({'mess':mess})
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    if strings_list == None:
        return mess[1:]
    else:
        filtered_mess = []
        for i in mess[1:]:
            for string in strings_list:
                if string in i:
                    filtered_mess.append(i)
        return filtered_mess
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    
    return mess[1:]

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def text_read(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

def text_append(path, appendage):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(appendage)

def text_create(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def clean_edges(string): # for removing whitespaces
    dirty = [" ","\t","\n"]
    while True:
        if len(string) == 0:
            return string
        if string[0] in dirty:
            string = string[1:]
        else:
            break
    while True:
        if len(string) == 0:
            return string
        if string[-1] in dirty:
            string = string[:-1]
        else:
            break
    return string

######################3 ########################## #######################

# general tkinter functions

# changes word boundaries in order to improve double-click behavior in Text and Entry widgets.
    # copypasted it from Stackoverflow lol. dont ask me how it works.
def set_word_boundaries(root):
    # this first statement triggers tcl to autoload the library
    # that defines the variables we want to override.  
    root.tk.call('tcl_wordBreakAfter', '', 0) 

    # this defines what tcl considers to be a "word". For more
    # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
    root.tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_.,]')
    root.tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_.,]')


def apply_layout(layout):
    for i in range(len(layout)):
        for j in range(len(layout[i])):
            w = layout[i][j]
            if w == None:
                continue
            w.grid(row=i,column=j)

            if type(w) == tk.Text:
                font = tkinter.font.Font(font=w['font'])
                tab = font.measure(' '*4)
                w.config(tabs=tab)


################## #################### ####################
######### app specific functions ####################

def highlight_bracketed(widget, color):
    contents = widget.get(1.0, 'end')[:-1]
    counter = 0
    for n, line in enumerate(contents.split('\n')):
        idk = 0
        for _ in range(line.count('[[')):
            if '[[' in line:
                start = f"{n+1}.{line.index('[[')+idk}"
            if ']]' in line:
                #print(line.index(']]'))
                end = f"{n+1}.{line.index(']]')+2+idk}"
                #print(end)
                widget.tag_add(counter, start, end)
                widget.tag_config(counter, foreground=color)
                idk += len(line.partition(']]')[0])+1
                line = line[line.index(']]')+2:]
                counter += 1

class Display:

    def __init__(self, parent):
        self.frame = tk.Frame(parent, **frameSettings)
        self.title = tk.Entry(self.frame, **entrySettings)
        self.tags = tk.Entry(self.frame, **entrySettings)
        self.text = tk.Text(self.frame, **textSettings)

        w = self.text
        font = tkinter.font.Font(font=w['font'])
        tab = font.measure(' '*4)
        w.config(tabs=tab)

        self.linkbuttons_frame = tk.Frame(self.frame, **frameSettings)
        self.current_passage = ''
        self.docs = {'knowledge':['frame','title','tags','text','linkbuttons_frame','current_passage','docs'],
                     'abilities':['create_linkbuttons','show_passage','initial_layout']}

    # creates buttons that show previous and next passages, and link to them
    def create_linkbuttons(self, title):
        for w in self.linkbuttons_frame.winfo_children(): #start by deleting previous passage's buttons
            w.destroy()
            
        def make_cmd(string): # for making functions that make the UI "go to" another passage
            #print(f'making for {string}')
            def cmd():
                #print(f'{string} button pressed')
                manager.wanna_change_to(string)

                new_index = titles_listbox.get(0, 'end').index(string)
                titles_listbox.selection_clear(0, 'end')
                titles_listbox.selection_set(new_index)
                titles_listbox.see(new_index)
                
            return cmd

        linkbuttons_layout = []
        for r, txt in enumerate(('previous', 'next')):
            tk.Label(self.linkbuttons_frame, text=txt, **labelSettings).grid(row=r, column=0)
            #print(f'about to enumerate on {find_passage(title)["link info"][txt]}')
            #print('error here', find_passage(title)['link info'])
            for n, linked_title in enumerate(find_passage(title)['link info'][txt]):
                #print(303, find_passage(title)['link info'][txt])
                #print(f'{title}, {txt}, linked_title:{linked_title}')
                c = n+1
                tk.Button(self.linkbuttons_frame, text=linked_title, command=make_cmd(linked_title), **buttonSettings).grid(row=r, column=c)

    # put passage information on screen
    def show_passage(self, title, source='not given'):
    
        passage = manager.get_passage(title) 
        if passage == None:
            return 0
        
        self.current_passage = title
        
        self.text.delete(1.0, 'end')
        self.text.insert(1.0, passage['text'])

##        # make sure the title is present
##        if title not in titles_listbox.get(0, 'end'):
##            return 0
##
##        # for vis
##        window.network.select_node(title)
##
        # set tags
        tags = passage['tags']
        self.tags.delete(0, 'end')
        if tags != []:
            self.tags.insert(0, ', '.join(tags))

        self.title.delete(0, 'end')
        self.title.insert(0, title)

        # set buttons to "next" and "previous"
        self.create_linkbuttons(title)

        highlight_bracketed(self.text, 'brown')

        new_index = titles_listbox.get(0, 'end').index(title)
        titles_listbox.selection_clear(0, 'end')
        titles_listbox.selection_set(new_index)
        titles_listbox.see(new_index)
        
    def initial_layout(self): # this is my initial layout.  
        layout = [
            [self.title],
            [self.tags],
            [self.text],
            [self.linkbuttons_frame]
            ]
        apply_layout(layout)
        
        # put previous and next in, so that those labels are visible when this app is started
        tk.Label(self.linkbuttons_frame, text='previous', **labelSettings).grid(row=0, column=0)
        tk.Label(self.linkbuttons_frame, text='next', **labelSettings).grid(row=1, column=0)

class Node:
    '''
stores:
    title--connections--segments--styleinfo--center--color--size--textcolor--coords--ogcenter--texttag--canvas
title = circle tag
'''
    def __init__(self, canvas, title, styleinfo):
        self.title = title
        self.connections = []
        self.segments = []

        center = styleinfo[title]['pos']
        color = styleinfo[title]['node']
        size = styleinfo[title]['size']
        textcolor = styleinfo[title]['text']

        self.center = center
        self.size = size
        
        self.coords = self.get_coords()
        self.ogcenter = self.center

        self.texttag = f'text_belonging_to_{title}'

        self.canvas = canvas

        self.canvas.create_oval(*self.coords, fill=color, tags=self.title)
        self.canvas.create_text(*center, text=self.title, fill=textcolor, tags=self.texttag, font=('comic sans',13))
        '''
        print(248, 'after creating oval and text')
        print(self.canvas.find_all())
        print()'''

    def get_coords(self):
        center = self.center
        size = self.size
        return (center[0]-size, center[1]-size, center[0]+size, center[1]+size)

class Network:
    def __init__(self, canvas, nodeinfo, styleinfo={}):
        # nodeinfo structure -> {title:{next:[title,title], previous:[]}}

        self.defaults = {'node':'grey',
                         'segment':'grey',
                         'text':'yellow',
                         'pos':(50,50),
                         'size':30}
        
        # iterate over titles and fill in defaults as necessary
        for title in nodeinfo:
            if title in styleinfo:
                for k,v in self.defaults.items():
                    if k in styleinfo[title]:
                        continue
                    else:
                        if k == 'pos':
                            styleinfo[title]['pos'] = (random.choice(range(50,500)), random.choice(range(50,500)))
                        else:
                            styleinfo[title][k] = v
            else:
                styleinfo[title] = copy.deepcopy(self.defaults)
                styleinfo[title]['pos'] = (random.choice(range(50,500)), random.choice(range(50,500)))
        self.styleinfo = styleinfo

        self.canvas = canvas
        
        self.nodeinfo = nodeinfo
        self.titles = list(nodeinfo.keys())
        self.shapetags = {}
        self.shapeids = {}
        
        self.nodes = {}
        
        self.clicked_title = None
        self.clicked_pos = None

        # initialize nodes and put in dictionary
        nodecount = 0
        for t in self.titles:
            self.nodes[t] = Node(self.canvas, t, self.styleinfo)
            i = self.canvas.find_withtag(t)
            i = i[0]
            self.shapetags[i] = t
            self.shapeids[t] = i

        # connect nodes
        for t in self.titles:
            node = self.nodes[t]
            to_connect_titles = self.nodeinfo[t]['previous'] + self.nodeinfo[t]['next']
            for other_title in to_connect_titles:
                if other_title not in self.titles:
                    #print(f'skipping other_title:{other_title} because not in self.titles')
                    continue

                other = self.nodes[other_title]
                if other not in node.connections:
                    self.connect(node, other) # draws line
                    node.connections.append(other)
                    other.connections.append(node)
                    #print(f'connected {t} to {other_title}')

        self.canvas.bind('<ButtonPress-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        for title, node in self.nodes.items():
            self.canvas.lift(node.texttag)
    
    def connect(self, node, other):
        '''
bad function name + bad abstraction/structure. but:
    2 nodes (node, other) --> nodes become connected OR their position is updated

    t0, t1 = node.title, other.title
    tags = (f'{t0}{connector}{t1}', f'{t1}{connector}{t0}')
    
'''

        t0 = node.title
        t1 = other.title
        connector = '---'
        tags = (f'{t0}{connector}{t1}', f'{t1}{connector}{t0}')

        previous = None
        if t1 in self.nodeinfo[t0]['previous']:
            previous = other
        elif t1 in self.nodeinfo[t0]['next']:
            previous = node
        else:
            previous = None

        if previous:
            linecolor = self.styleinfo[previous.title]['node']
        else:
            linecolor = self.styleinfo[previous.title]['segment']

        if len(self.canvas.find_withtag(tags[0])) == 0 or len(self.canvas.find_withtag(tags[1])) == 0:
            self.canvas.create_line(node.center, other.center, fill=linecolor, width=2, tags=tags)
        else:
            self.canvas.coords(tags[0], *node.center, *other.center)

        for t in tags:
            if len(self.canvas.find_withtag(t)) != 1:
                exit('error in def connect')

        self.canvas.lower(tags[0])
        
    def on_click(self, event):
        x,y = event.x, event.y
        halo = 1
        found = self.canvas.find_overlapping(x-halo, y-halo, x+halo, y+halo)
        for i in found:
            if i in self.shapetags:
                clicked_title = self.shapetags[i]
                self.clicked_title = clicked_title
                self.clicked_pos = (x, y)
                if 0: # debug
                    print(f'clicked on {self.clicked_title} at {x,y}')

                manager.wanna_change_to(clicked_title, source='on_click(self, event)')
                
                return 1

    def highlight_node(self, title):
        for t in self.nodes:
            if t == title:
                self.canvas.itemconfigure(t, outline='white', width=2)
            else:
                self.canvas.itemconfigure(t, outline='black', width=1)

    def on_move(self, event):
        if self.clicked_title != None:
            x, y = event.x, event.y
            delta = x-self.clicked_pos[0], y-self.clicked_pos[1]

            if 0: # debug
                print('dragging:', self.clicked_title)
                print('delta:', delta)
                print()

            # use the ogcenter to apply the proper delta. use the actual center to apply a movement
            clicked = self.nodes[self.clicked_title]
            clicked.center = (clicked.ogcenter[0]+delta[0], clicked.ogcenter[1]+delta[1]) # update center
            self.canvas.coords(self.clicked_title, *clicked.get_coords()) # calculate new coords
            
            # redraw node
            others = clicked.connections
            for other_node in others:
                # this is where you have to identify the segment and call .coords, or else you have to delete and .create_line
                self.connect(clicked, other_node)
            # redraw text
            self.canvas.coords(clicked.texttag, *clicked.center)

    def on_release(self, event):
        # just reset things and save state
        if self.clicked_title == None or self.clicked_pos == None:
            pass
        else:
            #print(self.clicked_title)
            
            node = self.nodes[self.clicked_title]
            node.ogcenter = node.center

            # update styleinfo
            self.styleinfo[node.title]['pos'] = node.center
            make_json(self.styleinfo, manager.all_info[manager.current_tab]['styleinfo_path'])

            # update rest of stuff
            self.clicked_title = None
            self.clicked_pos = None
            self.save()

    def update_positions(self):
        pass
##        # bugfix. imperfect tracking of state
##        for title, node in self.nodes.items():
##            self.positions[title] = node.center
    
    def save(self):
        pass
        # bugfix. imperfect tracking of state
##        self.update_positions()
##        make_json({'colors':self.colors, 'positions':self.positions}, 'network.json')

    def iter_segments():
        pass

class Window:
    # is intended for a parent toplevel window
    def __init__(self, parent):
        # style settings of tkinter widgets
        textSettings = {'bg':'black', 'fg':'green', 'height':global_settings['text window']['textbox height'], 'width':global_settings['text window']['textbox width'], 'font':('comic sans', 13), 'insertbackground':'white', 'selectbackground':'dark green', 'selectforeground':'white' }
        frameSettings = {'background':'black'}
        buttonSettings = {'fg':'green', 'bg':'black'}
        labelSettings = {'font':('comic sans', 13), 'fg':'green', 'bg':'black', 'width':30}
        entrySettings = {'font':('comic sans', 13), 'bg':'black', 'fg':'green', 'insertbackground':'white', 'width':30, 'selectbackground':'dark green', 'selectforeground':'white'}

        # make frame and notebook
        self.frame = tk.Frame(parent, **frameSettings)
        self.nb = ttk.Notebook(self.frame)
        self.frame.pack()
        self.nb.pack()

        self.network = None
        if 'styleinfo.json' in os.listdir(manager.current_tab):
            styleinfo = open_json(manager.all_info[manager.current_tab]['styleinfo_path'])
        else:
            styleinfo = {}
        inter_list = manager.inter_list
        self.instantiate_network(inter_list, styleinfo)

        # command stuff
        self.command_tab = tk.Frame(self.nb, **frameSettings)
        self.nb.add(self.command_tab, text='-- commands --')

        command_input = tk.Entry(self.command_tab, **entrySettings)
        command_output = tk.Text(self.command_tab, **textSettings)

        w = command_output
        font = tkinter.font.Font(font=w['font'])
        tab = font.measure(' '*4)
        w.config(tabs=tab)


        command_input.pack()
        command_output.pack()

        command_input.bind('<Return>', self.process_command)

        self.command_input = command_input
        self.command_output = command_output

    # the input can be from any tk.Entry widget, the output is always self.command_output
    def process_command(self, event):
        command = event.widget.get()
        words = command.split(' ')
        if command == 'images':
            # note: src has to be relative to from where you run tweego. not relative to where the .tw file is.
            img_location = 'story/images'
            self.command_output.insert('end', '\n'.join([f'<img src="{img_location}/{name}">' for name in os.listdir(f'{img_location}')])+'\n')
        elif 'change map' in command:
            new_tab = command.split(' ')[2]
            manager.change_tab(new_tab)
        elif command == 'jan 24':
            manager.create_mindmap()
            def apply_rules(d):
                return d

            manager.change_tab('testing_here___one') # portal
        elif command == 'all links':
            self.command_output.insert('end', '\n'.join([f'{title} ' for title in window.network.nodes.keys()])+'\n')
        elif command == 'mass color':
            lines = self.command_output.get(1.0, 'end').split('\n')
            for line in lines:
                if line == '':
                    continue
                title, new_color = line.split(' ')
                manager.change_color(title, new_color)
        elif command == 'mass link':
            in_lines = self.command_output.get(1.0, 'end').split('\n')
            out_lines = []
            for line in in_lines:
                if line == '':
                    continue
                manager.add_title(line)
                out_lines.append(f'[[{line}-->{line}]]')
            self.command_output.insert('end', '\n' + '\n'.join(out_lines))
        elif command == 'mass remove':
            in_lines = self.command_output.get(1.0, 'end').split('\n')
            for line in in_lines:
                manager.remove_title(line)
        elif words[0] == 'change':
            if words[1] == 'color':
                if len(words) == 4:
                    title = words[2]
                    new_color = words[3]
                    manager.change_color(title, new_color)
                else:
                    self.command_output.insert('end', 'example command: change color Start red\nhas to be 4 words'+'\n')
            elif words[1] == 'title':
                if len(words) == 4:
                    old = words[2]
                    new = words[3]
                    manager.change_title(old, new)
                else:
                    self.command_output.insert('end', 'example command: change title Start Beginning-of-story\nhas to be 4 words'+'\n')
        elif words[0] == 'clear':
            self.command_output.delete(1.0, 'end')
        elif words[0] == 'commands':
            if 1:
                commands = ['save', 'compile', 'get backup',
                            'commands', 'images', 'color',
                            'add passage title', 'delete passage title', 'remove passage title',
                            'change color Start red', 'change title Start Story-begins', 'css color tag newcolor', 'tagall',
                            'clear', '$e thing_to_eval', '$e c']
                self.command_output.insert('end', ', '.join(commands)+'\n(note: $e is for programmers only)\n')
        elif command == 'allnames':
            pass
        elif words[0] == 'tagall':
            for i, d in enumerate(manager.inter_list):
                title = d['title']
                tags = d['tags']
                if 'stylesheet' in tags:
                    continue
                if title not in tags:
                    manager.inter_list[i]['tags'].append(title)
            report = 'put the title as a tag for every passage, except for the current passage, and the one tagged "stylesheet"'
            self.command_output.insert('end', report+'\n')
        elif words[0] == 'add':
            if words[1] == 'passage':
                if len(words) == 2:
                    manager.add_title()
                else:
                    new_title = words[2]
                    manager.add_title(new_title)
        elif words[0] == 'delete' or words[0] == 'remove':
            if len(words) == 2:
                self.command_output.insert('end', 'example command: delete passage Start'+'\n')
            else:
                to_remove = words[2]
                manager.remove_title(to_remove)
        elif words[0] == 'save':
            manager.backup_tw()
            manager.save_tw()
        elif words[0] == 'compile':
            if len(words) == 2:
                html_name = words[1]
                manager.compile_tw(html_name)
            else:
                manager.compile_tw()
        elif words[0] == 'color':
            color = askcolor()
            report = f'{color[1]}'
            self.command_output.insert('end', report+'\n')
        elif words[0] == 'custom':
            report = f'there are no custom commands yet'
            self.command_output.insert('end', report+'\n')
        elif words[0] == 'css':
            if words[1] == 'color':
                if len(words) == 2:
                    tag = 'passagetag'
                    color = 'passagecolor'
                if len(words) == 3:
                    tag = words[2]
                    color = 'passagecolor'
                if len(words) == 4:
                    tag = words[2]
                    color = words[3]
                d = {'color':f'{color}'}
                
                lines = []
                lines.append(f'[tags="{tag}"] ' + '{')
                for k,v in d.items():
                    lines.append(f'\t{k}:{v}')
                lines.append('}')
                report = '\n'.join(lines)
            else:
                #print('command:',command, 'words:',words)
                report = f'"{command}" is not a valid command'
            self.command_output.insert('end', report+'\n')
        # a little dev tool, for running code while the app is running
        elif words[0] == '$e':
            if words[1] == 'c':
                self.command_output.delete(1.0, 'end')
            else:
                to_eval = command.partition('$e ')[2]
                self.command_output.insert('end', str(eval(to_eval))+'\n')
        else:
            report = f'"{command}" is not a valid command'
            self.command_output.insert('end', report+'\n')

    def instantiate_network(self, inter_list, styleinfo):
        '''
inter_list, styleinfo --> set window.canvas, window.styleinfo, window.nodeinfo, window.network
    '''
        firsttime = self.network == None

        if not firsttime:
            self.canvas.delete('all')
            
        self.styleinfo = styleinfo
            
        nodeinfo = {d['title']:{'next':d['link info']['next'],'previous':d['link info']['previous']} for d in inter_list}
        make_json(nodeinfo, manager.all_info[manager.current_tab]['nodeinfo_path'])
        self.nodeinfo = nodeinfo

        if firsttime:
            self.canvas = tk.Canvas(self.nb, bg='black', width=global_settings['visualization window']['canvas width'], height=global_settings['visualization window']['canvas height'])
            self.nb.add(self.canvas, text='-- diagram --')

        self.network = Network(self.canvas, self.nodeinfo, self.styleinfo)

def get_listbox_choice(listbox):
    curs = listbox.curselection()
    if len(curs) == 0:
        return None
    else:
        return listbox.get(curs[0])

# app-specific functions

def interpret_tw(string):
    # takes a raw string (like from from a .tw file) and returns an "interpretation", inter_list, a list of dictionaries
    
    if '[stylesheet]' not in string:
        pass
        #string += '\n\n::css [stylesheet]'
        
    # fix spaces
    space_repl = '-'
    titles = between2(string, '::', '\n')
    for t in titles:
        if '[' in t:
            t = t.partition(' [')[0]
        if ' ' in t:
            old = t
            new = t.replace(' ', space_repl)
            if old != new:
                string = string.replace(f'->{old}]]', f'->{new}]]')
                if f'::{old}\n' in string:
                    string = string.replace(f'::{old}\n', f'::{new}\n')
                elif f'::{old} [' in string:
                    string = string.replace(f'::{old} [', f'::{new} [')

    raw_passages = string.split('::')
    raw_passages = [f'::{p}' for p in raw_passages if p != '']

    # create inter_list. enforce ordering of keys and make extra entries to make the json more pleasant to look at
    begin = '+'*14
    end = '+'*15
    empty = ''
    inter_list = [{k:[] for k in (begin, 'title', 'tags', 'link info', 'text', empty, 'raw passage', end)} for _ in range(len(raw_passages))]

    for i, r in enumerate(raw_passages):
        inter_list[i]['raw passage'] = r
        for filling in begin, end, empty:
            inter_list[i][filling] = filling
        
    # get title, text, tags
    for i, d in enumerate(inter_list):
        r = d['raw passage']
        pretitle, _, text = r.partition('\n')

        if '[' in pretitle and ']' in pretitle:
            tags = pretitle.partition('[')[2].partition(']')[0].split(' ')
        else:
            tags = []
        title = pretitle.partition('::')[2].partition('[')[0]
        title, text = map(clean_edges, (title, text))
        tags = clean_edges(tags)
        inter_list[i]['title'] = title
        inter_list[i]['text'] = text
        inter_list[i]['tags'] = tags

    # getting links, which requires 2 iterations through inter_list.

    # getting next
    for i, d in enumerate(inter_list):
        t = d['text']
        bracketed = between2(t, '[[', ']]')

        nxt = []
        if bracketed != []:
            for b in bracketed:
                nxt.append(b.split('->')[1])
        inter_list[i]['link info'] = {'previous':[], 'next':nxt}

    # getting previous
        # first collect source info, then put into inter_list
    source_info = {d['title']:[] for d in inter_list}
    for i, d in enumerate(inter_list):
        source = d['title']
        destinations = d['link info']['next']
        #print(f'source_info:{source_info}\n\ndestinations:{destinations}')

        for dest in destinations:
            if dest not in source_info:
                continue
            source_info[dest].append(source)

    for i, d in enumerate(inter_list):
        sources = source_info[d['title']]
        for s in sources:
            inter_list[i]['link info']['previous'].append(s)

    inter_list = [d for d in inter_list if d['title'] != 'css']
    return inter_list

def examine_equality(string1, string2):
    report = []
    if string1 == string2:
        return True, report
    else:
        for l1, l2 in zip(string1.split('\n'), string2.split('\n')):
            report.append({
                'eq':l1==l2,
                'l1':l1,
                'l2':l2
            })
        return False, report

def show_report(s1, s2):
    eq, rest = examine_equality(s1, s2)
    if eq:
        print('equal')
    else:
        return 0
        for d in rest:
            if d['eq']:
                continue
            else:
                if 0:
                    print(f"l1\n{d['l1']}")
                    print(f"l2\n{d['l2']}")
                    print()
                else:
                    print(d['l1'])
                    print(d['l2'])
                    print()

def find_passage(title):
    n = next((item for item in manager.all_info[manager.current_tab]['inter_list'] if item["title"] == title), None)
    return n

def make_tw(inter_list, add_ifid=False):
    tw = []
    if add_ifid:
        if find_passage('StoryData') == None:
            pass
            ifid = str(uuid.uuid4())
            tw.append('::StoryData\n{\n\t' + f'"ifid": "{ifid}"\n' + '}')

    for d in inter_list:
        title = d['title']
        text = d['text']
        tags = d['tags']
        title = clean_edges(title)
        if tags == []:
            tw.append(f'::{title}\n{text}')
        else:
            tags = '[' + ' '.join(tags) + ']'
            tw.append(f'::{title} {tags}\n{text}')

    return '\n\n'.join(tw)

# any desired change to either the underlying files and data, or to the in-UI representation is communicated to Manager and performed here.
class Manager:
    def __init__(self):

        # sets up the structure of where things are, and holds the inter_list lists
        # none of this should change while the app is running, except for inter_list, for now
        all_info = {}
        folder = os.getcwd()
        in_folder = os.listdir(folder)
        for f in in_folder:
            if f.partition('.')[2] == 'tw':
                name = f.partition('.')[0]
                if name not in in_folder:
                    os.mkdir(name)

                all_info[name] = {'inter_list':[],
                                  'nodeinfo_path':f'{name}/nodeinfo.json',
                                  'styleinfo_path':f'{name}/styleinfo.json',
                                  'twee_path':f'{name}.tw'
                                  }
        self.all_info = all_info
        self.current_tab = list(self.all_info.keys())[0]
        
        self.inter_list = self.interpret_tw(text_read(all_info[self.current_tab]['twee_path']))
        self.fix_linkinfo_conflicts()
        self.current_passage = ''
        self.autobackup = True
    
    def create_mindmap(self):
        '''
        create new directory if necessary
            (or delete stuff in old one?)
        create new .tw
        create nodeinfo and styleinfo
        insert into self.all_info
        insert into self.inter_list
        '''
        test_folder = 'testing_here'
        for mindmap_name in ['one', 'two', 'three']:
            info = {
                'inter_list':[],
                'nodeinfo_path':f'{test_folder}/{mindmap_name}/nodeinfo.json',
                'styleinfo_path':f'{test_folder}/{mindmap_name}/styleinfo.json',
                'twee_path':f'{test_folder}/{mindmap_name}/twee.tw'
            }
            os.mkdir(f'{test_folder}/{mindmap_name}')

            def make_nodeinfo():
                return {
                    'thisis':'nodeinfo',
                    'location':test_folder + mindmap_name
                }

            def make_styleinfo():
                return {
                    'thisis':'styleinfo',
                    'location':test_folder + mindmap_name
                }

            def make_tw():
                return '::this-is\nthe twee file of ' + test_folder + mindmap_name

            # make objects
            nodeinfo = make_nodeinfo()
            styleinfo = make_styleinfo()
            twee = make_tw()
            
            # create files from objects
            make_json(nodeinfo, info['nodeinfo_path'])
            make_json(styleinfo, info['styleinfo_path'])
            text_create(info['twee_path'], twee)

            self.all_info[f'{test_folder}___{mindmap_name}'] = info
            self.all_info[f'{test_folder}___{mindmap_name}']['inter_list'] = self.interpret_tw(twee)

        self.current_passage = 'testing_here___one'
        self.inter_list = self.all_info[self.current_passage]['inter_list']

    def change_text(self, title, new_text):
        
        # helper function
        def find_next(text):
            bracketed = between2(text, '[[', ']]')

            links_to = []
            if bracketed != []:
                for b in bracketed:
                    links_to.append(b.split('->')[1])
                    
            return links_to
        
        # change in inter_list[n]:
            # - ['text']
            # - ['link info']['next']
        for n, d in enumerate(self.inter_list):
            if d['title'] == title:
                links_to = find_next(new_text)
                self.inter_list[n]['link info']['next'] = links_to
                self.inter_list[n]['text'] = new_text
                break
        
        # change in inter_list[n]:
            # - ['link info']['previous']
        for n, d in enumerate(self.inter_list):
            if d['title'] in links_to:
                for linked in links_to:
                    if title not in d['link info']['previous']:
                        d['link info']['previous'].append(title)
                        #print(f'added {title} to {d}')
                self.inter_list[n]['link info']['previous'] = d['link info']['previous']

        self.fix_linkinfo_conflicts()

    def save_current(self):
        pass
    
    # for cleaning up unwanted titles from link info.  (will do this more cleanly later)
    def fix_linkinfo_conflicts(self):
        pure_dictionary = {d['title']:{k:v for k,v in d.items() if k != 'title'} for d in self.inter_list}
        removed = []
        for cur, d in pure_dictionary.items():
            if cur in removed:
                continue
            
            add_to_others = []
            remove_from_yourself = []
            
            for nxt in d['link info']['next']:
                if nxt not in pure_dictionary:
                    remove_from_yourself.append(nxt)
                elif cur not in pure_dictionary[nxt]['link info']['previous']:
                    add_to_others.append(nxt)
            # apply add_to_others
            for nxt in add_to_others:
                if nxt not in pure_dictionary:
                    continue
                pure_dictionary[nxt]['link info']['previous'].append(cur)
            
            for prev in d['link info']['previous']:
                if cur not in pure_dictionary[prev]['link info']['next']:
                    remove_from_yourself.append(prev)
                    removed.append(prev)
            # apply remove_from_yourself
            pure_dictionary[cur]['link info']['previous'] = [t for t in pure_dictionary[cur]['link info']['previous'] if t not in remove_from_yourself]

        self.inter_list = []
        for title, rest in pure_dictionary.items():
            newd = {'title':title}
            for k, v in rest.items():
                newd[k] = v
            self.inter_list.append(copy.deepcopy(newd))

    def change_tags(self, title, new_tags):
        for n, d in enumerate(self.inter_list):
            if d['title'] == title:
                self.inter_list[n]['tags'] = new_tags
                break

    def resolve_conflict(self, existing, new):
        # update title, by changing self.inter_list and letting the changes propagate to other places
        if existing['title'] != new['title']:
            self.change_title(existing['title'], new['title'])

        # change ['tags'] in inter_list[n]
        #print(f'existing: {existing["tags"]}, new: {new["tags"]}')
        if existing['tags'] != new['tags']:
            self.change_tags(new['title'], new['tags'])

        # change ['text'] and ['link info']['next'] in inter_list[n]
        if existing['text'] != new['text']:
            self.change_text(new['title'], new['text'])
            window.instantiate_network(self.inter_list, window.styleinfo)
        
        if self.autobackup:
            self.backup_tw()

    def check_title(self, title):
        for d in self.inter_list:
            if d['title'] == title:
                return True
        return False
    
    def wanna_change_to(self, title, source='not given'):
        '''
when some other object or function wants to change the passage that is currently displayed, it calls this function, and then
    this function does all the required logic.

steps:
    - compare: existing vs displayed
    - resolve conflict
    - update: self.current_passage (and displayed link info?)
'''
        if 1:
            # get current passage
            if self.current_passage == '':
                existing = None
            else:
                existing = self.get_passage(self.current_passage)

            # get display contents
            new_contents = {
                'title':display.title.get(),
                'tags':display.tags.get(),
                'text':display.text.get(1.0, 'end')[:-1]}
            if new_contents['tags'] == '':
                new_contents['tags'] = []
            else:
                new_contents['tags'] = new_contents['tags'].split(', ')

            # check conflict  *unless exiting == None
            if existing != None:
                for k,v in new_contents.items():
                    equal = v==existing[k]
                    if not equal:
                        # if any value is not the same between new and existing, it will resolve_conflicts and break the loop
                        self.resolve_conflict(existing, new_contents)
                        text_create(self.all_info[self.current_tab]['twee_path'], self.make_tw(self.inter_list))
                        break

            display.show_passage(title) # change display
            self.current_passage = title # change current passage

            window.network.highlight_node(title)

            self.all_info[self.current_tab]['inter_list'] = self.inter_list

    def get_passage(self, title):
##        print('/')
##        print('manager.get_passage called, title is', title)
        n = next((item for item in self.all_info[self.current_tab]['inter_list'] if item["title"] == title), None)
##        make_json(self.inter_list, 'self inter_list.json')
##        print(f'return is {n}')
##        print('/')
        return n        

    # list(inter_list) -> str
    def make_tw(self, inter_list):
        return make_tw(inter_list)

    # str(tw) -> list(inter_list)
    def interpret_tw(self, string):
        return interpret_tw(string)

    def save_tw(self):
        string = self.make_tw(manager.inter_list)
        text_create('story/twee.tw', string)

    def backup_tw(self):
        if 'backups' not in os.listdir(os.getcwd()):
            pass
            #os.mkdir('backups')

        string = self.make_tw(self.inter_list)
        timestamp = str(time.time()).partition('.')[0]
        #text_create(f'backups/{timestamp}.tw', string)

    def compile_tw(self, html_name='story.html', safe=True):
        self.wanna_change_to(self.current_passage) # to make it store the current contents
        if safe: # always use protection.
            self.backup_tw()
            self.save_tw()

        string = make_tw(self.inter_list)
        has_storydata = False
        for d in self.inter_list:
            if d['title'] == 'StoryData':
                has_storydata = True
                break
        if not has_storydata:
            ifid = str(uuid.uuid4())
            story_format = 'Harlowe'
            format_version = '3.0.0'
            string += '\n'.join(['',
                                 '::StoryData',
                                 '{',
                                 f'\t"ifid": "{ifid}",',
                                 f'\t"format": "{story_format}",',
                                 f'\t"format-version": "{format_version}"',
                                 '}'])
        text_create('story/twee.tw', string)

        command = f'tweego -o {html_name} story'
        os.system(command)

    # old title, new title --> title gets updated everywhere
    def change_title(self, old, new):
        '''
Manager method.
changes title from old to new by:
    - update self.inter_list
    - update styleinfo.json
    - titles_sv.set(new_titles)
    - call window.instantiate_network(self.inter_list, styleinfo)
'''
        string = self.make_tw(self.inter_list)

        string = string.replace(f'->{old}]]', f'->{new}]]')

        if f'::{old}\n' in string:
            string = string.replace(f'::{old}\n', f'::{new}\n')
        elif f'::{old} [' in string:
            string = string.replace(f'::{old} [', f'::{new} [')
        else:
            exit('::{old}\\n not in string, and ::old{old} [ not in string.')

        def update_styleinfo(old, new):
            outdated = window.styleinfo
            updated = {}
            for k, v in outdated.items():
                if k == old:
                    k = new
                updated[k] = v
            return updated
        
        styleinfo = update_styleinfo(old, new)

        make_json(styleinfo, self.all_info[self.current_tab]['styleinfo_path'])
        text_create(f'{self.current_tab}.tw', string)
        self.inter_list = self.interpret_tw(string)
        self.fix_linkinfo_conflicts()
        titles_sv.set([d['title'] for d in self.inter_list])

        window.instantiate_network(self.inter_list, styleinfo)

    def change_tab(self, new_tab):
        # set self.inter_list, set self.current_tab, instantiate network, set titles for the listbox
        
        self.current_tab = new_tab
        d = self.all_info[new_tab]
        self.inter_list = d['inter_list']

        defaults = {'node':'grey',
                    'segment':'grey',
                    'text':'yellow',
                    'pos':(50,50),
                    'size':30}

        if '___' in new_tab:
            exists = True
        else:
            if new_tab in os.listdir():
                exists = True
            else:
                exists = True

        # dealing with styleinfo            
        if exists:
            styleinfo = open_json(self.all_info[self.current_tab]['styleinfo_path'])
        else:
            styleinfo = {d['title']:defaults for d in self.inter_list}
            make_json(styleinfo, self.all_info[self.current_tab]['styleinfo_path'])
        # iterate over titles and fill in defaults as necessary
        all_titles = [d['title'] for d in self.inter_list]
        for title in all_titles:
            if title in styleinfo:
                for k,v in defaults.items():
                    if k in styleinfo[title]:
                        continue
                    else:
                        styleinfo[title][k] = v
            else:
                styleinfo[title] = copy.deepcopy(defaults)
                styleinfo[title]['pos'] = (random.choice(range(50,500)), random.choice(range(50,500)))

        make_json(styleinfo, self.all_info[self.current_tab]['styleinfo_path'])
        self.fix_linkinfo_conflicts()
        titles_sv.set([d['title'] for d in self.inter_list])

        window.instantiate_network(self.inter_list, styleinfo)

        self.wanna_change_to(self.inter_list[0]['title'])

        helper_window.title(self.current_tab + ' -- diagram')
        root.title(self.current_tab + ' -- text')

    def remove_title(self, to_remove):
        remember_current = display.current_passage  # to deal with listbox selection weirdness when you add/delete an item
        inter_list = []
        for d in self.inter_list:
            if d['title'] == to_remove:
                continue
            inter_list.append(d)
        self.inter_list = inter_list

        # fix all ['link info'] by excluding to_remove from each list.
        for n, d in enumerate(self.inter_list):
            new_link_info = {'next':[], 'previous':[]}
            for key in ['next', 'previous']:
                for title in d['link info'][key]:
                    if title != to_remove:
                        new_link_info[key].append(title)
            self.inter_list[n]['link info'] = copy.deepcopy(new_link_info)

        # refresh
        titles_sv.set([d['title'] for d in inter_list])
        if display.current_passage == to_remove:
            display.show_passage(inter_list[0]['title'])
        window.instantiate_network(inter_list, window.styleinfo)
        text_create(self.all_info[self.current_tab]['twee_path'], make_tw(inter_list))

        self.all_info[self.current_tab]['inter_list'] = self.inter_list

        display.show_passage(remember_current)

    delete_title = remove_title

    def add_title(self, title='untitled'):
        remember_current = display.current_passage # to deal with listbox selection weirdness when you add/delete an item
        defaults = {'begin':'+'*14,
                    'title':'',
                    'tags':[],
                    'link info':{'previous':[], 'next':[]},
                    'text':'',
                    'empty':'',
                    'end':'+'*15}
        defaults['title'] = title
        self.inter_list.insert(0, defaults)
        self.all_info[self.current_tab]['inter_list'] = self.inter_list
        
        # refresh
        titles_sv.set([d['title'] for d in self.inter_list])
        window.instantiate_network(self.inter_list, window.styleinfo)
        text_create(self.all_info[self.current_tab]['twee_path'], make_tw(self.inter_list))

        display.show_passage(remember_current)

    def change_color(self, title, color): 
        styleinfo = {}
        for k,v in window.styleinfo.items():
            if k == title:
                v['node'] = color
            styleinfo[k] = v
        window.styleinfo = styleinfo
        make_json(styleinfo, self.all_info[self.current_tab]['styleinfo_path'])
        window.instantiate_network(self.inter_list, styleinfo)

    def update_passage(self, title, new):
        print(f'updat epassage, title:{title}')
        pass
##        string = make_tw(self.inter_list)
##        
##        # do stuff
##        
##        inter_list = self.interpret_tw(string)
##        self.inter_list = inter_list

    def update_visualization(self, title, change):
        print(f'update vis, title:{title}')
        pass

def titles_listbox_selected(event):
    choice = get_listbox_choice(event.widget)
    if choice == False:
        return 0

    manager.wanna_change_to(choice, source='titles_listbox_selected(event)')

# basically a toggleable text editor
class Thingy:
    def __init__(self, content=''):
        self.exists = False
        self.current_tab = None
        self.tab_amount = 3

        self.tab_contents = {str(n):{'widget':'', 'content':''} for n in range(1, self.tab_amount+1)}
        
        self.all_windows = [root, helper_window]
        for w in self.all_windows:
            w.bind('<KeyPress>', self.on_press)

    # toggle the window
    def toggle(self, f_number):
        if self.exists: # store content, destroy widgets
            if f_number != self.current_tab:
                pass
            else:
                for n, info in self.tab_contents.items():
                    self.tab_contents[n]['content'] = info['widget'].get(1.0, 'end')[:-1]
                self.w.destroy()
                self.exists = False
                self.current_tab = None
        else: # re-create, re-insert content, re-bind on_press
            self.w = tk.Toplevel()
            self.w.config(background = 'black')

            self.nb = ttk.Notebook(self.w)

            # create tabs of text widgets
            for n, info in self.tab_contents.items():
                text_widget = tk.Text(self.nb, **textSettings)
                self.tab_contents[n]['widget'] = text_widget
                text_widget.insert(1.0, info['content'])
                
                self.nb.add(text_widget, text=f'- F{n} -')

            self.nb.pack()
            
            self.w.bind('<KeyPress>', self.on_press)
            self.nb.bind('<KeyPress>', self.on_press)
            self.exists = True
            self.current_tab = f_number
            
    def on_press(self, event):
        n = event.keysym.partition('F')[2]
        if n in self.tab_contents:
            self.toggle(n)

            if self.exists:
                tab_id = int(n)-1
                self.nb.select(tab_id)

                self.tab_contents[n]['widget'].focus_set()
                self.current_tab = n
        else:
            #print(n)
            #print(self.tab_contents.keys())
            pass


#################### #################### ####################

global_settings = {
    'text window':{
        'title':'the title. lol.',
        'window width':800,
        'window height':300,
        'window x':0,
        'window y':0,
        'textbox width':60,
        'textbox height':10
        },
    'visualization window':{
        'title':'idk',
        'window width':1300,
        'window height':500,
        'window x':0,
        'window y':100,
        'canvas width':1000,
        'canvas height':500
        }
    }
if 'settings.txt' in os.listdir():
    for section in text_read('settings.txt').split('\n\n'):
        lines = section.split('\n')
        section_title = clean_edges(lines[0].partition('#')[0])
        if section_title in global_settings:
            for line in lines[1:]:
                line = line.partition('#')[0]
                splt = line.split(':')
                if len(splt) == 2:
                    k,v = map(clean_edges,splt)
                    global_settings[section_title][k] = v

manager = Manager()

# styling
textSettings = {'bg':'black', 'fg':'green', 'height':global_settings['text window']['textbox height'], 'width':global_settings['text window']['textbox width'], 'font':('comic sans', 13), 'insertbackground':'white', 'selectbackground':'dark green', 'selectforeground':'white' }
frameSettings = {'background':'black'}
buttonSettings = {'fg':'green', 'bg':'black'}
labelSettings = {'font':('comic sans', 10), 'fg':'green', 'bg':'black', 'width':30}
entrySettings = {'bg':'black', 'fg':'green', 'insertbackground':'white', 'width':50, 'selectbackground':'dark green', 'selectforeground':'white'}

# main window
root = tk.Tk()
root.config(background = 'black')
set_word_boundaries(root)
root.title(global_settings['text window']['title'])
#setting geometry
keys = ['window width', 'window height', 'window x', 'window y']
values = list(map(lambda key:global_settings['text window'][key], keys))
root.geometry(f'{values[0]}x{values[1]}+{values[2]}+{values[3]}')

# secondary window that will have a command tab and a visualization tab
helper_window = tk.Toplevel()
helper_window.config(background = 'black')
set_word_boundaries(helper_window)
# setting geometry
keys = ['window width', 'window height', 'window x', 'window y']
values = list(map(lambda key:global_settings['visualization window'][key], keys))
helper_window.geometry(f'{values[0]}x{values[1]}+{values[2]}+{values[3]}')
# setting title
helper_window.title(global_settings['visualization window']['title'])

window = Window(helper_window)

# list(box) where you can click and go to another passage
titles_sv = tk.StringVar(root)
titles_sv.set([d['title'] for d in manager.inter_list])
titles_listbox = tk.Listbox(root, listvariable=titles_sv, exportselection=False, **labelSettings, **{'selectbackground':'dark green', 'selectforeground':'white'})
titles_listbox.bind('<<ListboxSelect>>', titles_listbox_selected)

# class for showing passages and editing them.
display = Display(root)

titles_listbox.grid(row=0, column=0)
display.frame.grid(row=0, column=1)
display.initial_layout()

root.bind('<KeyPress-F5>', lambda *a:compile_tw())

display_command_entry = tk.Entry(root, width=50)
display_command_entry.grid(column=1)
display_command_entry.bind('<Return>', window.process_command)
display_command_entry.insert(0, 'jan 24')

for name in manager.all_info:
    manager.all_info[name]['inter_list'] = manager.interpret_tw(text_read(manager.all_info[name]['twee_path']))


# makes the app require a .tw file
if manager.all_info == {}:
    exit('put a .tw file in this directory with at least the text "::blablahuehueuheueh"')

# allows you to pick which mindmap is started with. make a .txt file named "default_tutorial.txt", for example
starting_mindmap = list(manager.all_info.keys())[0]
for f in os.listdir(os.getcwd()):
    if 'default_' in f and '.txt' in f:
        candidate = f.partition('default_')[2].partition('.txt')[0]
        if candidate in manager.all_info.keys():
            starting_mindmap = candidate
            break
manager.change_tab(starting_mindmap)

thingy = Thingy()


root.mainloop()

def clear_dir(to_clear):
    # make sure it only has directories
    for file_name in os.listdir(to_clear):
        if os.path.isdir(f'{to_clear}/{file_name}'):
            pass
        else:
            exit('can only have directories inside to_clear')
            
    for inner_dir in os.listdir(to_clear):
        for file_name in os.listdir(f'{to_clear}/{inner_dir}'):
            to_del = f'{to_clear}/{inner_dir}/{file_name}'
            os.remove(to_del)
            print('    ' + f'removed {to_del}')
        os.rmdir(f'{to_clear}/{inner_dir}')
        print(f'cleared and removed {to_clear}/{inner_dir}')
        print()

path = 'testing_here'
clear_dir(path)








