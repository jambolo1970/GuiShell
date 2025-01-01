#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import shlex
from googletrans import Translator  # Modulo per la traduzione
import difflib  # Per suggerire comandi simili

translator = Translator()  # Inizializza il traduttore

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
    # Recupera la lista dei comandi validi dal sistema
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
            # Traduzione in italiano
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
            return  # Utente ha annullato l'operazione
        
        # Determina quale sezione salvare
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
root.geometry("800x700")

# Barra dei menu
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Salva Output", command=salva_output)
file_menu.add_separator()
file_menu.add_command(label="Esci", command=root.quit)
menu.add_cascade(label="File", menu=file_menu)

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
