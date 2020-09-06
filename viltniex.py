import cv2
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import emulator_control
import logging

from timeit import default_timer as timer

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)               
        self.master = master
        self.init_window()
        self.init_hc()

    def init_window(self):
        self.master.title('Viltniex')
        self.master.geometry('500x500')
        self.pack(fill=BOTH, expand=1)

        log = ScrolledText(self)
        log.grid(column=0, row=0, columnspan=3, sticky='ENWS')      
        text_handler = TextHandler(log)
        logging.basicConfig(level=logging.INFO, format='%(message)s')        
        self.logger = logging.getLogger()        
        self.logger.addHandler(text_handler)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        parametri = Frame(self)
        parametri.grid(column=0, row=1)
        self.power = StringVar()
        numbers = (self.master.register(self.validate_numbers),  '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        power_box = Entry(parametri, validate='key', validatecommand = numbers, textvariable=self.power)
        power_box.grid(column=1, row=0)
        powerlabel = Label(parametri, text='Arena power')
        powerlabel.grid(column=0, row=0)
        self.tickets = IntVar()
        ticket_box = Checkbutton(parametri, text='Use tickets', variable=self.tickets)
        ticket_box.grid(column=0, row=1)
        self.high_level = IntVar()
        level_box = Checkbutton(parametri, text='10-man arena', variable=self.high_level)
        level_box.grid(column=0, row=2)        

        self.tickets.set(1)
        self.high_level.set(1)
        self.power.set('10000000')
        if True:
            self.tickets.set(0)
            self.high_level.set(0)
            self.power.set('580000')

        buttons = Frame(self)
        buttons.grid(column=1, row=1)

        quitButton = Button(buttons, text='Quit', command=self.master.destroy)
        quitButton.grid(column=0, row=0, padx=5, pady=5)
        self.initButton = Button(buttons, text='Connect', command=self.init_hc)
        self.initButton.grid(column=1, row=0, padx=5, pady=5)
        screenshotButton = Button(buttons, text='Screenshot', command=self.screenshot)
        screenshotButton.grid(column=2, row=0, padx=5, pady=5)
        fullshotButton = Button(buttons, text='Fullshot', command=self.fullshot)
        fullshotButton.grid(column=3, row=0, padx=5, pady=5)
        whereamiButton = Button(buttons, text='Where am I?', command=self.whereami)
        whereamiButton.grid(column=0, row=1, padx=5, pady=5)
        arenaButton = Button(buttons, text='Arena', command=self.run_arena)
        arenaButton.grid(column=1, row=1, padx=5, pady=5)
        invasionButton = Button(buttons, text='Invasion', command=self.run_invasion)
        invasionButton.grid(column=2, row=1, padx=5, pady=5)
        stopButton = Button(buttons, text='Stop', command=self.stop_agents)
        stopButton.grid(column=3, row=1, padx=5, pady=5)

        self.buttons_that_need_hc = [arenaButton, invasionButton, screenshotButton, fullshotButton, whereamiButton]

    # Validation from https://stackoverflow.com/a/8960839
    def validate_numbers(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    def init_hc(self):
        try:
            self.hc = emulator_control.HC(self.master, self.logger)            
            self.logger.info('Initialized HC')
            for button in self.buttons_that_need_hc:
                button['state'] = NORMAL
            self.initButton.configure(text = 'Reconnect')
        except Exception as e:
            self.logger.error('Failed to init hc')
            self.logger.error(e)
            self.hc = None
            for button in self.buttons_that_need_hc:
                button['state'] = DISABLED

    def run_arena(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.run_arena(int(self.power.get()), bool(self.tickets.get()), bool(self.high_level.get()))

    def run_invasion(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.run_invasion()

    def stop_agents(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.stop_agents()

    def screenshot(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.screenshot()

    def fullshot(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.screenshot(full=True)

    def whereami(self, benchmark=False):
        assert self.hc is not None, 'HC connection not initialized'
        page, _ = self.hc.pages.active_page()

        if benchmark:        
            start = timer()
            for _ in range(10):
                page, _ = self.hc.pages.active_page()
            end = timer()
            print('Timing active_page(): ', end - start)

        if page:
            print(page)

if __name__ == '__main__':
    root = Tk()
    app = Window(root)
    root.mainloop()

