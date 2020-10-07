#-*-coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk,messagebox
from time import time
import datetime
import pickle

class Application(tk.Frame):
    def __init__(self, master=None): 
        super().__init__(master)
        self.pack()

        master.title("勤怠管理")
        master.geometry("350x177")
        
        #初期値の設定
        self.wage = 1000 #時給
        self.have_money = 0 #給与
        self.total = 0 #現在動いているタイマーの合計時間（秒）
        self.achieve = 21600 #目標時間（秒）
        self.achieve_hour = 6 #目標時間（時間表示・画面表示用）
        self.achieve_min = 0 #目標時間（分表示・画面表示用）
        self.record_list = [] #タイマーの時間の記録
        self.money_record_list = [] #給与の引き出し記録

        #save_data() でセーブしたり、load_data() でロードする際に使用
        self.data_list = [
            self.wage,
            self.have_money,
            self.record_list,
            self.money_record_list,
            self.total,
            self.achieve,
            self.achieve_hour,
            self.achieve_min,
        ]
        
        #データのロード
        self.load_data()

        #タブと内容を作成
        self.create_tabs()
        self.create_main(self.main)
        self.create_record(self.record)
        self.create_history(self.history)
        self.create_setting(self.setting)


    #================
    # タブを作成・配置
    #================
    def create_tabs(self):
        self.notebook = tk.ttk.Notebook()
        self.main = tk.Frame(self.notebook)
        self.record = tk.Frame(self.notebook)
        self.history = tk.Frame(self.notebook)
        self.setting = tk.Frame(self.notebook)

        self.notebook.add(self.main, text="メイン画面")
        self.notebook.add(self.record, text="記録")
        self.notebook.add(self.history, text="引き出し記録")
        self.notebook.add(self.setting, text="設定")

        self.notebook.pack(expand=True, fill="both")


    #==================
    # 各タブの内容の作成
    #==================

    #「メイン画面」タブ
    def create_main(self,master):
        #「作業時間」ラベルの作成
        working_hours_lb = tk.Label(master, text="作業時間")
        working_hours_lb.place(x=10, y=4)

        #画面にタイマーの時間を表示する部分の作成
        self.canvas = tk.Canvas(master,width=290,height=80)
        self.canvas.place(x=10,y=20)

        #開始ボタンの作成
        self.spbt = tk.Button(master,text="開始",command=self.start_pause_button,width=10)
        self.spbt.place(x=250, y=20)

        #完了ボタンの作成
        tk.Button(master,text="完了",command=self.stop_button_click,width=10).place(x=250, y=50)

        #リセットボタンの作成
        tk.Button(master,text="リセット",command=self.reset_button_click,width=10).place(x=250, y=80)

        #給与引き出しボタンの作成
        tk.Button(master,text="給与引き出し",command=self.withdraw,width=10).place(x=250, y=110)
        
        #時給を表示する部分の作成
        self.wage_var = tk.StringVar()
        wage_lb = tk.Label(master,textvariable=self.wage_var)
        self.wage_var.set("時給 : {0}円".format(self.wage))
        wage_lb.place(x=10, y=90)

        #給与を表示する部分の作成
        self.money_var = tk.StringVar()
        money_var_lb = tk.Label(master, textvariable=self.money_var)
        self.money_var.set("給与 : {0}円".format(int(self.have_money)))
        money_var_lb.place(x=100, y=90)

        #合計作業時間を表示する部分の作成
        self.total_var = tk.StringVar()
        total_var_lb = tk.Label(master, textvariable=self.total_var)
        self.str_total = self.strtime(self.total)
        self.total_var.set("合計作業時間  {0}".format(self.str_total))
        total_var_lb.place(x=8,y=108)

        #目標達成までの残り時間を表示する部分の作成
        self.achieve_rem_var = tk.StringVar()
        archieve_rem_var_lb = tk.Label(master, textvariable=self.achieve_rem_var)
        archieve_rem_var_lb.place(x=8, y=125)
        self.update_achieve()

        #初期値の設定
        self.stop_time = 0.0
        self.elapsed_time = 0.0 #現在測っている時間（タイマーに表示されている時間）（秒）
        self.timer_running = False #タイマーが動いていればTrue、止まっていればFalse

        master.after(50,self.update) #update() を50msごとに実行


    #「記録」タブ
    def create_record(self,master):
        #リストボックスを作成
        self.record_lb = tk.Listbox(master,width=42,height=8)
        self.record_lb.place(x=0,y=0)

        #リストボックスの内容を取得
        self.record_load()

        tk.Button(master,text="削除",command=self.del_record,width=10).place(x=260, y=0) #データを1件削除
        tk.Button(master,text="全て削除",command=self.del_all_records,width=10).place(x=260, y=30) #データを全件削除

    #「引き出し記録」タブ
    def create_history(self,master):
        #リストボックスを作成
        self.money_record_lb = tk.Listbox(master,width=42,height=8)
        self.money_record_lb.place(x=0,y=0)

        #リストボックスの内容を取得
        self.money_record_load()

        tk.Button(master,text="削除",command=self.del_money_record,width=10).place(x=260, y=0) #データ1件削除
        tk.Button(master,text="全て削除",command=self.del_all_money_records,width=10).place(x=260, y=30) #データを全件削除

    #「設定」タブ
    def create_setting(self,master):
        #時給を変更するためのフィールド
        wage_lb = tk.Label(master, text="・時給")
        wage_lb.place(x=5,y=3)

        wage_value = tk.StringVar()
        wage_value.set(self.wage)

        self.wage_sp = tk.Spinbox(master,textvariable=wage_value,from_=0,to=100000000,width=8,increment=50)
        self.wage_sp.place(x=50,y=6)

        tk.Button(master,text="変更",command=self.chg_wage,width=5).place(x=120, y=2)

        #目標時間を変更するためのフィールド
        achieve_time_lb = tk.Label(master, text="・目標時間")
        achieve_time_lb.place(x=5, y=37)

        colon_lb1 = tk.Label(master, text=":")
        colon_lb1.place(x=98, y=35)

        achieve_hour = tk.StringVar()
        achieve_hour.set(self.achieve_hour)
        achieve_min = tk.StringVar()
        achieve_min.set(self.achieve_min)
        
        self.achieve_hour_sp = tk.Spinbox(master,textvariable=achieve_hour,from_=0,to=23,width=2,increment=1)
        self.achieve_hour_sp.place(x=70,y=37)
        self.achieve_min_sp = tk.Spinbox(master,textvariable=achieve_min,from_=0,to=59,width=4,increment=10)
        self.achieve_min_sp.place(x=110,y=37)

        tk.Button(master,text="変更",command=self.chg_achieve,width=5).place(x=160,y=32)

        #合計作業時間を手動で変更するためのフィールド
        chg_total_lb = tk.Label(master, text="・合計作業時間の変更")
        chg_total_lb.place(x=5, y=65)

        self.total_hour_chg_sp = tk.Spinbox(master,from_=0,to=1000,width=2,increment=1)
        self.total_hour_chg_sp.place(x=130,y=65)
        self.total_min_chg_sp = tk.Spinbox(master,from_=0,to=1000,width=4,increment=1)
        self.total_min_chg_sp.place(x=170,y=65)

        colon_lb2 = tk.Label(master, text=":")
        colon_lb2.place(x=158,y=63)

        tk.Button(master,text="+",command=self.add_total_click,width=3).place(x=215,y=60)
        tk.Button(master,text="-",command=self.dif_total_click,width=3).place(x=255,y=60)

        #給与を手動で変更するためのフィールド
        chg_wage_lb = tk.Label(master, text="・給与の変更")
        chg_wage_lb.place(x=5, y=95)

        self.have_money_chg_sp = tk.Spinbox(master,from_=0, to=10000, width=8, increment=50)
        self.have_money_chg_sp.place(x=85, y=95)

        tk.Button(master,text="+",command=self.add_have_money_click,width=3).place(x=155,y=90)
        tk.Button(master,text="-",command=self.dif_have_money_click,width=3).place(x=195,y=90)

        #合計作業時間のリセット
        self.total_var_setting = tk.StringVar()
        total_var_lb = tk.Label(master, textvariable=self.total_var_setting)
        self.str_total = self.strtime(self.total)
        self.total_var_setting.set("・合計作業時間  {0}".format(self.str_total))
        total_var_lb.place(x=5,y=124)

        tk.Button(master,text="リセット",command=self.reset_total_click,width=5).place(x=135, y=122)


    #===========================
    #「メイン画面」タブ用メソッド
    #===========================

    #開始 / 一時停止ボタンが押された時
    def start_pause_button(self):
        if self.timer_running:
            self.pause_timer()
            self.spbt["text"] = "再開"
        else:
            #「再開」ではなく「開始」を押す時、その時刻を取得
            if not self.elapsed_time:
                self.dt_start = datetime.datetime.now() #タイマー開始時刻を取得（記録として保存するため）

            self.start_timer()
            self.spbt["text"] = "一時停止"


    #タイマー開始
    def start_timer(self):
        if not self.timer_running:
            self.start_time = time() - self.elapsed_time
            self.timer_running = True


    #タイマー一時停止
    def pause_timer(self):
        if self.timer_running:
            self.stop_time = time() - self.start_time #一時停止ボタンを押したときのタイマーの表示時間
            self.timer_running = False


    #タイマーの時間を更新
    def update(self):
        self.canvas.delete("time")
        if self.timer_running:
            self.elapsed_time = time() - self.start_time
            elapsed_time_str = self.strtime(self.elapsed_time)
            self.canvas.create_text(200,40,text=elapsed_time_str,font=("Helvetica",40,"bold"),fill="black",tag="time",anchor="e")
        else:
            stop_time_str = self.strtime(self.stop_time)
            self.canvas.create_text(200,40,text=stop_time_str,font=("Helvetica",40,"bold"),fill="black",tag="time",anchor="e")
        
        self.master.after(50,self.update)


    #完了ボタンが押された時
    def stop_button_click(self):
        if self.elapsed_time:
            msgbox = messagebox.askyesno("確認","記録を完了してもよろしいですか？")
            if msgbox:
                self.start_time = time()
                self.add_wage()
                self.add_total()
                self.update_achieve()
                self.dt_stop = datetime.datetime.now()
                self.new_record()
                self.spbt["text"] = "開始"
                self.stop_time = 0.0
                self.elapsed_time = 0.0
                self.timer_running = False
                self.save_data()


    #前回の記録を追加
    def new_record(self):
        start_date = self.dt_start.strftime("%m/%d")
        start_time = self.dt_start.strftime("%H:%M")
        stop_time = self.dt_stop.strftime("%H:%M")
        elapsed_time = self.strtime(self.elapsed_time)
        str_record = "{0}    {1}～{2}    {3}".format(start_date,start_time,stop_time,elapsed_time)
        self.record_lb.insert(0,str_record)
        self.record_list.insert(0,str_record)


    #タイマー停止時に給与を追加
    def add_wage(self):
        self.have_money += int(self.wage) * self.elapsed_time / 3600
        self.money_var.set("給与 : {0}円".format(int(self.have_money)))


    #リセットボタンが押された時
    def reset_button_click(self):
        if self.elapsed_time:
            msgbox = messagebox.askyesno("確認","ストップウォッチをリセットしますか？")
            if msgbox:
                self.spbt["text"] = "開始"
                self.resettimer()


    #タイマーリセット
    def resettimer(self):
        self.start_time = time()
        self.stop_time = 0.0
        self.elapsed_time = 0.0
        self.timer_running = False


    #給与引き出しボタンが押された時
    def withdraw(self):
        if self.have_money:
            msgbox = messagebox.askyesno("確認","給与を引き出しますか？")
            if msgbox:
                self.dt_wd = datetime.datetime.now()
                self.add_money_record()
                self.have_money = 0
                self.money_var.set("給与 : {0}円".format(int(self.have_money)))
                self.save_data()


    #前回の給与引き出し記録を追加
    def add_money_record(self):
        wd_time = self.dt_wd.strftime("%m/%d  %H:%M")
        record_money = int(self.have_money)
        str_money_record = "{0}    -{1}円".format(wd_time,record_money)
        self.money_record_lb.insert(0,str_money_record)
        self.money_record_list.insert(0,str_money_record)


    #=====================
    #「記録」タブ用メソッド
    #=====================

    #記録の削除（1件）
    def del_record(self):
        index = self.record_lb.curselection()
        if index:
            msgbox = messagebox.askyesno("確認","選択中の記録を削除してもよろしいですか？")
            if msgbox:
                self.record_lb.delete(int(index[0]))
                self.record_list.pop(int(index[0]))
                self.record_lb.select_set(int(index[0])-1)
                self.save_data()
                

    #記録の削除（全件）
    def del_all_records(self):
        print(self.record_lb.size())
        if self.record_lb.size() != 0:
            msgbox = messagebox.askyesno("確認","全ての記録を削除してもよろしいですか？")
            if msgbox:
                self.record_lb.delete(0,tk.END)
                self.record_list.clear()
                self.save_data()


    #self.record_lbのロード
    """
    self.record_lb が空リストの場合、self.record_list の要素を self.record_lb にコピーする
    """
    def record_load(self):
        if self.record_lb.size() == 0:
            for i in self.record_list:
                self.record_lb.insert(tk.END,i)


    #=============================
    # 「引き出し記録」タブ用メソッド
    #=============================

    #引き出し記録の削除（1件）
    def del_money_record(self):
        index = self.money_record_lb.curselection()
        if index:
            msgbox = messagebox.askyesno("確認","選択中の記録を削除してもよろしいですか？")
            if msgbox:
                self.money_record_lb.delete(int(index[0]))
                self.money_record_list.pop(int(index[0]))
                self.money_record_lb.select_set(int(index[0])-1)
                self.save_data()


    #引き出し記録の削除（全件）
    def del_all_money_records(self):
         if self.money_record_lb.size() != 0:
            msgbox = messagebox.askyesno("確認","全ての記録を削除してもよろしいですか？")
            if msgbox:
                self.money_record_lb.delete(0,tk.END)
                self.money_record_list.clear()
                self.save_data()


    #self.money_record_lbのロード
    """
    self.money_record_lb が空リストの場合、self.money_record_list の要素を self.record_lb にコピーする
    """
    def money_record_load(self):
        if self.money_record_lb.size() == 0:
            for i in self.money_record_list:
                self.money_record_lb.insert(tk.END,i)


    #======================
    # 「設定」タブ用メソッド
    #======================

    #時給の変更
    def chg_wage(self):
        if self.wage_sp.get().isnumeric():
            if 0 <= int(self.wage_sp.get()) <= 100000000:
                self.wage = self.wage_sp.get()
                self.wage_var.set("時給 : {0}円".format(self.wage))
                self.save_data()
                messagebox.showinfo("変更完了", "時給を変更しました")
            
            else:
                messagebox.showinfo("エラー","時給は0から100000000までの整数値で入力して下さい")
        else:
            messagebox.showinfo("エラー","時給は0から100000000までの整数値で入力して下さい")

    #目標時間の変更
    def chg_achieve(self):
        if self.achieve_hour_sp.get().isnumeric() and self.achieve_min_sp.get().isnumeric():
            if 0 <= int(self.achieve_hour_sp.get()) <= 23 and 0 <= int(self.achieve_min_sp.get()) <= 59:
                self.achieve = int(self.achieve_hour_sp.get()) * 3600 + int(self.achieve_min_sp.get()) * 60
                self.achieve_hour = int(self.achieve_hour_sp.get())
                self.achieve_min = int(self.achieve_min_sp.get())
                self.achieve_rem = self.achieve - self.total
                self.str_achieve_rem = self.strtime(self.achieve_rem)
                self.achieve_rem_var.set("目標達成まで残り : {0}".format(self.str_achieve_rem))
                self.update_achieve()
                self.save_data()
                messagebox.showinfo("変更完了", "目標時間を変更しました")
            else:
                messagebox.showinfo("エラー", "時間は0~23、分は0~59の整数値で入力してください")
        else:
            messagebox.showinfo("エラー", "時間は0~23、分は0~59の整数値で入力してください")
    

    #合計作業時間の更新
    def add_total(self):
        self.total += self.elapsed_time
        self.str_total = self.strtime(self.total)
        self.total_var_setting.set("・合計作業時間  {0}".format(self.str_total))
        self.total_var.set("合計作業時間  {0}".format(self.str_total))


    #合計作業時間の追加ボタンが押された時
    def add_total_click(self):
        if self.total_hour_chg_sp.get().isnumeric() and self.total_min_chg_sp.get().isnumeric(): 
            chg = int(self.total_hour_chg_sp.get()) * 3600 + int(self.total_min_chg_sp.get()) * 60
            if chg != 0:
                self.new_chg_record(chg)
                self.chg_total(chg)
        else:
            messagebox.showinfo("エラー", "変更分は整数値で入力してください")


    #合計作業時間の削除ボタンが押された時
    def dif_total_click(self):
        if self.total_hour_chg_sp.get().isnumeric() and self.total_min_chg_sp.get().isnumeric(): 
            chg = -(int(self.total_hour_chg_sp.get()) * 3600 + int(self.total_min_chg_sp.get()) * 60)
            if chg != 0:
                self.new_chg_record(chg)
                self.chg_total(chg)
        else:
            messagebox.showinfo("エラー", "変更分は0以上の整数値で入力してください")


    #合計作業時間を増減する処理
    def chg_total(self, chg):
        self.total += chg
        self.str_total = self.strtime(self.total)
        self.total_var_setting.set("・合計作業時間  {0}".format(self.str_total))
        self.total_var.set("合計作業時間  {0}".format(self.str_total))
        self.update_achieve()
        self.save_data()


    #前回の記録を記録（手動で追加時）
    def new_chg_record(self, chg):
        date = datetime.datetime.now()
        add_date = date.strftime("%m/%d")
        add_time = date.strftime("%H:%M")

        if chg >= 0:
            chg_time = self.strtime(chg)
        else:
            chg_time = "-" + self.strtime(-chg)
        str_record = "{0}    {1} (手動)     {2}".format(add_date, add_time, chg_time)
        self.record_lb.insert(0,str_record)
        self.record_list.insert(0,str_record)


    #給与の追加ボタンが押された時
    def add_have_money_click(self):
        if self.have_money_chg_sp.get().isnumeric(): 
            chg = int(self.have_money_chg_sp.get())
            self.chg_have_money(chg)
        else:
            messagebox.showinfo("エラー", "変更分は整数値で入力してください")


    #給与の削除ボタンが押された時
    def dif_have_money_click(self):
        if self.have_money_chg_sp.get().isnumeric(): 
            chg = -(int(self.have_money_chg_sp.get()))
            self.chg_have_money(chg)
        else:
            messagebox.showinfo("エラー", "変更分は整数値で入力してください")


    #給与を増減する処理
    def chg_have_money(self, chg):
        self.have_money += chg
        self.money_var.set("給与 : {0}円".format(int(self.have_money)))
        self.save_data()


    #合計作業時間のリセットボタンが押された時
    def reset_total_click(self):
        if self.total:
            msgbox = messagebox.askyesno("確認","合計作業時間をリセットしますか？")
            if msgbox:
                self.total = 0
                self.update_achieve()
                self.str_total = self.strtime(self.total)
                self.total_var_setting.set("・合計作業時間  {0}".format(self.str_total))
                self.total_var.set("合計作業時間  {0}".format(self.str_total))
                self.save_data()


    #========================
    # アプリ全体で使うメソッド
    #========================

    #「メイン画面」タブの「目標達成まで残り」の時間の更新
    def update_achieve(self):
        self.achieve_rem = self.achieve - self.total
        if self.achieve_rem >= 0:
            self.str_achieve_rem = self.strtime(self.achieve_rem)
            self.achieve_rem_var.set("目標達成まで残り : {0} | {1}".format(self.str_achieve_rem, self.rem_percent(self.total, self.achieve)))
        else:
            self.achieve_rem = self.total - self.achieve
            self.str_achieve_rem = self.strtime(self.achieve_rem)
            self.achieve_rem_var.set("目標達成済み（+{0}）".format(self.str_achieve_rem))
    

    #「メイン画面」タブの目標達成までの残り%の計算と、グラフの作成
    def rem_percent(self, total, achieve):
        percent = int(total / achieve * 100)
        percent_graph = "|" * (percent // 5) + " " * (20-(percent // 5))
        return str(percent) + "% " + "[" + percent_graph + "]"


    #データの取得
    def load_data(self):
        with open("log.dat","rb") as fp:
            load_list = pickle.load(fp)
            count = 0
            for i in load_list:
                self.data_list[count] = i
                count += 1
        
        self.wage = self.data_list[0]
        self.have_money = self.data_list[1]
        self.record_list = self.data_list[2]
        self.money_record_list = self.data_list[3]
        self.total = self.data_list[4]
        self.achieve = self.data_list[5]
        self.achieve_hour = self.data_list[6]
        self.achieve_min = self.data_list[7]


    #データの保存
    def save_data(self):
        data_list = [
            self.wage,
            self.have_money,
            self.record_list,
            self.money_record_list,
            self.total,
            self.achieve,
            self.achieve_hour,
            self.achieve_min,
        ]
        with open("log.dat","wb") as fp:
            pickle.dump(data_list,fp)


    #時間をh:mm:ssの形のstr型に変換
    def strtime(self, time):
        hour = int(time / 3600)
        min = int((time / 60) % 60)
        sec =int(time % 60)

        if hour == 0:
            if min < 10:
                if sec < 10:
                    strtime = "0{min}:0{sec}".format(min=min,sec=sec)
                else:
                    strtime = "0{min}:{sec}".format(min=min,sec=sec)
            else:
                if sec < 10:
                    strtime = "{min}:0{sec}".format(min=min,sec=sec)
                else:
                    strtime = "{min}:{sec}".format(min=min,sec=sec)
        else:
            if min < 10:
                if sec < 10:
                    strtime = "{hour}:0{min}:0{sec}".format(hour=hour,min=min,sec=sec)
                else:
                    strtime = "{hour}:0{min}:{sec}".format(hour=hour,min=min,sec=sec)
            else:
                if sec < 10:
                    strtime = "{hour}:{min}:0{sec}".format(hour=hour,min=min,sec=sec)
                else:
                    strtime = "{hour}:{min}:{sec}".format(hour=hour,min=min,sec=sec)

        return strtime


def main():
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.iconbitmap('icon.ico')
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()