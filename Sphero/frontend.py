import tkinter as tk
import subprocess
import threading
import time
import atexit

# Functie om het SSH-commando uit te voeren
def run_ssh_command():
    # Start het SSH-commando
    try:
        subprocess.Popen(["ssh", "pi@192.168.0.70", "./sphero1.sh"])
    except Exception as e:
        status_label.config(text=f"Fout: {e}")

# Functie om de timer te starten
def start_timer():
    # Zet de timer naar 5 minuten (300 seconden)
    countdown_time = 300
    # Start de timer in een aparte thread om de GUI niet te blokkeren
    threading.Thread(target=update_timer, args=(countdown_time,)).start()
    # Voer het SSH-commando uit
    run_ssh_command()

# Functie om de timer bij te werken
def update_timer(countdown_time):
    while countdown_time >= 0:
        # Converteer seconden naar minuten:seconden formaat
        minutes, seconds = divmod(countdown_time, 60)
        time_format = f"{minutes:02d}:{seconds:02d}"
        # Update het timer_label
        timer_label.config(text=f"Timer: {time_format}")
        # Wacht 1 seconde
        time.sleep(1)
        # Verlaag de countdown
        countdown_time -= 1
    # Als de tijd voorbij is
    timer_label.config(text="Tijd is om!")

# Functie die wordt aangeroepen wanneer het script eindigt
def on_exit():
    # Toon een boodschap in de console
    print("Het script is gestopt. Boodschap bij exit.")

# Registreer de exit-functie
atexit.register(on_exit)

# Maak het Tkinter hoofdvenster aan
root = tk.Tk()
root.title("Start Player 1")

# Maak een label aan om de timer weer te geven
timer_label = tk.Label(root, text="Timer: 05:00", font=("Helvetica", 16))
timer_label.pack(pady=20)

# Maak een knop aan om het SSH-commando te starten en de timer te beginnen
start_button = tk.Button(root, text="Start SSH en Timer", command=start_timer, font=("Helvetica", 14))
start_button.pack(pady=20)

# Maak een statuslabel voor foutmeldingen of statusupdates
status_label = tk.Label(root, text="", font=("Helvetica", 12))
status_label.pack(pady=10)

# Start de Tkinter event loop
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Script onderbroken door gebruiker.")
    on_exit()
