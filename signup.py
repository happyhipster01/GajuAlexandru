from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import cv2
from setup_database import mycol


# Parametrii ferestrei
canvas_size = (400, 400)
cell_size = 100

# Parametrii folosiți pentru a desena 
drawing_color = (255, 255, 255, 255) # White
drawing_thickness = 3

# Parametrii grid-ului
grid_color = (255, 255, 255, 127) # Liniile grid-ului sunt albe și au opacitate de 50%
grid_thickness = 1
drawing = False # Condiția este adevărată atunci când mouse-ul este apăsat
pt1_x , pt1_y = None , None

canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)  # Se creează o matrice tridimensională cu dimensiunile specificate în variabila canvas_size # 3 reprezintă RGB # dimensiunea ferestrei este de 400x400x3 
valid_drawing = False # Variabilă de tip flag care verifică dacă utilizatorul a desenat sau nu ceva în fereastră

# Funcția care face posibilă desenarea cu mouse-ul în fereastră
def DAS():
    global pt1_x,pt1_y,drawing, canvas, valid_drawing

    def draw_line(event, x, y, flags, params): # Gestionează evenimentele mouse-ului
        global pt1_x,pt1_y,drawing, canvas, valid_drawing
        if event==cv2.EVENT_LBUTTONDOWN:
            drawing=True # Verifică dacă utilizatorul este în procesul de desenare sau nu
            valid_drawing = True # Verifică daca utilizatorul a desenat ceva în canvas
            pt1_x,pt1_y=x,y # Punctul de început (pt1_x, pt1_y) și punctul curent (x, y) pe canvas
        elif event==cv2.EVENT_MOUSEMOVE:
            if drawing==True:
                cv2.line(canvas,(pt1_x,pt1_y),(x,y),color=(255,255,255),thickness=3)  # Unește punctele (pt1_x,pt1_y),(x,y)  printr-o linie albă pe suprafața canvas-ului, RGB -> (255,255,255)
                pt1_x,pt1_y=x,y
                valid_drawing = True # Verifică daca utilizatorul a desenat ceva în canvas
        elif event==cv2.EVENT_LBUTTONUP:
            cv2.line(canvas,(pt1_x,pt1_y),(x,y),color=(255,255,255),thickness=3)
            drawing=False

    cv2.namedWindow("Canvas") # Crearea ferestrei Canvas
    cv2.setMouseCallback("Canvas", draw_line) # Setează funcția "draw_line" ca funcție de callback pentru evenimentele mouse-ului

    # Realizarea grid-ului
    for i in range(0, len(canvas), cell_size):
        cv2.line(canvas, (0, i), (len(canvas), i), grid_color, grid_thickness)
        cv2.line(canvas, (i, 0), (i, len(canvas)), grid_color, grid_thickness)


    # Bucla principală pentru actualizarea canvas-ului
    while True:
        cv2.imshow("Canvas", canvas)
        key = cv2.waitKey(1)
        if key == ord("s"):
            # Din imaginea finală se elimină liniile grid-ului pentru a evita creșterea nejustificată a similitudinii în timpul comparării imaginilor
            for i in range(0, len(canvas), cell_size):
                cv2.line(canvas, (0, i), (len(canvas), i), (0, 0, 0), grid_thickness)
                cv2.line(canvas, (i, 0), (i, len(canvas)), (0, 0, 0), grid_thickness)
            break

        if key == ord("r"):
            # Resetarea canvas-ului
            canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)
            valid_drawing = False
            break


    cv2.destroyAllWindows()


def validation():
    if name.get()!="" and email.get()!="" and password.get()!="" and gender.get()!="" and age.get()!="" and cpassword.get()!="" and valid_drawing:  # Verificarea câmpurilor obligatorii
        email_check=email_validation() # Verificarea formatului email-ului
        password_check=password_validation() # Verificarea formatului parolei
        duplicate_check=duplicates() # Se verifică dacă există deja un utilizator cu același user name sau cu același email
        if email_check:
            if duplicate_check:
                messagebox.showerror("EROARE","Numele sau Adresa de email deja există!")
            else:
                if password_check:
                    if cpassword.get() != password.get():
                        messagebox.showerror("EROARE", "Parolele nu corespund!")
                    else:
                        insertion_data()
                        messagebox.showinfo("INFO","Înregistrarea a avut loc cu succes!")
                        shifting_form()
                        import main
                else:
                    messagebox.showerror("EROARE","Parola trebuie să conțină: minim 8 caractere, litere majuscule și minuscule, numere și simboluri!")
        else:
            messagebox.showerror("EROARE","Formatul adresei de email nu este valid!")
    else:
        messagebox.showerror("EROARE","Completează toate câmpurile obligatorii!")

def shifting_form():
    screen.destroy()


def insertion_data():

    payload = {
        "name": name.get(),
        "email": email.get(),
        "password": password.get(),
        "gender": gender.get(),
        "age": age.get(),
        "canvas": canvas.tobytes() # Conversia matricei în bytes care pot fi stocați în baza de date.
    }
    # Adăugarea detaliilor utilizatorului în baza de date împreună cu parola grafică sub formă de octeți.
    mycol.insert_one(payload)


def email_validation():
    temp = email.get() 
    count=-1
    for i in temp:
        count+=1
        if i=="@":
            if temp[count:len(temp)]=="@gmail.com" or temp[count:len(temp)]=="@yahoo.com" or temp[count:len(temp)]=="@mta.ro":
                return True
            else:
                return False
    else:
        return False

def password_validation():
    temp = password.get()
    if len(temp)>=8:
        a,b,c,d=False,False,False,False  
        # Utilizarea mai multor variabile pentru verificarea validității parolei de acces.
        for i in temp:
            x = ord(i)
            if x>=65 and x<=90: # A-Z majuscule
                a=True
            elif x>=97 and x<=122: # a-z minuscule
                b=True
            elif x>=48 and x<=57: # 0-9 cifre
                c=True
            else: # Caractere speciale/simboluri
                d=True
        if a and b and c and d:
            return True
        else:
            return False
    else:
        return False
    
def duplicates():
    # Se verifică dacă există deja un utilizator cu același user name sau cu același email
    dup_account = list(mycol.find({'email':email.get()} and {'name':name.get()}))
    return [] != dup_account

# Interfața grafică

screen = Tk()

# Variabile

name = StringVar()
email = StringVar()
password = StringVar()
cpassword= StringVar()
gender = StringVar()
age = StringVar()

# Screen-uri
 
screen.geometry("700x600")
screen.maxsize(width="700",height="600")
screen.minsize(width="700",height="600")
screen.config(bg="#B660CD")
screen.title("Înregistrare")

# Titlul interfeței de Sign-UP

title = Label(text="SIGN UP",font=("Arial",70,"bold"),padx="4",pady="5",bg="#B660CD",fg="#FCD12A").pack(pady="25")

# Signup frame

signup_frame = Frame(screen,width="500",height="500",bg="#FFCCFF")
signup_frame.place(x="122",y="126")

# Câmpurile din sign-up
# Câmpul 1

fullname_label = Label(signup_frame,width="15",padx="5",pady="5",text="User Name",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=0,column=0,padx="5",pady="5")
fullname_entry = Entry(signup_frame,textvariable=name,selectbackground="#B660CD",selectforeground="black",font=("Calibri",15,"italic")).grid(row=0,column=1,padx="15",pady="5")

# Câmpul 2

email_label = Label(signup_frame,width="15",padx="5",pady="5",text="User Email",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=1,column=0,padx="5",pady="5")
email_entry = Entry(signup_frame,textvariable=email,selectbackground="#B660CD",selectforeground="black",font=("Calibri",15,"italic")).grid(row=1,column=1,padx="15",pady="5")

# Câmpul 3

password_label = Label(signup_frame,width="15",padx="5",pady="5",text="User Password",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=2,column=0,padx="5",pady="5")
password_entry = Entry(signup_frame,show="*",textvariable=password,selectbackground="#B660CD",selectforeground="black",font=("Calibri",15,"italic")).grid(row=2,column=1,padx="15",pady="5")

# Câmpul 4

cpassword_label = Label(signup_frame,width="20",padx="5",pady="5",text="Confirm User Password",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=3,column=0,padx="5",pady="5")
cpassword_entry = Entry(signup_frame,show="*",textvariable=cpassword,selectbackground="#B660CD",selectforeground="black",font=("Calibri",15,"italic")).grid(row=3,column=1,padx="15",pady="5")

# Câmpul 5

gender.set("Radio")
gender_label = Label(signup_frame,width="15",padx="5",pady="5",text="User Gender",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=4,column=0,padx="5",pady="5")
gander_male = Radiobutton(signup_frame,text="Male",bg="#FFCCFF",value="Male",width="5",variable=gender).place(x="260",y="205")
gander_female = Radiobutton(signup_frame,text="Female",bg="#FFCCFF",width="5",value="Female",variable=gender).place(x="330",y="205")

# Câmpul 6

age_label = Label(signup_frame,width="15",padx="5",pady="5",text="User Age",bg="#FFCCFF",fg="#B660CD",font=("Calibri",15,'bold',"italic")).grid(row=5,column=0,padx="5",pady="5")
values = [int(i) for i in range(9,100)]
age.set("")
age_combo = ttk.Combobox(signup_frame,value=values,width="26",state="readonly",textvariable=age,font=("Arial",10,"italic")).grid(row=5,column=1)

# Câmpul 7

draw_your_secret = Button(signup_frame,text="Draw Your Secret",width="30",bg="#FCD12A",fg="#B660CD",font=("Arial",15,"bold","italic"),command=DAS).grid(row=6,columnspan=2,pady="15",padx="10")

# Câmpul 8

signup_btn = Button(signup_frame,text="Sign Up",width="35",bg="#FCD12A",fg="#B660CD",font=("Arial",15,"bold","italic"),command=validation).grid(row=7,columnspan=2,pady="15",padx="10")

screen.mainloop()