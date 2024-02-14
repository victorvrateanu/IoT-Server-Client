import socket
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from threading import *
import mysql.connector
import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import email_smtp
import efect_butoane

LARGE_FONT = ("Verdana", 12)
ultima_temp = 0
ultima_umid = 0

# conector la baza de date MySQL

try:
    bazadateUser = mysql.connector.connect(
        host="192.168.217.75",  # ip-ul raspberry pi
        port=3306,  # portul de la phpmyadmin
        user="myuser",
        password="admin",
        database="bazadate1"
    )
except:
    print("conexiunea la baza de date nu a fost realizata")
finally:
    print("conexiune reusita la baza de date")


class Pagina(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        pagina = tk.Frame(self)

        pagina.pack(side="top", fill="both", expand=True)  # se refera la geometry maganerul

        pagina.grid_rowconfigure(0, weight=1)
        pagina.grid_columnconfigure(0, weight=1)

        # initializam frame-ul paginii  cu un array gol
        self.frames = {}

        # iteram paginile programului
        for F in (StartPage, PaginaMonitorizare, PaginaErori):
            frame = F(pagina, self)

            self.frames[F] = frame

            # nsew se refera la pozitionarea widget-urilor din tkinter ( nord sud est vest )
            frame.grid(row=0, column=0, sticky="nsew")

        self.arata_pagina(StartPage)

    def arata_pagina(self, numar):
        frame = self.frames[numar]  # initializeaza frame-ul cu pagina dorita
        frame.tkraise()  # deschide pagina


class StartPage(tk.Frame):
    def __init__(self, parinte, controller):
        tk.Frame.__init__(self, parinte)
        imagine_logo = tk.PhotoImage(file='photo.png')
        imagine = ttk.Label(self, image=imagine_logo)
        imagine.grid(column=2, row=2, sticky="nswe", padx=10, pady=10)

        # configurare label si camp pentru username
        nutilizator = ttk.Label(self, text="Username:", font=LARGE_FONT)
        nutilizator.grid(column=0, row=3, sticky="nswe", padx=10, pady=10)

        nutilizator_camp = ttk.Entry(self, font=LARGE_FONT)
        nutilizator_camp.grid(column=1, row=3, sticky="nswe", padx=10, pady=10)

        # configurare label si camp pentru parola
        parola = ttk.Label(self, text="Parola:", font=LARGE_FONT)
        parola.grid(column=0, row=4, sticky="nswe", padx=10, pady=10)

        parola_camp = ttk.Entry(self, show="*", font=LARGE_FONT)
        parola_camp.grid(column=1, row=4, sticky="nswe", padx=10, pady=10)

        # verifica daca utilizatorul se afla in baza de date

        # butonul care duce la pagina principala dupa logare folosin expresia lambda
        buton1 = ttk.Button(self, text="Logare"
                            , command=lambda: login_btn_apasat())
        buton1.grid(row=5, column=1, padx=10, pady=10)

        def login_btn_apasat():
            try:
                cursorBazaDate = bazadateUser.cursor()  # cursorul care ne ajuta sa navigam baza de date
                cursorBazaDate.execute("SELECT * FROM user")  # se executa comanda mysql SELECT din tabelul USER
                rezultat = cursorBazaDate.fetchall()
                ok = 0
            except Exception as e:
                print(e)

            for x in rezultat:

                if nutilizator_camp.get() == x[0] and parola_camp.get() == x[1]:  # verifica daca contul se afla in baza de date
                    controller.arata_pagina(PaginaMonitorizare)
                    ok = 1
                    break
            if len(nutilizator_camp.get()) == 0 or len(parola_camp.get()) == 0:
                messagebox.showinfo("Alarma", "Introduceti usernameul sau parola")
            elif ok == 0:
                messagebox.showinfo("Alarma", "Username sau parola incorecta")


class PaginaMonitorizare(tk.Frame):
    def __init__(self, parinte, controler):
        tk.Frame.__init__(self, parinte)
        # initializare label

        self.flagthread = False

        label = ttk.Label(self, text="Monitorizare", font=LARGE_FONT)
        label.grid(row=0, column=2, sticky=tk.N, padx=10, pady=10)

        ceas = tk.Label(self, font=('times', 18, 'bold'), bg='green', fg="white")
        ceas.grid(row=0, column=2, sticky="NSNESWSE", padx=8, pady=8)

        def tick():
            time2 = time.strftime('%H:%M:%S')
            ceas.config(text=time2)
            ceas.after(200, tick)

        def ModificareFlag():
            self.flagthread = True
            time.sleep(180)
            self.flagthread = False

        tick()

        label = tk.Label(self, text="Client", font="Arial,16", bg="black", fg="White")
        label.grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")

        l_host = tk.Label(self, text="Numele hostului sau IP-ul")
        l_host.grid(row=1, column=0, padx=8, pady=8, sticky="NSNESWSE")

        e_host = tk.Entry(self)
        e_host.grid(row=1, column=1, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")
        e_host.insert(tk.END, '192.168.217.75')

        l_port = tk.Label(self, text="Introduceti portul")
        l_port.grid(row=2, column=0, padx=8, pady=8, sticky="NSNESWSE")

        e_port = tk.Entry(self)
        e_port.grid(row=2, column=1, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")
        e_port.insert(tk.END, 65432)

        message_label = tk.Label(self, text="Mesaje server", font=("Arial,12"))
        message_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="NSEW")

        scrollbar_y = tk.Scrollbar(self)
        scrollbar_y.grid(row=4, column=3, rowspan=6)

        show_1 = tk.Text(self, height=8, width=35, yscrollcommand=scrollbar_y.set,
                         bg="Grey", fg="White")
        show_1.grid(row=4, column=0, rowspan=3, columnspan=3, sticky="NSEW")

        b_connect = tk.Button(self, text="Stabileste conexiune",
                              command=lambda: monitorizare_background())
        b_connect.grid(row=14, column=0, padx=10, pady=10, sticky="nsew")

        inchidere_con = tk.Button(self, text="Inchidere conexiune",
                                  command=lambda: inchidere_conexiune())
        inchidere_con.grid(row=14, column=2, padx=10, pady=10, sticky="nsew")

        # Entry-ul e facut in asa fel in cat sa nu poata fi modificat
        e_data = tk.Entry(self)
        e_data.bind("<Button-1>", lambda e: "break")
        e_data.bind("<Key>", lambda e: "break")
        e_data.grid(row=14, column=1, padx=10, pady=10, sticky="nsew")

        # Buton care duce la tabela de erori din mysql
        erori = tk.Button(self, text="Lista avertismente si erori",
                          command=lambda: controler.arata_pagina(PaginaErori))
        erori.grid(row=15, column=1, padx=10, pady=10, sticky="nsew")

        # inlocuieste comanda cu quit
        def inchidere_conexiune():
            efect_butoane.buton_activ(b_connect)
            e_data.delete(0, tk.END)
            e_data.insert(0, "quit");  # 0 face referinta la index

        # inlocuieste comanda cu date
        def monitorizare_background():
            efect_butoane.buton_inactiv(b_connect)
            e_data.delete(0, tk.END)
            e_data.insert(0, "date")
            t1 = Thread(target=m_client)
            t1.start()

        def procesare_date(x):  # proceseaza datele prin impartirea lor prin virgula
            y1, x1, z1 = x.split(',')
            return x1, y1, z1

        def m_client():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((e_host.get(), int(e_port.get())))  # stabileste conexiunea catre server

                # securitate - encriptia datelor
                pem_public_key = client.recv(1024)  # primeste public key-ul de la server

                server_public_key = RSA.import_key(pem_public_key)  # incarca cheia publica de la server
                cipher_rsa = PKCS1_OAEP.new(server_public_key)
                # ------------------------------

                while True:
                    comanda = e_data.get()
                    comanda = comanda.encode('utf-8')  #

                    if (comanda.strip().lower() == "quit"):
                        comanda = cipher_rsa.encrypt(comanda)  # cryptarea datelor
                        client.sendall(comanda)  # trimite comanda spre server
                        break

                    comanda = cipher_rsa.encrypt(comanda)  # cryptarea datelor

                    client.sendall(comanda)  # trimite comanda spre server
                    date = client.recv(1024).decode('utf-8')  # asteapta primirea datelor de la server
                    try:
                        umiditate, temperatura, ultima_accesare_timp = procesare_date(date)
                    except:
                        continue
                    # ..................................................
                    # pregatim cursorul SQL pentru lucrul cu baza de date
                    try:
                        bazadateUser.connect()
                        cursor = bazadateUser.cursor()
                    except:
                        print("Nu s-a putut conecta la baza de date")
                        continue

                    # comanda sql de inserare in baza de date erori
                    sql = "INSERT INTO `erori` (`ID`, `Detalii`, `Data`) VALUES (NULL, %s,CURRENT_TIMESTAMP())"

                    if float(temperatura) > 70:
                        val = ("TEMPERATURA RIDICATA",)
                        try:
                            cursor.execute(sql, val)  # executa comanda
                            bazadateUser.commit()
                            messagebox.showinfo("Alarma", "Temperatura a crescut peste valorile acceptate")
                            email_smtp.trimite_email("TEMPERATURA RIDICATA")  # trimite email cu eroarea pentru temperatura
                        except Exception as e:
                            print(e)
                    if 70 < float(umiditate) < 100:
                        val = ("UMIDITATE CRESCUTA",)
                        try:
                            if not self.flagthread:
                                cursor.execute(sql, val)
                                bazadateUser.commit()  # executa comanda
                                messagebox.showinfo("Alarma", "Umiditatea a crescut peste valorile acceptate")
                                email_smtp.trimite_email("UMIDITATE CRESCUTA")  # trimite email cu eroarea pentru umiditate
                                thread1 = Thread(target=ModificareFlag)
                                thread1.start()
                        except Exception as e:
                            print(e)
                    if float(ultima_accesare_timp) < 20:
                        try:
                            sql = "UPDATE timp SET UltimaAccesare = %s WHERE ID = 1"
                            val = (datetime.datetime.now(),)
                            cursor.execute(sql, val)
                            bazadateUser.commit()
                            email_smtp.trimite_email("Camera de servere a fost accesata")
                            messagebox.showinfo("Alarma", "Camera dee servere a fost accesată.")
                        except Exception as e:
                            print(e)

                    show_1.delete(1.0, tk.END)  # clear la textul de pe pagina principala

                    # insereaza in aplicatie

                    # senzorul DHT e un senzor greu de citit care uneori da erori, asa ca in codul de mai jos se elimina
                    # erorile prin afisarea ultimelor date care au fost citite corect
                    if temperatura == 0:
                        global ultima_temp
                        temperatura = ultima_temp
                    else:
                        ultima_temp = temperatura
                    temperatura = temperatura[0:5]
                    show_1.insert(tk.END, "Temperatura {} C".format(temperatura))
                    show_1.insert(tk.END, '\n')

                    if umiditate == 0:
                        global ultima_umid
                        umiditate = ultima_umid
                    else:
                        ultima_umid = umiditate
                    umiditate = umiditate[0:5]
                    show_1.insert(tk.END, "Umiditate {} %".format(umiditate))
                    show_1.insert(tk.END, '\n')

                    try:
                        cursor.execute("SELECT * FROM timp")
                        rezultat = cursor.fetchall()
                        for x in rezultat:
                            if int(x[0]) == 1:
                                timp = x[1]
                                timp = timp[0:19]
                                show_1.insert(tk.END, "Ultima accesare in camera de servare {}".format(timp))
                    except:
                        print("Eroare la cursor.execute('SELECT * FROM timp'")
                    time.sleep(3)

                client.close()
                show_1.delete(1.0, tk.END)
                show_1.insert(1.0, "Conexiunea spre servar a fost inchisa")
                print("Clientul a fost inchis")
                return 1


class PaginaErori(tk.Frame):

    def __init__(self, parinte, controler):
        tk.Frame.__init__(self, parinte)

        self.tree = self.create_tree_widget()  # creare tree view

        stergere_eroare = tk.Button(self, text="Sterge eroare",
                                    command=lambda: self.stergere_er())
        stergere_eroare.grid(row=15, column=0, padx=10, pady=10, sticky="nsew")

        intoarcere = tk.Button(self, text="Monitorizare",
                               command=lambda: controler.arata_pagina(PaginaMonitorizare))
        intoarcere.grid(row=16, column=0, padx=10, pady=10, sticky="nsew")
        self.update_erori()

    def stergere_er(self):
        eroare_selectata = self.tree.selection()[0]  # salvare eroare selectata
        if not eroare_selectata:
            return
        date_eroare = self.tree.item(eroare_selectata)  # salveaza datele erorii
        self.tree.delete(eroare_selectata)

        try:
            cursor = bazadateUser.cursor()
            # pregateste cursorul
            sql = "DELETE FROM erori WHERE ID = %s"  # comanda de stergere mysql
            adr = (int(date_eroare['values'][0]),)
            cursor.execute(sql, adr)  # executa comanda non-query
            bazadateUser.commit()  # comite in baza de date
        except:
            print("Eroare la stergere in baza de date")

    def update_erori(self):
        Thread(target=self.populate_tree_widget).start()

    def populate_tree_widget(self):
        self.tree.after(0, self.update_tree_widget)

    def update_tree_widget(self):
        self.tree.delete(*self.tree.get_children())  # clear existing data
        try:
            cursor = bazadateUser.cursor()  # define cursor in the database
            cursor.execute("SELECT * FROM erori")  # execute SELECT command
            rezultate = cursor.fetchall()  # save results
            for x in rezultate:
                # add error
                self.tree.insert('', tk.END, values=(x[0], x[1], x[2]))
        except Exception as e:
            print(e)
        finally:
            self.tree.after(5000, self.populate_tree_widget)  # schedule the next update

    def create_tree_widget(self):
        columns = ('ID Eroare', 'Explicatie', 'Data')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # define headings
        tree.heading('ID Eroare', text='ID Eroare')
        tree.heading('Explicatie', text='Explicatie')
        tree.heading('Data', text='Data')

        tree.grid(row=0, column=0, sticky=tk.NSEW)

        bazadateUser.connect()  # reconectare la baza de date
        cursor = bazadateUser.cursor()  # definire cursor in baza date
        while 1:
            try:
                cursor.execute("SELECT * FROM erori")  # executare comanda SELECT
                rezultate = cursor.fetchall()  # salvare rezultate

                for x in rezultate:
                    # adaugare eroare
                    tree.insert('', tk.END, values=(x[0], x[1], x[2]))
                return tree
            except Exception as e:
                print(e)


if __name__ == '__main__':
    aplicatie = Pagina()
    aplicatie.title("Monitorizare Servere")
    aplicatie.geometry("")
    aplicatie.iconbitmap('photo.ico')
    aplicatie.mainloop()