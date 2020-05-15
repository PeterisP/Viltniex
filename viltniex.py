from tkinter import *
from tkinter.scrolledtext import ScrolledText
import emulator_control

from timeit import default_timer as timer

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

        self.log = ScrolledText(self)
        self.log.grid(column=0, row=0, columnspan=3, sticky='ENWS')      
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        pogas = Frame(self)
        pogas.grid(column=1, row=1)

        quitButton = Button(pogas, text='Quit', command=self.master.destroy)
        quitButton.grid(column=0, row=0, padx=5, pady=5)
        self.initButton = Button(pogas, text='Connect', command=self.init_hc)
        self.initButton.grid(column=1, row=0, padx=5, pady=5)
        arenaButton = Button(pogas, text='Arena', command=self.run_arena)
        arenaButton.grid(column=2, row=0, padx=5, pady=5)
        invasionButton = Button(pogas, text='Invasion', command=self.run_invasion)
        invasionButton.grid(column=3, row=0, padx=5, pady=5)
        stopButton = Button(pogas, text='Stop', command=self.stop_agents)
        stopButton.grid(column=4, row=0, padx=5, pady=5)
        screenshotButton = Button(pogas, text='Screenshot', command=self.screenshot)
        screenshotButton.grid(column=5, row=0, padx=5, pady=5)
        whereamiButton = Button(pogas, text='Where am I?', command=self.whereami)
        whereamiButton.grid(column=6, row=0, padx=5, pady=5)

        self.buttons_that_need_hc = [arenaButton, invasionButton, screenshotButton, whereamiButton]

    def init_hc(self):
        try:
            self.hc = emulator_control.HC(self.master)
            emulator_control.log_error('Initialized HC')
            for button in self.buttons_that_need_hc:
                button['state'] = NORMAL
            self.initButton.configure(text = 'Reconnect')
        except Exception as e:
            emulator_control.log_error('Failed to init hc')
            emulator_control.log_error(e)
            self.hc = None
            for button in self.buttons_that_need_hc:
                button['state'] = DISABLED

    def run_arena(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.run_arena()

    def run_invasion(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.run_invasion()

    def stop_agents(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.stop_agents()

    def screenshot(self):
        assert self.hc is not None, 'HC connection not initialized'
        self.hc.screenshot()

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

