import tkinter as tk
from tkinter import Toplevel, Checkbutton, IntVar, messagebox

# Database dei comandi e relativi flag
comandi_e_flag = {
    "ls": ["-l (dettagliato)", "-a (includi file nascosti)", "-h (dimensioni leggibili)"],
    "grep": ["-i (ignora maiuscole/minuscole)", "-r (ricorsivo)", "-v (inversa)"],
    "ps": ["-e (tutti i processi)", "-f (formato completo)", "-u (specifica utente)"],
    "tar": ["-c (crea archivio)", "-x (estrae archivio)", "-z (compressione gzip)"]
}

# Funzione globale per simulare l'interruzione del comando
simulazione_in_corso = False  # Stato del comando simulato


def mostra_selettore_flag(comando):
    """Crea una finestra per selezionare i flag del comando."""
    top = Toplevel(root)
    top.title(f"Seleziona opzioni per {comando}")
    top.geometry("400x300")

    label = tk.Label(top, text=f"Seleziona le opzioni per '{comando}':")
    label.pack(pady=10)

    variabili_flag = []  # Per tenere traccia dei flag selezionati

    def applica_flag():
        """Mostra il comando e i flag selezionati nell'area di output."""
        global simulazione_in_corso
        if simulazione_in_corso:
            messagebox.showwarning("Attenzione", "Un comando è già in esecuzione!")
            return

        flag_selezionati = []
        for var, flag in variabili_flag:
            if var.get():
                # Prende solo la parte del flag (senza descrizione)
                flag_selezionati.append(flag.split()[0])
        comando_completo = f"{comando} {' '.join(flag_selezionati)}"
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Simulazione: {comando_completo}\nEsecuzione in corso...\n")
        simulazione_in_corso = True
        top.destroy()

    for flag in comandi_e_flag[comando]:
        var = IntVar()
        chk = Checkbutton(top, text=flag, variable=var)
        chk.pack(anchor="w")
        variabili_flag.append((var, flag))

    btn_applica = tk.Button(top, text="Applica e Mostra", command=applica_flag)
    btn_applica.pack(pady=10)


def interrompi_comando():
    """Interrompe la simulazione del comando."""
    global simulazione_in_corso
    if simulazione_in_corso:
        simulazione_in_corso = False
        output_text.insert(tk.END, "Simulazione interrotta.\n")
    else:
        messagebox.showinfo("Informazione", "Nessuna simulazione in corso.")


# Creazione finestra principale
root = tk.Tk()
root.title("Shell Grafica Linux con Flag e Interruzione")
root.geometry("800x600")

# Barra dei menu
menu = tk.Menu(root)
root.config(menu=menu)

# Categorie e comandi
categorie = {
    "Comandi di Base": ["ls", "pwd", "cd", "mkdir", "touch", "rm"],
    "Gestione dei Processi": ["ps", "top", "kill"]
}

for categoria, comandi in categorie.items():
    submenu = tk.Menu(menu, tearoff=0)
    for comando in comandi:
        submenu.add_command(label=comando, command=lambda cmd=comando: mostra_selettore_flag(cmd))
    menu.add_cascade(label=categoria, menu=submenu)

# Input del comando
frame_input = tk.Frame(root)
frame_input.pack(pady=10, padx=10, fill=tk.X)

btn_interrompi = tk.Button(frame_input, text="Interrompi Comando", command=interrompi_comando, bg="red", fg="white")
btn_interrompi.pack(side=tk.LEFT, padx=5)

# Output dell'esecuzione
frame_output = tk.Frame(root)
frame_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

label_output = tk.Label(frame_output, text="Output:")
label_output.pack(anchor="w")

output_text = tk.Text(frame_output, height=15)
output_text.pack(fill=tk.BOTH, expand=True)

# Avvia la finestra principale
root.mainloop()
