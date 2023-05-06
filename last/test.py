# from tkinter import *
#
#
# def clicked():
#     res = "Привет {}".format(txt.get())
#     lbl.configure(text=res)
#     txt.delete(0, END)
#
#
# window = Tk()
# window.title("Добро пожаловать в приложение PythonRu")
# window.geometry('400x250')
# lbl = Label(window, text="Привет")
# lbl.grid(column=0, row=0)
# txt = Entry(window, width=10)
# txt.grid(column=1, row=0)
# btn = Button(window, text="Клик!", command=clicked)
# btn.grid(column=2, row=0)
# window.mainloop()


from tkinter import *

window = Tk()

input_user = StringVar()
input_field = Entry(window, text=input_user)
input_field.pack(side=BOTTOM, fill=X)

def enter_pressed(event):
    input_get = input_field.get()
    print(input_get)
    label = Label(frame, text=input_get)
    input_user.set('')
    label.pack()
    return "break"

frame = Frame(window, width=300, height=300)
frame.pack_propagate(False) # prevent frame to resize to the labels size
input_field.bind("<Return>", enter_pressed)
frame.pack()

window.mainloop()