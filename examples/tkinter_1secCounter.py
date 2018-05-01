# a second counter using Tkinter
# tested with Python25  by  vegaseat  17aug2007
import Tkinter as tk
from itertools import count
def start_counter(label):
    counter = count(0)
    def update_func():
        label.config(text="Timer: " + str(counter.next()))
        label.after(1000, update_func)  # 1000ms
    update_func()
    
def start_counter2(label):
    counter = count(0)
    def update_func():
        label.config(text="Timer: " + str(counter.next()))
        label.after(5000, update_func)  # 5sec
    update_func()
    
root = tk.Tk()
root.title("Counting Seconds")
label = tk.Label(root, fg="red")
label2 = tk.Label(root, fg="green")
label.pack()
label2.pack()
start_counter(label)
start_counter2(label2)
button = tk.Button(root, text='Stop', width=30, command=root.destroy)
button.pack()
root.mainloop()
