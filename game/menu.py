import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.btn = tk.Button(self, text="           Играть           ", command=self.start_game)
        self.btn.pack(padx=120, pady=5)
        self.btn = tk.Button(self, text="Играть с друзьями", command=self.multiplayer)
        self.btn.pack(padx=120, pady=5)
        self.btn = tk.Button(self, text="           Выход           ", command=self.quit)
        self.btn.pack(padx=120, pady=5)


    def start_game(self):
        print("начало игры")

    def quit(self):
        app.destroy()

    def multiplayer(self):
        entry = ttk.Entry()
        entry.pack( padx=6, pady=6)

        btn = ttk.Button(text="ok", command=self.multiplayer)
        btn.pack( padx=6, pady=6)

        label = ttk.Label()
        label.pack( padx=6, pady=6)
        label["text"] = entry.get()
        print(label)


if __name__ == "__main__":
    app = App()
    app.title("Better with your friend")
    app.mainloop()