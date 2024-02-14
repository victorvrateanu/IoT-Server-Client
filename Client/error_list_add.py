
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import email_smtp
from main import bazadateUser

# pregatim cursorul SQL pentru lucrul cu baza de date
try:
    bazadateUser.connect()
    cursor = bazadateUser.cursor()
except:
    print("Nu s-a putut conecta la baza de date")

# comanda sql de inserare in baza de date erori
sql = "INSERT INTO `erori` (`ID`, `Detalii`, `Data`) VALUES (NULL, %s,CURRENT_DATE())"

if float(temperatura) > 70:
    val = ("TEMPERATURA RIDICATA", )
    cursor.execute(sql, val)  # executa comanda
    bazadateUser.commit()
    messagebox.showinfo(self ,"Temperatura ridicata !!!")
    email_smtp.trimite_email("TEMPERATURA RIDICATA")  # trimite email cu eroarea pentru temperatura
if float(umiditate) > 70:
    val = ("UMIDITATE CRESCUTA", )
    cursor.execute(sql, val)
    bazadateUser.commit()  # executa comanda
    messagebox.showinfo(self ,"Umiditate crescuta !!!")
    email_smtp.trimite_email("UMIDITATE CRESCUTA")  # trimite email cu eroarea pentru umiditate

if float(ultima_accesare_timp) < 20:
    try:
        sql = "UPDATE timp SET UltimaAccesare = %s WHERE ID = 1"
        val = (datetime.datetime.now(),)
        cursor.execute(sql ,val)
        bazadateUser.commit()
        email_smtp.trimite_email("Camera de servare a fost accesata")
    except Exception as e:
        print(e)