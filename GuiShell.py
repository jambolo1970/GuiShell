#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import shlex
from googletrans import Translator
import difflib

translator = Translator()

def esegui_comando_diretto(comando):
    """Esegue un comando diretto dal menu."""
    input_comando.delete(0, tk.END)  # Pulisce l'input
    input_comando.insert(0, comando)  # Inserisce il comando
    esegui_comando()

def esegui_comando():
    """Esegue il comando e mostra il risultato."""
    comando = input_comando.get()
    if not comando.strip():
        messagebox.showwarning("Attenzione", "Inserire un comando!")
        return
    
    try:
        args = shlex.split(comando)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result.stdout or result.stderr)
    except FileNotFoundError:
        suggerisci_comandi(comando.split()[0])
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'esecuzione: {e}")

def suggerisci_comandi(comando_errato):
    """Suggerisce comandi simili in caso di errore."""
    try:
        comandi = subprocess.run("compgen -c", shell=True, stdout=subprocess.PIPE, text=True).stdout.splitlines()
        suggerimenti = difflib.get_close_matches(comando_errato, comandi, n=5, cutoff=0.6)
        if suggerimenti:
            suggerimenti_str = "\n".join(suggerimenti)
            messagebox.showinfo("Suggerimenti", f"Comando non trovato.\nForse intendevi:\n{suggestioni_str}")
        else:
            messagebox.showinfo("Suggerimenti", f"Nessun comando simile trovato per: {comando_errato}")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la ricerca di suggerimenti: {e}")

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

def salva_output():
    """Salva l'output o la spiegazione in un file di testo."""
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")]
        )
        if not file_path:
            return
        
        contenuto_output = output_text.get("1.0", tk.END).strip()
        contenuto_spiegazione = spiegazione_text.get("1.0", tk.END).strip()
        
        with open(file_path, "w", encoding="utf-8") as file:
            if contenuto_output:
                file.write("Output del comando:\n")
                file.write(contenuto_output)
                file.write("\n\n")
            if contenuto_spiegazione:
                file.write("Spiegazione del comando:\n")
                file.write(contenuto_spiegazione)
        
        messagebox.showinfo("Successo", f"File salvato in: {file_path}")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante il salvataggio: {e}")

def mostra_info():
    """Mostra informazioni sull'applicazione."""
    messagebox.showinfo("Informazioni", "Shell Grafica Linux\nVersione 1.0\nCreato con Python e Tkinter")

# Creazione finestra principale
root = tk.Tk()
root.title("Shell Grafica Linux")
root.geometry("900x800")

# Barra dei menu
menu = tk.Menu(root)
root.config(menu=menu)

# Funzione per aggiungere menu dinamicamente
def aggiungi_categoria_menu(titolo, comandi):
    """Aggiunge una categoria e i suoi comandi al menu."""
    submenu = tk.Menu(menu, tearoff=0)
    for comando in comandi:
        submenu.add_command(label=comando, command=lambda cmd=comando: esegui_comando_diretto(cmd))
    menu.add_cascade(label=titolo, menu=submenu)

# Categorie e comandi
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
    "Comandi Utili": ["alias", "unalias", "history", "echo", "clear"]
}

# Aggiungi le categorie al menu
for categoria, comandi in categorie.items():
    aggiungi_categoria_menu(categoria, comandi)

# Menu Aiuto
help_menu = tk.Menu(menu, tearoff=0)
help_menu.add_command(label="Informazioni", command=mostra_info)
menu.add_cascade(label="Aiuto", menu=help_menu)

# Input del comando
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

# Output dell'esecuzione
frame_output = tk.Frame(root)
frame_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

label_output = tk.Label(frame_output, text="Output:")
label_output.pack(anchor="w")

output_text = tk.Text(frame_output, height=15)
output_text.pack(fill=tk.BOTH, expand=True)

# Spiegazione del comando
frame_spiegazione = tk.Frame(root)
frame_spiegazione.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

label_spiegazione = tk.Label(frame_spiegazione, text="Spiegazione:")
label_spiegazione.pack(anchor="w")

spiegazione_text = tk.Text(frame_spiegazione, height=15, bg="#f4f4f4")
spiegazione_text.pack(fill=tk.BOTH, expand=True)

# Avvia la finestra principale
root.mainloop()
