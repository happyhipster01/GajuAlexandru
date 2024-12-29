from tkinter import *
from tkinter import messagebox
import numpy as np
import cv2
from setup_database import mycol
import similaritymeasures
import webbrowser

# Parametrii ferestrei

# Setarea dimensiunii ferestrei canvas la 400x400
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

canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8) # Se creează o matrice tridimensională cu dimensiunile specificate în variabila canvas_size # 3 reprezintă RGB # dimensiunea ferestrei este de 400x400x3 

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
                cv2.line(canvas,(pt1_x,pt1_y),(x,y),color=(255,255,255),thickness=3) # Unește punctele (pt1_x,pt1_y),(x,y)  printr-o linie albă pe suprafața canvas-ului, RGB -> (255,255,255)
                pt1_x,pt1_y=x,y
                valid_drawing = True # Verifică daca utilizatorul a desenat ceva în canvas
        elif event==cv2.EVENT_LBUTTONUP:
            drawing=False
            cv2.line(canvas,(pt1_x,pt1_y),(x,y),color=(255,255,255),thickness=3)

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

    
# Obținerea detaliilor utilizatorului din baza de date folosind adresa de email
def get_user_details():
    user_details = mycol.find_one({'email':email.get()})
    return user_details


def check_grid(draw1,draw2):

    # 2 matrici pentru a verifica dacă forma originală și forma actuală acoperă același număr de grile
    draw_grid1 = [[0 for i in range(4)]for i in range(4)]
    draw_grid2 = [[0 for i in range(4)]for i in range(4)]

    # Marchează grila vizitată de desen în forma originală
    for i in range(4):
        for j in range(4):
            if 255 in draw1[i*100:(i+1)*100-1,j*100:(j+1)*100-1]:
                draw_grid1[i][j] = 1
    
    # Marchează grila vizitată de desen în forma originală
    for i in range(4):
        for j in range(4):
            if 255 in draw2[i*100:(i+1)*100-1,j*100:(j+1)*100-1]:
                draw_grid2[i][j] = 1
            
    # Se verifică dacă desenul acoperă aceeași suprafață în ambele imagini.
    return draw_grid1 == draw_grid2


def drawing_is_similar(draw1, draw2):
    
    # Se verifică numărul de grile vizitate de desen atât în imaginea originală, cât și în cea actuală. 
    if not check_grid(draw1,draw2):
        return False

    # Convertește matricea 400x400x3 în matrice 160000x3 pentru a calcula MSE.
    img_canvas1=draw1.reshape(160000,3)
    img_canvas2=draw2.reshape(160000,3)

    # Eroarea medie pătratică (mean squared error)
    mse = similaritymeasures.mse(img_canvas1,img_canvas2)
    print('mse',mse)

    # Dacă MSE este < 0.035, atunci se va returna true, altfel false.
    return mse < 0.035


def validation():

    if email.get()!="" and password.get()!="" and valid_drawing: # Verificarea câmpurilor obligatorii
        user_details = get_user_details() # Obținerea detaliile utilizatorului după adresa de email din baza de date
        email_format = emailformat_checker() # Verificarea formatului email-ului

        if email_format:
            if user_details != None:
                if user_details['password'] == password.get():

                    user_img = np.frombuffer(user_details['canvas'], dtype=np.uint8) # Conversia octeților în matrice de tip Numpy
                    user_canvas = user_img.reshape((canvas_size[1], canvas_size[0], 3)) # Refacerea matricei NumPy la dimensiunile corespunzătoare -> 400x400x3
                    
                    if valid_drawing and drawing_is_similar(canvas, user_canvas): # Verifică dacă utilizatorul a desenat o parolă grafică similară cu cea de la înregistrare
                        # messagebox.showinfo("INFO","Autentificarea a avut loc cu succes")
                        webbrowser.open("https://mta.ro/")
                    else:
                        messagebox.showerror("EROARE", "Parola ta grafică este incorectă!")
                else:
                    messagebox.showerror("EROARE","Parola ta este incorectă!")
            else:
                messagebox.showerror("EROARE",'Adresa ta de email nu există, te rog înregistrează-te înainte!')
        else:
            messagebox.showerror("EROARE","Formatul adresei de email nu este valid!")
    else:
        messagebox.showerror("EROARE","Completează câmpurile obligatorii!")



def emailformat_checker():
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


def shifting_form():
    screen.destroy()
    import signup


# Interfața grafică

screen = Tk()

# Variabile

email=StringVar()
password = StringVar()

# Screen-uri

screen.geometry("700x600")
screen.maxsize(width="700",height="600")
screen.minsize(width="700",height="600")
screen.config(bg="#B660CD")
screen.title("Autentificare")

# Titlul interfeței de Log-in

title = Label(text="LOG IN",font=("Arial",72,"bold"),pady="5",bg="#B660CD",fg="#FCD12A").pack(pady="50")

# Login frame

login_frame = Frame(screen,width="380",height="320",bg="#FFCCFF")
login_frame.place(x="162",y="150")

# Câmpurile din log-in
# Câmpul 1

email_label = Label(width="15",padx="5",pady="5",text="User Email",bg="#FFCCFF",fg="#B660CD",font=("Calibri",20,"bold","italic"))
email_label.place(x="166",y="170")

# Câmpul 2

email_entry = Entry(textvariable=email,width="26",selectbackground="#FFCCFF",selectforeground="black",font=("Calibri",15,"bold","italic"))
email_entry.place(x="215",y="210")

# Câmpul 3

password_label = Label(width="15",padx="5",pady="5",text="User Password",bg="#FFCCFF",fg="#B660CD",font=("Calibri",20,"bold","italic"))
password_label.place(x="188",y="240")

# Câmpul 4

password_entry = Entry(textvariable=password,show="*",width="26",selectbackground="#FFCCFF",selectforeground="black",font=("Calibri",15,"bold","italic"))
password_entry.place(x="215",y="280")

# Câmpul 5

draw_your_secret_btn = Button(text="Draw Your Secret",width="23",bg="#FCD12A",fg="#B660CD",font=("Arial",15,"bold","italic"),command=DAS)
draw_your_secret_btn.place(x="215", y="330")

# Câmpul 6

login_btn = Button(text="Log In",width="23",font=("Arial",14,"bold","italic"),bg="#FCD12A",fg="#B660CD",command=validation)
login_btn.place(x="215",y="390")

# Câmpul 7

txt=Label(text="not a member?",font=("Calibri",12,"bold","italic"),bg="#FCD12A",fg="#B660CD").place(x="215",y="435")

# Câmpul 8

sgnup_btn = Button(text="Sign up now",width="14",font=("Calibri",10,"bold","italic"),bg="#FCD12A",fg="#B660CD",command=shifting_form).place(x="340",y="435")

screen.mainloop()