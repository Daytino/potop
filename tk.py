import tkinter as tk
from tkinter import font
from datetime import datetime
from typing import Dict
from operations import Operations

class Calculator():
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("350x420")
        self.root.title("Простой калькулятор")
        self.root.configure(bg="#282828")

        self.radio_btn_frame = tk.Frame(self.root, bg="#282828")

        self.create_menu()
        self.create_radio_buttons()
        self.create_labels_buttons_entries()
        self.create_canvas()
        self.canvas.pack_forget()

        self.root.mainloop()
    
    @property
    def config(self) -> Dict:
        config = {
            "font_family": "Consolas",
            "font_size": 11,
            "font_weight": "normal"
        }

        return config
    

    def get_font(self, size: int = 11, weight: str = "normal") -> object:
        return font.Font(family=self.config["font_family"], size=size, weight=weight)

    def create_radio_buttons(self):
        self.mode_var = tk.StringVar(value="Calculator")
        
        self.calc_btn = tk.Radiobutton(self.root, text="Калькулятор", 
                                       variable=self.mode_var, value="Calculator", 
                                       font=self.get_font(), 
                                       bg="#282828", fg="#ebdbb2", 
                                       selectcolor="#3c3836", 
                                       activebackground="#504945",
                                       command=self.switch_mode)
        self.calc_btn.pack()
        self.rect_btn = tk.Radiobutton(self.root, text="Прямоугольник", 
                                       variable=self.mode_var, value="Rectangle", 
                                       font=self.get_font(), 
                                       bg="#282828", fg="#ebdbb2", 
                                       selectcolor="#3c3836", 
                                       activebackground="#504945",
                                       command=self.switch_mode)
        self.rect_btn.pack()
    
    def switch_mode(self):
        if self.mode_var.get() == "Calculator":
            self.root.geometry("350x420")
            self.canvas.pack_forget()
            self.label1.config(text="Значение 1")
            self.label2.config(text="Значение 2")
            self.btn1.config(text="Сложение", command=self.add)
            self.btn2.config(text="Вычитание", command=self.subtract)
            self.btn3.config(text="Умножение", command=self.multiply)
            self.btn4.config(text="Деление", command=self.divide)
            self.btn3.pack(padx=10, pady=2)
            self.btn4.pack(padx=10, pady=2)
        else:
            self.root.geometry("350x560")
            self.canvas.pack()
            self.label1.config(text="Длина")
            self.label2.config(text="Ширина")
            self.btn1.config(text="Периметр", command=self.perimeter)
            self.btn2.config(text="Площадь", command=self.area)
            self.btn3.pack_forget()
            self.btn4.pack_forget()
            self.btn1.pack(padx=10, pady=2)
            self.btn2.pack(padx=10, pady=2)

    def create_menu(self):
        self.menu_frame = tk.Frame(self.root, border=1, borderwidth=2, bg="#282828")

        self.file_btn = tk.Menubutton(self.menu_frame, text="Меню", 
                                      bg="#3c3836", fg="#ebdbb2", 
                                      activebackground="#504945", 
                                      activeforeground="#fb4934")
        self.file_btn.menu = tk.Menu(self.file_btn, bg="#3c3836", fg="#ebdbb2", 
                                     activebackground="#504945", 
                                     activeforeground="#fb4934")
        self.file_btn["menu"] = self.file_btn.menu
        self.file_btn.menu.add_checkbutton(label="Выход",
                                           variable=tk.IntVar(),
                                           command=self.exit)
        self.file_btn.menu.delete(0)
        self.file_btn.pack(side=tk.LEFT, padx=2)

        self.operations_btn = tk.Menubutton(self.menu_frame, 
                                            text="Операции", 
                                            bg="#3c3836", fg="#ebdbb2", 
                                            activebackground="#504945", 
                                            activeforeground="#fb4934")
        self.operations_btn.menu = tk.Menu(self.operations_btn, 
                                           bg="#3c3836", fg="#ebdbb2", 
                                           activebackground="#504945", 
                                           activeforeground="#fb4934")
        self.operations_btn["menu"] = self.operations_btn.menu

        self.operations_btn.menu.add_command(label="Сложение", command=self.add)
        self.operations_btn.menu.add_command(label="Вычитание", command=self.subtract)
        self.operations_btn.menu.add_command(label="Умножение", command=self.multiply)
        self.operations_btn.menu.add_command(label="Деление", command=self.divide)
        self.operations_btn.menu.add_separator()
        self.operations_btn.menu.add_command(label="Периметр", command=self.perimeter)
        self.operations_btn.menu.add_command(label="Площадь", command=self.area)

        self.operations_btn.pack(side=tk.LEFT, padx=2)

        self.help_btn = tk.Menubutton(self.menu_frame, text="Справка", 
                                      bg="#3c3836", fg="#ebdbb2", 
                                      activebackground="#504945", 
                                      activeforeground="#fb4934")
        self.help_btn.menu = tk.Menu(self.help_btn, 
                                     bg="#3c3836", fg="#ebdbb2", 
                                     activebackground="#504945", 
                                     activeforeground="#fb4934")
        self.help_btn["menu"] = self.help_btn.menu

        self.help_btn.menu.add_checkbutton(label="О программе",
                                                 variable=tk.IntVar(),
                                                 command=self.get_help)
        
        self.help_btn.pack(side=tk.LEFT, padx=2)

        self.menu_frame.pack(anchor="nw")

    def swap_values(self):
        value1 = self.entry1.get()
        value2 = self.entry2.get()
        self.entry1.delete(0, tk.END)
        self.entry1.insert(0, value2)
        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, value1)
        self.create_rect()

    def add(self):
        answer = Operations().add(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)
    
    def subtract(self):
        answer = Operations().subtract(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)

    def multiply(self):
        answer = Operations().multiply(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)
    
    def divide(self):
        answer = Operations().divide(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)
    
    def create_rect(self):
        self.canvas.delete("all")
        h, w = float(self.entry1.get()), float(self.entry2.get())
        self.canvas.create_rectangle(0, 0, h, w,
                                     fill="#d79921", outline="#b57614")
    
    def perimeter(self):
        answer = Operations().rectangle_perimeter(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)
        self.create_rect()
    
    def area(self):
        answer = Operations().rectangle_area(self.entry1.get(), self.entry2.get())
        if answer == ValueError: answer = "Вы ввели неверные данные!"
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, answer)
        self.create_rect()
    
    def copy_result(self):
        value = self.result_entry.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
    
    def clear_entries(self):
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.result_entry.delete(0, tk.END)

    def change_operations_btns_state(self, state):
        for btn in self.operations_btn_frame.slaves():
            btn.configure(state=state)

    def on_change(self, text_var, entry):
        text = text_var.get()
        try:
            float(text)
            entry.config(fg="#ebdbb2")
            self.change_operations_btns_state(tk.NORMAL)
        except ValueError:
            entry.config(fg="#fb4934")
            self.change_operations_btns_state(tk.DISABLED)
        else:
            if self.entry1.get() == "" or self.entry2.get() == "":
                self.change_operations_btns_state(tk.DISABLED)
            else:
                try:
                    float(self.entry1.get()), float(self.entry2.get())
                    if self.mode_var.get() == "Rectangle":
                        if float(self.entry1.get()) <= 0 or float(self.entry2.get()) <= 0:
                            self.change_operations_btns_state(tk.DISABLED)
                        else:
                            self.change_operations_btns_state(tk.NORMAL)
                    else:
                        self.change_operations_btns_state(tk.NORMAL)
                except ValueError:
                    self.change_operations_btns_state(tk.DISABLED)
                else:
                    self.change_operations_btns_state(tk.NORMAL)

    def create_labels_buttons_entries(self):
        self.frame = tk.Frame(self.root, bg="#282828", bd=2)
        self.frame.grid_rowconfigure(1, weight=2)

        self.label1 = tk.Label(self.frame, text="Значение 1", 
                               font=self.get_font(), 
                               bg="#282828", fg="#ebdbb2")
        self.label1.grid(row=0, column=0)

        self.label2 = tk.Label(self.frame, text="Значение 2", 
                               font=self.get_font(), 
                               bg="#282828", fg="#ebdbb2")
        self.label2.grid(row=0, column=2)

        text_var1 = tk.StringVar()
        self.entry1 = tk.Entry(self.frame, textvariable=text_var1, 
                               font=self.get_font(), 
                               justify="center",
                               bg="#3c3836", fg="#ebdbb2", 
                               insertbackground="#fb4934", 
                               width=13)
        self.entry1.grid(row=1, column=0, padx=12)
        text_var1.trace("w", lambda *args: self.on_change(text_var1, self.entry1))

        self.swap_btn = tk.Button(self.frame, text="<=>", 
                                  command=self.swap_values,
                                  font=self.get_font(10), 
                                  bg="#3c3836", fg="#fabd2f", 
                                  activebackground="#504945", 
                                  activeforeground="#fb4934", 
                                width=5)
        self.swap_btn.grid(row=1, column=1, padx=5)

        text_var2 = tk.StringVar()
        self.entry2 = tk.Entry(self.frame, textvariable=text_var2, 
                               font=self.get_font(), 
                               justify="center",
                               bg="#3c3836", fg="#ebdbb2", 
                               insertbackground="#fb4934", 
                               width=13)
        self.entry2.grid(row=1, column=2, padx=12)
        text_var2.trace("w", lambda *args: self.on_change(text_var2, self.entry2))

        self.frame.pack(pady=10, padx=10, fill="x")

        #--Buttons--

        self.operations_btn_frame = tk.Frame(self.root, width=200, bg="#282828")
        
        self.btn1 = tk.Button(self.operations_btn_frame, text="Сложение", command=self.add,
                              state=tk.DISABLED, font=self.get_font(), 
                              bg="#3c3836", fg="#ebdbb2", activebackground="#504945", 
                              activeforeground="#fb4934")
        self.btn1.pack(padx=10, pady=2)
        
        self.btn2 = tk.Button(self.operations_btn_frame, text="Вычитание", command=self.subtract,
                              state=tk.DISABLED, font=self.get_font(), 
                              bg="#3c3836", fg="#ebdbb2", activebackground="#504945", 
                              activeforeground="#fb4934")
        self.btn2.pack(padx=10, pady=2)
        
        self.btn3 = tk.Button(self.operations_btn_frame, text="Умножение", command=self.multiply,
                              state=tk.DISABLED, font=self.get_font(), 
                              bg="#3c3836", fg="#ebdbb2", activebackground="#504945", 
                              activeforeground="#fb4934")
        self.btn3.pack(padx=10, pady=2)
        
        self.btn4 = tk.Button(self.operations_btn_frame, text="Деление", command=self.divide,
                              state=tk.DISABLED, font=self.get_font(), 
                              bg="#3c3836", fg="#ebdbb2", activebackground="#504945", 
                              activeforeground="#fb4934")
        self.btn4.pack(padx=10, pady=2)

        self.operations_btn_frame.pack(anchor="center", pady=5)

        #--Result--
        self.result_label = tk.Label(self.root, text="Итоговый результат:", 
                                     font=self.get_font(),
                                     bg="#282828", fg="#ebdbb2")
        self.result_label.pack()

        self.result_entry = tk.Entry(self.root, justify="center")
        self.result_entry.config(state="normal", 
                                 font=self.get_font(), 
                                 bg="#3c3836", fg="#ebdbb2", 
                                 insertbackground="#fb4934", 
                                 width=26)
        self.result_entry.pack()

        #--Copy & Clear--
        copy_clear_frame = tk.Frame(self.root, bg="#282828")
        
        self.copy_btn = tk.Button(copy_clear_frame, 
                            text="Скопировать",
                            command=self.copy_result,
                            font=self.get_font(), 
                            bg="#3c3836", fg="#ebdbb2",
                            activebackground="#504945", 
                            activeforeground="#fb4934")
        self.copy_btn.pack(padx=5, side=tk.LEFT)
        
        self.clear_btn = tk.Button(copy_clear_frame, 
                            text="Очистить всё",
                            command=self.clear_entries,
                            font=self.get_font(), 
                            bg="#3c3836", fg="#ebdbb2",
                            activebackground="#504945", 
                            activeforeground="#fb4934")
        self.clear_btn.pack(padx=5, side=tk.LEFT)
        copy_clear_frame.pack(pady=10)
    
    def create_canvas(self):
        self.canvas_width, self.canvas_height = 350, 200
        self.canvas = tk.Canvas(bg="#282828", width=self.canvas_width, height=self.canvas_height, 
                                borderwidth=10, 
                                highlightthickness=2, highlightbackground="#b57614")
        self.canvas.pack(anchor=tk.CENTER, expand=0)
        

    def get_help(self):
        self.dialogue = tk.Toplevel(self.root)
        self.dialogue.geometry("450x60")
        self.dialogue.configure(bg="#282828")
        self.label = tk.Label(self.dialogue, 
                              text=f"Простой калькулятор /// Асанов Даут Владимирович \n {str(datetime.today().date()).replace('-', '.')} /// GNU GPL 3.0", 
                              font=self.get_font(), 
                              bg="#282828", fg="#ebdbb2")
        self.label.pack()

    def exit(self):
        self.root.destroy()


Calculator()