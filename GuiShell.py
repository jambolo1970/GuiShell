import os
import subprocess
import tkinter as tk
from tkinter import Toplevel, Checkbutton, IntVar, filedialog, messagebox
import shlex
from googletrans import Translator
from threading import Thread

translator = Translator()

# Database dei comandi e relativi flag
comandi_e_flag = {
    "ls": ["-l (dettagliato)", "-a (includi file nascosti)", "-h (dimensioni leggibili)"],
    "grep": ["-i (ignora maiuscole/minuscole)", "-r (ricorsivo)", "-v (inversa)"],
    "ps": ["-e (tutti i processi)", "-f (formato completo)", "-u (specifica utente)"],
    "tar": ["-c (crea archivio)", "-x (estrae archivio)", "-z (compressione gzip)"],
}

simulazione_in_corso = False
processo_corrente = None


def mostra_selettore_flag(comando):
    top = Toplevel(root)
    top.title(f"Seleziona opzioni per {comando}")
    top.geometry("400x300")

    label = tk.Label(top, text=f"Seleziona le opzioni per '{comando}':")
    label.pack(pady=10)

    variabili_flag = []

    def applica_flag():
        global simulazione_in_corso
        if simulazione_in_corso:
            messagebox.showwarning("Attenzione", "Un comando è già in esecuzione!")
            return

        flag_selezionati = []
        for var, flag in variabili_flag:
            if var.get():
                flag_selezionati.append(flag.split()[0])
        comando_completo = f"{comando} {' '.join(flag_selezionati)}"
        input_comando.delete(0, tk.END)
        input_comando.insert(0, comando_completo)
        top.destroy()

    for flag in comandi_e_flag.get(comando, []):
        var = IntVar()
        chk = Checkbutton(top, text=flag, variable=var)
        chk.pack(anchor="w")
        variabili_flag.append((var, flag))

    btn_applica = tk.Button(top, text="Applica", command=applica_flag)
    btn_applica.pack(pady=10)


def esegui_comando():
    global simulazione_in_corso, processo_corrente
    if simulazione_in_corso:
        messagebox.showwarning("Attenzione", "Un comando è già in esecuzione!")
        return

    comando = input_comando.get()
    if not comando.strip():
        messagebox.showwarning("Attenzione", "Inserire un comando!")
        return

    simulazione_in_corso = True
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Esecuzione: {comando}\n")
    
    def run_comando():
        global processo_corrente
        try:
            args = shlex.split(comando)
            processo_corrente = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = processo_corrente.communicate()
            output_text.insert(tk.END, stdout or stderr)
        except Exception as e:
            output_text.insert(tk.END, f"Errore durante l'esecuzione: {e}\n")
        finally:
            simulazione_in_corso = False
            processo_corrente = None

    Thread(target=run_comando).start()


def interrompi_comando():
    global simulazione_in_corso, processo_corrente
    if simulazione_in_corso and processo_corrente:
        processo_corrente.terminate()
        output_text.insert(tk.END, "Comando interrotto.\n")
        simulazione_in_corso = False
        processo_corrente = None
    else:
        messagebox.showinfo("Informazione", "Nessun comando in esecuzione.")


def spiega_comando():
    comando = input_comando.get().split()[0]
    if not comando.strip():
        messagebox.showwarning("Attenzione", "Inserire un comando!")
        return

    try:
        result = subprocess.run(["man", comando], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        spiegazione_text.delete("1.0", tk.END)

        if result.returncode == 0:
            man_output = result.stdout
            traduzione = translator.translate(man_output, src='en', dest='it').text
            spiegazione_text.insert(tk.END, traduzione)
        else:
            spiegazione_text.insert(tk.END, f"Comando non trovato o man page assente per: {comando}")
    except Exception as e:
        spiegazione_text.insert(tk.END, f"Errore durante la spiegazione: {e}")


# Finestra principale
root = tk.Tk()
root.title("Shell Grafica Linux Completa")
root.geometry("900x700")

menu = tk.Menu(root)
root.config(menu=menu)

categorie = {
    "Comandi di Base": ["ls", "pwd", "cd", "mkdir", "touch", "rm"],
    "Gestione dei Processi": ["ps", "top", "kill"],
}

for categoria, comandi in categorie.items():
    submenu = tk.Menu(menu, tearoff=0)
    for comando in comandi:
        submenu.add_command(label=comando, command=lambda cmd=comando: mostra_selettore_flag(cmd))
    menu.add_cascade(label=categoria, menu=submenu)

frame_input = tk.Frame(root)
frame_input.pack(pady=10, padx=10, fill=tk.X)

label_comando = tk.Label(frame_input, text="Comando:")
label_comando.pack(side=tk.LEFT, padx=5)

input_comando = tk.Entry(frame_input, width=60)
input_comando.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

pulsante_esegui = tk.Button(frame_input, text="Esegui", command=esegui_comando)
pulsante_esegui.pack(side=tk.LEFT, padx=5)

pulsante_spiega = tk.Button(frame_input, text="Spiega", command=spiega_comando)
pulsante_spiega.pack(side=tk.LEFT, padx=5)

pulsante_interrompi = tk.Button(frame_input, text="Interrompi", command=interrompi_comando, bg="red", fg="white")
pulsante_interrompi.pack(side=tk.LEFT, padx=5)

frame_output = tk.Frame(root)
frame_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

label_output = tk.Label(frame_output, text="Output:")
label_output.pack(anchor="w")

output_text = tk.Text(frame_output, height=15)
output_text.pack(fill=tk.BOTH, expand=True)

frame_spiegazione = tk.Frame(root)
frame_spiegazione.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

label_spiegazione = tk.Label(frame_spiegazione, text="Spiegazione:")
label_spiegazione.pack(anchor="w")

spiegazione_text = tk.Text(frame_spiegazione, height=15, bg="#f4f4f4")
spiegazione_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
