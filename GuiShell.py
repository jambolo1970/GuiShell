import os
import subprocess
import tkinter as tk
from tkinter import Toplevel, Checkbutton, IntVar, filedialog, messagebox
import shlex
from googletrans import Translator
from threading import Thread

translator = Translator()

# Categorie dei comandi con relativi flag
comandi_e_flag = {
    "ls": ["-l (dettagliato)", "-a (includi file nascosti)", "-h (dimensioni leggibili)"],
    "pwd": [],
    "cd": [],  # Cambio directory
    "mkdir": ["-p (crea directory annidate)"],
    "rm": ["-r (ricorsivo)", "-f (forza eliminazione)"],
    "mv": [],
    "cp": ["-r (ricorsivo)", "-f (forza copia)"],
    "chmod": ["-R (ricorsivo)", "+x (aggiungi eseguibilità)", "u+w (aggiungi scrittura utente)"],
    "chown": ["-R (ricorsivo)"],
    "chgrp": ["-R (ricorsivo)"],
    "ps": ["-e (tutti i processi)", "-f (formato completo)", "-u (specifica utente)"],
    "top": [],
    "kill": ["-9 (terminazione forzata)"],
    "jobs": [],
    "tar": ["-c (crea archivio)", "-x (estrae archivio)", "-z (compressione gzip)"],
    "zip": ["-r (ricorsivo)"],
    "unzip": ["-o (sovrascrivi senza chiedere)", "-l (elenca contenuto)"],
    "gzip": [],
    "find": ["-name (cerca per nome)", "-type d (cerca directory)", "-size +1M (file > 1MB)"],
    "locate": [],
    "grep": ["-i (ignora maiuscole/minuscole)", "-r (ricorsivo)", "-v (inversa)"],
    "df": ["-h (spazio leggibile)", "-T (mostra tipo filesystem)", "-i (informazioni inode)"],
    "du": ["-h (dimensioni leggibili)", "-s (sommario)"],
    "mount": [],
    "umount": [],
    "ping": ["-c 4 (numero pacchetti)", "-i 0.2 (intervallo secondi)", "-s 64 (dimensione pacchetto)"],
    "wget": ["--quiet (silenzioso)", "--limit-rate=100k (limita velocità)", "-O (file di output)"],
    "curl": ["-X POST (metodo HTTP)", "-d (dati corpo richiesta)"],
    "ifconfig": [],
    "who": [],
    "whoami": [],
    "id": [],
    "adduser": ["-m (crea home directory)", "-s /bin/bash (specifica shell)"],
    "apt": ["update (aggiorna pacchetti)", "upgrade (aggiorna sistema)"],
    "yum": ["install (installa pacchetti)", "remove (rimuove pacchetti)"],
    "pacman": ["-S (installa pacchetti)", "-R (rimuove pacchetti)"],
    "snap": ["install (installa pacchetti)", "remove (rimuove pacchetti)"],
    "dmesg": [],
    "uptime": [],
    "free": ["-h (formato leggibile)"],
    "vmstat": [],
    "bash": [],
    "python": [],
    "gcc": ["-o (specifica file output)"],
    "make": [],
    "alias": [],
    "unalias": [],
    "history": [],
    "echo": [],
    "clear": [],
    "smbclient": ["-L (elenca risorse condivise)", "-U (specifica utente)", "-N (senza autenticazione)"],
    "testparm": ["-v (output dettagliato)", "--suppress-prompt (sopprime domande)"],
    "smbpasswd": ["-a (aggiunge utente)", "-x (rimuove utente)"],
    "nmblookup": ["-A (esegue una ricerca avanzata)", "-R (forza interrogazione broadcast)"],
}

simulazione_in_corso = False
processo_corrente = None


def mostra_selettore_flag(comando):
    """Mostra una finestra per selezionare i flag e inserire parametri aggiuntivi per il comando."""
    top = Toplevel(root)
    top.title(f"Configura opzioni per {comando}")
    top.geometry("500x400")

    label = tk.Label(top, text=f"Configura il comando '{comando}':")
    label.pack(pady=10)

    variabili_flag = []
    entry_parametro = None

    def applica_configurazione():
        """Costruisce il comando con flag e parametri personalizzati."""
        global simulazione_in_corso
        if simulazione_in_corso:
            messagebox.showwarning("Attenzione", "Un comando è già in esecuzione!")
            return

        # Costruisce i flag
        flag_selezionati = []
        for var, flag in variabili_flag:
            if var.get():
                flag_selezionati.append(flag.split()[0])

        # Recupera eventuali parametri
        parametri = entry_parametro.get().strip() if entry_parametro else ""

        # Costruisce il comando completo
        comando_completo = f"{comando} {' '.join(flag_selezionati)} {parametri}"
        input_comando.delete(0, tk.END)
        input_comando.insert(0, comando_completo)
        top.destroy()

    # Crea i checkbox per i flag
    for flag in comandi_e_flag.get(comando, []):
        var = IntVar()
        chk = Checkbutton(top, text=flag, variable=var)
        chk.pack(anchor="w")
        variabili_flag.append((var, flag))

    # Aggiunge un campo per i parametri aggiuntivi
    label_parametro = tk.Label(top, text="Inserisci parametri aggiuntivi (es. nome file, directory, ecc.):")
    label_parametro.pack(pady=5)
    entry_parametro = tk.Entry(top, width=40)
    entry_parametro.pack(pady=5)

    btn_applica = tk.Button(top, text="Applica Configurazione", command=applica_configurazione)
    btn_applica.pack(pady=10)


def esegui_comando():
    """Esegue il comando e mostra il risultato."""
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
    """Interrompe l'esecuzione del comando."""
    global simulazione_in_corso, processo_corrente
    if simulazione_in_corso and processo_corrente:
        processo_corrente.terminate()
        output_text.insert(tk.END, "Comando interrotto.\n")
        simulazione_in_corso = False
        processo_corrente = None
    else:
        messagebox.showinfo("Informazione", "Nessun comando in esecuzione.")


def spiega_comando():
    """Mostra una spiegazione del comando e la traduce in italiano."""
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
    "Permessi e Proprietà": ["chmod", "chown", "chgrp"],
    "Gestione dei Processi": ["ps", "top", "kill", "jobs"],
    "Compressione e Archiviazione": ["tar", "zip", "unzip", "gzip"],
    "Ricerca": ["find", "locate", "grep"],
    "Gestione del Disco": ["df", "du", "mount", "umount"],
    "Rete": ["ping", "wget", "curl", "ifconfig"],
    "Gestione Utenti": ["who", "whoami", "id", "adduser"],
    "Gestione Pacchetti": ["apt", "yum", "pacman", "snap"],
    "Monitoraggio": ["dmesg", "uptime", "free", "vmstat"],
    "Programmazione e Scripting": ["bash", "python", "gcc", "make"],
    "Comandi Utili": ["alias", "unalias", "history", "echo", "clear"],
    "Comandi Samba": ["smbclient", "testparm", "smbpasswd", "nmblookup"]
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
