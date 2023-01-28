'''
Medix Translation
CST8333 - Assignment 3
@author: Cassidy Creaco 
Student no: 040688954
100% of Source Code
'''

from tkinter import *
import tkinter.messagebox as MessageBox
import mysql.connector
import googletrans
import textblob
from tkinter import ttk, messagebox
import pyttsx3
import time
from datetime import datetime
import customtkinter
from customtkinter.windows.widgets.ctk_label import CTkLabel


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Main class that sets all of the frames into the GUI 
class MedixTranslation(Tk):
    
    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)
        self.container = Frame(self)
        
        MedixTranslation.title(self, "Medix Translation")
        MedixTranslation.geometry(self, "1100x500")
        
        self.container.pack(side="top", fill="both", expand=True)
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        
        self.shared_data = {
            "userID" : StringVar(),
            "clientID": StringVar(),
            "clientFN": StringVar(),
            "clientLN": StringVar()
            }
        
        self.current_frame = None
        self.show_frame(UserLogin)

    def show_frame(self, new_frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = new_frame_class(self.container, controller=self)
        self.current_frame.pack(fill="both", expand=True)
        menubar = self.current_frame.menubar(self)
        self.configure(menu=menubar)
    

# User login frame that connects to the database, verifies the credentials entered by the user and authorizes them into the application if credentials are verified
class UserLogin(Frame):
    
    db = mysql.connector.connect(
            host="localhost",
            port="3309",
            user="root",
            passwd="password",
            database="medixtranslation"
        )
        
    cursorObject = db.cursor()
    
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent, bg="#363534")
        self.controller = controller
        
        self.controller.userID = StringVar()
        
        self.title = customtkinter.CTkLabel(self, text="Medix Translation", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title.grid(row=1, column=1)
        
        self.description = customtkinter.CTkLabel(self, text="Login", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.description.grid(row=2, column=1, pady=25, sticky=W)
    
        self.usernametitle = customtkinter.CTkLabel(self, text="Username")
        self.usernametitle.grid(row=3, column=1, sticky=W)

        self.passwordtitle = customtkinter.CTkLabel(self, text="Password")
        self.passwordtitle.grid(row=4, column=1, sticky=W)

        self.username_input = customtkinter.CTkEntry(self, width=100)
        self.username_input.grid(row=3, column=1, sticky=E)

        self.password_input = customtkinter.CTkEntry(self, show="*", width=100)
        self.password_input.grid(row=4, column=1, sticky=E)

        self.submit_button = customtkinter.CTkButton(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=1, pady=10, sticky=W)

        self.register_button = customtkinter.CTkButton(self, text="New user? Register here", command=lambda: controller.show_frame(RegisterUser))
        self.register_button.grid(row=6, column=1, sticky=W)
    
        self.controller = controller
        
        self.count = 0
        
    def submit(self):
        username = self.username_input.get()
        password = self.password_input.get()
        
        if(username == ""):
            MessageBox.showinfo(title="Error", message="Username cannot be blank")
        if(password == ""):
            MessageBox.showinfo(title="Error", message="Password cannot be blank")
        else:
            self.loginto(username, password)
            return True;
        

    def loginto(self, username, password):
        query = "SELECT userID, username, password FROM USER WHERE username ='" + username + "' AND password='" + password + "';"
        self.cursorObject.execute(query)
        myresult = self.cursorObject.fetchall()
        
        
        if myresult:
            print("success login")
            for row in myresult:
                id = row[0]
                self.controller.shared_data["userID"].set(id)
            self.controller.show_frame(ClientList)
            return True;
        else:
            self.count += 1
            MessageBox.showinfo(title="Error", message="Incorrect username and/or password")
            if(self.count==5):
                MessageBox.showinfo(title="User Lockout", message="User is unable to attempt login for 3 minutes. Program will be unresponsive.")
                time.sleep(300)
            print(self.count)
            return False;
        
        
        
    def menubar(self, MedixTranslation):
        menubar = Menu(MedixTranslation, bg='#363534')
        file_menu = Menu(menubar)
        file_menu.add_command(label="Exit", command=self.controller.container.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        return menubar
        

# Translator frame that is accessed through login credentials, ability to translte from text-to-text and text-to-speech 
class Translator(Frame):
    
    db = mysql.connector.connect(
            host="localhost",
            port="3309",
            user="root",
            passwd="password",
            database="medixtranslation"
        )
        
    cursorObject = db.cursor(buffered=True)
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="#363534")
        self.controller = controller
        
        titles = "Translations for " + self.controller.shared_data["clientFN"].get() + " " +  self.controller.shared_data["clientLN"].get() 
        
        
        #title
        self.title = customtkinter.CTkLabel(self, text=titles)
        self.title.grid(row=0, column=1, pady=20, padx=10)
        
        # Language list from google translate
        self.languages = googletrans.LANGUAGES
        self.language_list = list(self.languages.values())
            
        # Original Text Boxes
        self.original_text = customtkinter.CTkTextbox(self, height=200, width=400)
        self.original_text.grid(row=1, column=0, columnspan=3, padx=10)
            
        # Translate Button
        self.translate_button = customtkinter.CTkButton(self, text="Translate", command=self.translate_it)
        self.translate_button.grid(row=1, column=3, columnspan=3, padx=10)
            
        # Translated Text Box
        self.translated_text = customtkinter.CTkTextbox(self, height=200, width=400)
        self.translated_text.grid(row=1, column=6, columnspan=3, pady=20, padx=10)
            
        # Language boxes
        self.original_combo = customtkinter.CTkComboBox(self, width=200, values=self.language_list)
        self.original_combo.grid(row=2, column=0, columnspan=3)
            
        self.translated_combo = customtkinter.CTkComboBox(self, width=200, values=self.language_list)
        self.translated_combo.grid(row=2, column=6, columnspan=3)
            
            
        # Clear button
        self.clear_button = customtkinter.CTkButton(self, text="Clear", width=10, command=self.clear)
        self.clear_button.grid(row=6, column=3, sticky=NSEW)
            
        # Speak button
        self.speak_button = customtkinter.CTkButton(self, text="Speak", width=10, command=self.text_to_speech)
        self.speak_button.grid(row=6, column=4, sticky=NSEW)
        
        # Save button
        self.save_button = customtkinter.CTkButton(self, text="Save", width=20, command=self.save_translation)
        self.save_button.grid(row=6, column=5, sticky=NSEW)
           
        historyquery = "SELECT * FROM translations WHERE clientId = " + self.controller.shared_data["clientID"].get()
        self.cursorObject.execute(historyquery)
        self.db.commit()
        
        x = 9
        #headers
        translationId = customtkinter.CTkLabel(self, width=5, text="Translation ID")
        translationId.grid(row=8, column=0, pady=2)
        
        languageTo = customtkinter.CTkLabel(self, width=5,text="Translated Language")
        languageTo.grid(row=8, column=1, pady=2)
        
        languageFrom = customtkinter.CTkLabel(self, width=5, text="Original Language")
        languageFrom.grid(row=8, column=2, pady=2)
        
        originalText = customtkinter.CTkLabel(self, width=5,  text="Original Text")
        originalText.grid(row=8, column=3, pady=2)
        
        translatedText = customtkinter.CTkLabel(self, width=5, text="Translated Text")
        translatedText.grid(row=8, column=4, pady=2)
        
        userid = customtkinter.CTkLabel(self, width=5, text="User ID")
        userid.grid(row=8, column=5, pady=2)
        
        clientId = customtkinter.CTkLabel(self, width=5, anchor='w', text="Client ID")
        clientId.grid(row=8, column=6, pady=2)
        
        date = customtkinter.CTkLabel(self, width=5, anchor='w', text="Date")
        date.grid(row=8, column=7, pady=2)
        
        #table
        for rows in self.cursorObject:
            for j in range(len(rows)):
                e = customtkinter.CTkLabel(self, width=10, anchor='w',  text=rows[j])
                e.grid(row=x, column=j)
                
            x=x+1
    
    def translate_it(self):
                
                # Clear previous translations
                self.translated_text.delete(1.0, END)
                
                try: 
                    # Get languages from dictionary keys
                    # Get From Language Key
                    for key, value in self.languages.items(): 
                        if (value == self.original_combo.get()):
                            self.from_language_key = key 
                    # Get the to language key
                    for key, value in self.languages.items(): 
                        if (value == self.translated_combo.get()):
                            self.to_language_key = key 
                    
                    # Turn original text to a textblob            
                    words = textblob.TextBlob(self.original_text.get(1.0, END))
                    
                    # Translate Text
                    words = words.translate(from_lang=self.from_language_key , to=self.to_language_key)
                    
                    
                    # Output Translated Text to box
                    self.translated_text.insert(1.0, words)
                    
                    return True;
                  
                #Test that shows exception if unable to translate  
                except Exception as e: 
                    messagebox.showerror("Translator", e)
            
    def clear(self):
        # Clear the text boxes
        self.original_text.delete(1.0, END)
        self.translated_text.delete(1.0, END)
        
        
    def text_to_speech(self):     
        try: 
            # Get languages from dictionary keys
            # Get From Language Key
            for key, value in self.languages.items(): 
                if (value == self.original_combo.get()):
                    self.from_language_key = key 
            # Get the to language key
            for key, value in self.languages.items(): 
                if (value == self.translated_combo.get()):
                    self.to_language_key = key 
            
            # Turn original text to a textblob            
            words = textblob.TextBlob(self.original_text.get(1.0, END))
            
            # Translate Text
            words = words.translate(from_lang=self.from_language_key , to=self.to_language_key)
            
        except Exception as e: 
            messagebox.showerror("Translator", e)
            
        # inital engine
        engine = pyttsx3.init()
        
        # pass text to speech engine
        engine.say(words)
        
        # run the engine
        engine.runAndWait()
    
    def save_translation(self):
        dateTimeObj = datetime.now()

        savequery = "INSERT INTO TRANSLATIONS(languageTo, languageFrom, originalText, translatedText, userId, clientId, date) VALUES('" + self.to_language_key + "', '" + self.from_language_key + "', '" + str(self.original_text.get(1.0, END)) + "', '" + str(self.translated_text.get(1.0, END)) + "', '" + self.controller.shared_data["userID"].get() + "', '" + self.controller.shared_data["clientID"].get() + "', '" + str(dateTimeObj) + "');"  
        self.cursorObject.execute(savequery)
        self.db.commit()
        
        if(self.cursorObject.rowcount >= 1): 
            print(self.cursorObject.rowcount, "record inserted.")
            self.controller.show_frame(Translator)
        else:         
            print("Unable to enter into database")
        
    def menubar(self, MedixTranslation):
        menubar = Menu(MedixTranslation)
        file_menu = Menu(menubar)
        file_menu.add_command(label="Clients", command=lambda: self.controller.show_frame(ClientList))
        file_menu.add_command(label="Logout", command=lambda: self.controller.show_frame(UserLogin))
        file_menu.add_command(label="Exit", command=self.controller.container.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        return menubar
    

        
#Register user frame that prompts the user to enter their credentials to make a profile for Medix Translation
class RegisterUser(Frame):
    
    db = mysql.connector.connect(
            host="localhost",
            port="3309",
            user="root",
            passwd="password",
            database="medixtranslation"
        )
        
    cursorObject = db.cursor(buffered=True)
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent, bg="#363534")
        self.controller = controller

        self.description = customtkinter.CTkLabel(self, text=" Register", font=("Arial", 24))
        self.description.grid(row=2, column=1, pady=25, sticky=W)
        
        #titles for input
        self.usernametitle = customtkinter.CTkLabel(self, text="Username")
        self.usernametitle.grid(row=3, column=1, sticky=W)
        
        self.passwordtitle = customtkinter.CTkLabel(self, text="Password")
        self.passwordtitle.grid(row=4, column=1, sticky=W)     

        self.fntitle = customtkinter.CTkLabel(self, text="First Name")
        self.fntitle.grid(row=5, column=1, sticky=W)

        self.lntite = customtkinter.CTkLabel(self, text="Last Name")
        self.lntite.grid(row=6, column=1, sticky=W)

        self.ptitle = customtkinter.CTkLabel(self, text="Position")
        self.ptitle.grid(row=7, column=1, sticky=W)
        
        #entries
        self.username_input = customtkinter.CTkEntry(self, width=100)
        self.username_input.grid(row=3, column=2, sticky=E)

        self.password_input = customtkinter.CTkEntry(self, show="*", width=100)
        self.password_input.grid(row=4, column=2, sticky=E) 
        
        self.fn_input = customtkinter.CTkEntry(self, width=100)
        self.fn_input.grid(row=5, column=2, sticky=E)

        self.ln_input = customtkinter.CTkEntry(self, width=100)
        self.ln_input.grid(row=6, column=2, sticky=E)
        
        self.pos_input = customtkinter.CTkEntry(self, width=100)
        self.pos_input.grid(row=7, column=2, sticky=E) 
        
        #register button
        self.register_button = customtkinter.CTkButton(self, text="Register", command=self.register)
        self.register_button.grid(row=8, column=1, pady=10, sticky=W)
        
    def register(self):
        
        username = self.username_input.get()
        password = self.password_input.get()
        firstName = self.fn_input.get()
        lastName = self.ln_input.get()
        position = self.pos_input.get()
        
        if(username == "" or password == "" or firstName == "" or lastName == "" or position == ""):
            MessageBox.showinfo(title="Error", message="Please ensure no entries are left blank.")
        else:
            self.submitToDB(username, password, firstName, lastName, position)
        
        if(self.cursorObject.rowcount >=1): 
            print(self.cursorObject.rowcount, "record inserted.")
            self.controller.show_frame(UserLogin)
        else:         
            print("Unable to enter into database")
            
        
    def submitToDB(self, username, password, firstName, lastName, position):
        query = "INSERT INTO USER(username, password, firstname, lastname, position) VALUES('" + username + "', '" + password + "', '" + firstName + "', '" + lastName + "', '" + position + "');"
        self.cursorObject.execute(query)
        
        self.db.commit()
        
        if(self.cursorObject.rowcount >= 1): 
            print(self.cursorObject.rowcount, "record inserted.")
        else:         
            print("Unable to enter into database")
        
        
    def menubar(self, MedixTranslation):
        menubar = Menu(MedixTranslation)
        file_menu = Menu(menubar)
        file_menu.add_command(label="Exit", command=self.controller.container.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        return menubar
        
class ClientList(Frame):
    
    
    db = mysql.connector.connect(
            host="localhost",
            port="3309",
            user="root",
            passwd="password",
            database="medixtranslation"
        )
        
    cursorObject = db.cursor(buffered=True)
    
        
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent, bg="#363534")
        self.controller = controller
               
                
        self.description = customtkinter.CTkLabel(self, text="Please fill out the below to add a new client.", font=("Arial", 10))
        self.description.grid(row=2, column=1, pady=25, sticky=W)
        
        #titles for input
        self.fntitle = customtkinter.CTkLabel(self, text="First Name")
        self.fntitle.grid(row=3, column=1, sticky=W)
        
        self.lntitle = customtkinter.CTkLabel(self, text="Last Name")
        self.lntitle.grid(row=4, column=1, sticky=W)     

        self.dobtitle = customtkinter.CTkLabel(self, text="Date of birth")
        self.dobtitle.grid(row=5, column=1, sticky=W)
        
        self.fn_input = customtkinter.CTkEntry(self, width=100)
        self.fn_input.grid(row=3, column=2, sticky=E)

        self.ln_input = customtkinter.CTkEntry(self, width=100)
        self.ln_input.grid(row=4, column=2, sticky=E)
        
        self.dob_input = customtkinter.CTkEntry(self, width=100)
        self.dob_input.grid(row=5, column=2, sticky=E) 
        
        #register button
        self.register_button = customtkinter.CTkButton(self, text="Register New Client", command=self.register)
        self.register_button.grid(row=8, column=1, pady=10, sticky=W)
        
        #show all clients button
        self.clients_button = customtkinter.CTkButton(self, text="Show Clients", command=self.clients)
        self.clients_button.grid(row=9, column=1, pady=10, sticky=W)
        
    def menubar(self, MedixTranslation):
        menubar = Menu(MedixTranslation)
        file_menu = Menu(menubar)
        file_menu.add_command(label="Logout", command=lambda: self.controller.show_frame(UserLogin))
        file_menu.add_command(label="Exit", command=self.controller.container.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        return menubar   
        
    def register(self):      
        
        firstName = self.fn_input.get()
        lastName = self.ln_input.get()
        dateOfBirth = self.dob_input.get()
        
        if(firstName == "" or lastName == "" or dateOfBirth == ""):
            MessageBox.showinfo(title="Error", message="Please ensure no entries are left blank.")
            
        else:
            self.submitToDB(firstName, lastName, dateOfBirth)
            self.clients()
    
    def submitToDB(self, firstName, lastName, dateOfBirth):
        
        query = "INSERT INTO clients(firstname, lastname, dob, userId) VALUES('" + firstName + "', '" + lastName + "', '" + dateOfBirth + "', '" + self.controller.shared_data["userID"].get() + "');"
        self.cursorObject.execute(query)
        
        self.db.commit()
        
        if(self.cursorObject.rowcount >= 1): 
            print(self.cursorObject.rowcount, "record inserted.")
        else:         
            print("Unable to enter into database")
        
    def clients(self):
        
        clientquery = "SELECT clientId, firstName, lastName, dob FROM clients WHERE userId = " + self.controller.shared_data["userID"].get()
        self.cursorObject.execute(clientquery) 
    
        self.db.commit()
        i = 13
        #headers
        clientID = customtkinter.CTkLabel(self, width=10, anchor='w', text="Client ID")
        clientID.grid(row=10, column=0)
        fn = customtkinter.CTkLabel(self, width=10, anchor='w', text="First Name")
        fn.grid(row=10, column=1)
        ln = customtkinter.CTkLabel(self, width=10, anchor='w', text="Last Name")
        ln.grid(row=10, column=2)
        d = customtkinter.CTkLabel(self, width=10, anchor='w', text="Date of Birth")
        d.grid(row=10, column=3)

        
        #table
        for rows in self.cursorObject:
            for j in range(len(rows)):
                e = customtkinter.CTkLabel(self, width=10, anchor='w',  text=rows[j])
                e.grid(row=i, column=j)
                
            b = customtkinter.CTkButton(self, width=5, text="Select", anchor='w', command=lambda k=rows[0]: self.select_client(k))
            b.grid(row=i, column=5)
            
            i=i+1
            
    def select_client(self, client_id):
        
        selectclient = "SELECT firstName, lastName FROM clients WHERE clientID = " + str(client_id) + ";"
        self.cursorObject.execute(selectclient)
        self.db.commit()
        
        for row in self.cursorObject:
            fn = row[0]
            ln = row[1]
        
            self.controller.shared_data["clientID"].set(client_id)
            self.controller.shared_data["clientFN"].set(fn)
            self.controller.shared_data["clientLN"].set(ln)
        
        self.controller.show_frame(Translator)

    
    
app = MedixTranslation()     
app.mainloop()