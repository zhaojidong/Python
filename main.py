import tkinter as Tk
import tkinter.messagebox as mbox
import Function
import DoExcel

class MainUI(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.grid(row=1,column=3)  # the location of window
        self.createWidgets()

    def createWidgets(self):
        self.firstLabel = Tk.Label(self, text="")
        self.firstLabel.grid()
        self.clickButton = Tk.Button(self, text="点一下瞧瞧？", command=self.answer,width=12,height=2,font=('Helvetice','10'))
        self.clickButton.grid(row=1,column=1)
        self.clickButton1 = Tk.Button(self, text="Function_1", command=self.function_1,width=12,height=2,font=('Helvetice','10'))
        self.clickButton1.grid(row=1,column=2)

    def answer(self):
        print('你好 海图')
        mbox.showinfo("海图微", '''海图微电子专注于做国际一流的CMOS芯片''')

    def function_1(self):
        print('Hello word')
        mbox.showinfo("测试组", '''Ansel''')
        Function.add(100,200)
        DoExcel.write_excel()

app = MainUI()
#app.iconbitmap('D:\PythonProject\Lab1\HaiTuICO.ico')
app.master.title('海图微')
app.master.geometry('400x200')   # the size of window
app.mainloop()
