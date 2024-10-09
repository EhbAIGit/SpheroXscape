import tkinter as tk
import subprocess
import threading
import atexit
import paho.mqtt.client as mqtt

sshRpi = ("pi@192.168.0.70","pi@192.168.0.70","pi@192.168.0.70")
spheroIds = ("SB-24D3","SB-1D86","SB-27A5","SB-81E0","SB-7740")

# Functie om het SSH-commando uit te voeren
def run_ssh_command(sshrpi,id, number, joystick):
    try:
        ssh_command = f"./sphero.sh {id} {number} {joystick}"
        subprocess.Popen(["ssh", sshrpi, ssh_command])
    except Exception as e:
        status_label.config(text=f"Fout: {e}")

# Functie die wordt aangeroepen wanneer het script eindigt
def on_exit():
    print("Het script is gestopt. Boodschap bij exit.")

# MQTT callback functies
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_label.config(text="Correct verbonden met MQTT broker")
        client.subscribe("sphero/ball_status")
        client.subscribe("sphero/ball_status/warning")
        client.subscribe("sphero/ball_status/timing")
    else:
        mqtt_label.config(text=f"Verbinding mislukt met code {rc}")

def on_message(client, userdata, msg):
    message = f"{msg.payload.decode()}"
    if msg.topic == "sphero/ball_status":
        ball_status_listbox.insert(0, message)
    elif msg.topic == "sphero/ball_status/warning":
        warning_listbox.insert(0, message)
    elif msg.topic == "sphero/ball_status/timing":
        timing_listbox.insert(0, message)

# Functie om een bericht te sturen wanneer een speler verliest
def send_lost_message(player_number):
    client.publish(f"sphero/ball_status", f"Player {player_number} lost! It did not survive")

def send_new_game_message():
    client.publish("sphero/ball_status", "New game started")

# Functie om de MQTT-client in een thread te starten
def start_mqtt():
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.emqx.io", 1883, 60)
    client.loop_start()

# Registreer de exit-functie
atexit.register(on_exit)

# Maak het Tkinter hoofdvenster aan
root = tk.Tk()
root.title("Sphero Controller")

# Frame voor de knoppen
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Launch Player knoppen
button1 = tk.Button(button_frame, text=f"Launch Player 1", 
                       command=lambda : run_ssh_command(sshRpi[0],spheroIds[0], 0, 1),  # Standaard joystick op 0
                       font=("Helvetica", 14))
button1.grid(row=0, column=0, padx=5)

button2 = tk.Button(button_frame, text=f"Launch Player 2", 
                       command=lambda : run_ssh_command(sshRpi[0],spheroIds[1], 0, 2),  # Standaard joystick op 0
                       font=("Helvetica", 14))
button2.grid(row=0, column=1, padx=5)

button3 = tk.Button(button_frame, text=f"Launch Player 3", 
                       command=lambda : run_ssh_command(sshRpi[1],spheroIds[1], 0, 3),  # Standaard joystick op 0
                       font=("Helvetica", 14))
button3.grid(row=0, column=2, padx=5)

button4 = tk.Button(button_frame, text=f"Launch Player 4", 
                       command=lambda : run_ssh_command(sshRpi[1],spheroIds[1], 1, 4),  # Standaard joystick op 0
                       font=("Helvetica", 14))
button4.grid(row=0, column=3, padx=5)

button5 = tk.Button(button_frame, text=f"Launch Player 5", 
                       command=lambda : run_ssh_command(sshRpi[2],spheroIds[1], 0, 5),  # Standaard joystick op 0
                       font=("Helvetica", 14))
button5.grid(row=0, column=4, padx=5)

# Frame voor de verlies knoppen
lost_button_frame = tk.Frame(root)
lost_button_frame.pack(pady=10)

# Verlies knoppen
lost_button1 = tk.Button(lost_button_frame, text=f"Player 1 Lost", 
                         command=lambda: send_lost_message(1), font=("Helvetica", 12))
lost_button1.grid(row=0, column=0, padx=5)

lost_button2 = tk.Button(lost_button_frame, text=f"Player 2 Lost", 
                         command=lambda: send_lost_message(2), font=("Helvetica", 12))
lost_button2.grid(row=0, column=1, padx=5)

lost_button3 = tk.Button(lost_button_frame, text=f"Player 3 Lost", 
                         command=lambda: send_lost_message(3), font=("Helvetica", 12))
lost_button3.grid(row=0, column=2, padx=5)

lost_button4 = tk.Button(lost_button_frame, text=f"Player 4 Lost", 
                         command=lambda: send_lost_message(4), font=("Helvetica", 12))
lost_button4.grid(row=0, column=3, padx=5)

lost_button5 = tk.Button(lost_button_frame, text=f"Player 5 Lost", 
                         command=lambda: send_lost_message(5), font=("Helvetica", 12))
lost_button5.grid(row=0, column=4, padx=5)

# Frame voor de "New Game" knop
new_game_frame = tk.Frame(root)
new_game_frame.pack(pady=10)

# Nieuwe spel knop
new_game_button = tk.Button(new_game_frame, text="New Game", 
                            command=send_new_game_message, font=("Helvetica", 14))
new_game_button.pack()


# Maak een statuslabel voor foutmeldingen of statusupdates
status_label = tk.Label(root, text="", font=("Helvetica", 12))
status_label.pack(pady=10)

# MQTT status label
mqtt_label = tk.Label(root, text="Verbinding maken met MQTT broker...", font=("Helvetica", 12))
mqtt_label.pack(pady=10)

# Frame voor de drie kaders
frame = tk.Frame(root)
frame.pack(pady=20)

# Frame voor ball_status
ball_status_frame = tk.Frame(frame, bd=2, relief="groove")
ball_status_frame.grid(row=0, column=0, padx=10)

ball_status_label = tk.Label(ball_status_frame, text="GAME STATUS", font=("Helvetica", 12))
ball_status_label.pack(pady=5)

ball_status_listbox = tk.Listbox(ball_status_frame, width=50, height=10)
ball_status_listbox.pack()

# Frame voor warning
warning_frame = tk.Frame(frame, bd=2, relief="groove")
warning_frame.grid(row=0, column=1, padx=10)

warning_label = tk.Label(warning_frame, text="WARNINGS", font=("Helvetica", 12))
warning_label.pack(pady=5)

warning_listbox = tk.Listbox(warning_frame, width=50, height=10)
warning_listbox.pack()

# Frame voor timing
timing_frame = tk.Frame(frame, bd=2, relief="groove")
timing_frame.grid(row=0, column=2, padx=10)

timing_label = tk.Label(timing_frame, text="TIMING", font=("Helvetica", 12))
timing_label.pack(pady=5)

timing_listbox = tk.Listbox(timing_frame, width=50, height=10)
timing_listbox.pack()

# Start de MQTT-client in een aparte thread om de GUI niet te blokkeren
threading.Thread(target=start_mqtt).start()

# Start de Tkinter event loop
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Script onderbroken door gebruiker.")
    on_exit()
