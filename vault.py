import os
import base64
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- LÓGICA CRIPTOGRÁFICA ---

def generar_llave_desde_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# --- INTERFAZ GRÁFICA V2.1 (CON BARRA DE PROGRESO) ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto-Vault | Advanced Security")
        self.geometry("500x650") # Aumenté un poco el alto para la barra
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ruta_archivo = None

        # --- CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.lbl_icono = ctk.CTkLabel(self.main_frame, text="🛡️", font=ctk.CTkFont(size=40))
        self.lbl_icono.pack(pady=(20, 5))
        
        self.lbl_titulo = ctk.CTkLabel(self.main_frame, text="CRYPTO-VAULT", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_titulo.pack()
        
        self.lbl_subtitulo = ctk.CTkLabel(self.main_frame, text="Cifrado AES-256 PBKDF2", text_color="#7F8C8D", font=ctk.CTkFont(size=12))
        self.lbl_subtitulo.pack(pady=(0, 20))

        # --- SECCIÓN DE ARCHIVO ---
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_file_title = ctk.CTkLabel(self.file_frame, text="1. Selección de Archivo", font=ctk.CTkFont(weight="bold"))
        self.lbl_file_title.pack(pady=(10, 5))

        self.btn_seleccionar = ctk.CTkButton(self.file_frame, text="📂 Explorar Sistema...", command=self.seleccionar_archivo, fg_color="#2980B9", hover_color="#1A5276")
        self.btn_seleccionar.pack(pady=5)

        self.lbl_archivo = ctk.CTkLabel(self.file_frame, text="Ningún archivo seleccionado", text_color="#BDC3C7", wraplength=400, font=ctk.CTkFont(slant="italic"))
        self.lbl_archivo.pack(pady=(5, 10))

        # --- SECCIÓN DE SEGURIDAD ---
        self.security_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        self.security_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_sec_title = ctk.CTkLabel(self.security_frame, text="2. Credenciales de Acceso", font=ctk.CTkFont(weight="bold"))
        self.lbl_sec_title.pack(pady=(10, 5))

        self.entrada_password = ctk.CTkEntry(self.security_frame, placeholder_text="Contraseña maestra", show="*", width=250, height=35)
        self.entrada_password.pack(pady=5)

        self.chk_mostrar_pass = ctk.CTkCheckBox(self.security_frame, text="Mostrar contraseña", font=ctk.CTkFont(size=11), command=self.toggle_password, checkbox_width=18, checkbox_height=18)
        self.chk_mostrar_pass.pack(pady=(5, 10))

        # --- SECCIÓN DE ACCIÓN ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(pady=20)

        self.btn_cifrar = ctk.CTkButton(self.action_frame, text="🔒 Cifrar", fg_color="#C0392B", hover_color="#922B21", font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.iniciar_cifrado)
        self.btn_cifrar.grid(row=0, column=0, padx=10)

        self.btn_descifrar = ctk.CTkButton(self.action_frame, text="🔓 Descifrar", fg_color="#27AE60", hover_color="#1E8449", font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.iniciar_descifrado)
        self.btn_descifrar.grid(row=0, column=1, padx=10)

        # --- BARRA DE PROGRESO (Oculta por defecto) ---
        self.progressbar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", width=350)
        self.progressbar.set(0)

        # --- BARRA DE ESTADO ---
        self.lbl_estado = ctk.CTkLabel(self, text="Estado: Esperando acción...", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_estado.pack(side="bottom", pady=10)

    # --- FUNCIONES DE LA INTERFAZ ---

    def toggle_password(self):
        if self.chk_mostrar_pass.get() == 1:
            self.entrada_password.configure(show="")
        else:
            self.entrada_password.configure(show="*")

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo")
        if ruta:
            self.ruta_archivo = ruta
            nombre_corto = os.path.basename(ruta)
            self.lbl_archivo.configure(text=nombre_corto, text_color="#F1C40F")
            self.lbl_estado.configure(text="Estado: Archivo cargado en memoria.")

    def bloquear_ui(self, bloqueado: bool):
        """Desactiva los botones mientras la barra de progreso se mueve"""
        estado = "disabled" if bloqueado else "normal"
        self.btn_cifrar.configure(state=estado)
        self.btn_descifrar.configure(state=estado)
        self.btn_seleccionar.configure(state=estado)

    # --- LÓGICA DE HILOS PARA CIFRADO ---
    def iniciar_cifrado(self):
        if not self.validar_entradas(): return
        
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 10)) # Mostramos la barra
        self.progressbar.start() # Animamos la barra
        self.lbl_estado.configure(text="Estado: Ejecutando cifrado militar en segundo plano...", text_color="white")
        
        # Lanzamos el trabajo pesado en un hilo separado
        threading.Thread(target=self.tarea_cifrar, args=(self.ruta_archivo, self.entrada_password.get()), daemon=True).start()

    def tarea_cifrar(self, ruta, password):
        try:
            salt = os.urandom(16)
            llave = generar_llave_desde_password(password, salt)
            f = Fernet(llave)

            with open(ruta, "rb") as archivo:
                datos_originales = archivo.read()

            datos_cifrados = f.encrypt(datos_originales)
            nuevo_nombre = ruta + ".enc"
            
            with open(nuevo_nombre, "wb") as archivo_cifrado:
                archivo_cifrado.write(salt + datos_cifrados)
            
            os.remove(ruta)
            
            # .after permite actualizar la UI desde un hilo secundario de forma segura
            self.after(500, self.finalizar_operacion, "Cifrado", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "Cifrado", False, str(e))

    # --- LÓGICA DE HILOS PARA DESCIFRADO ---
    def iniciar_descifrado(self):
        if not self.validar_entradas(es_descifrado=True): return

        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 10))
        self.progressbar.start()
        self.lbl_estado.configure(text="Estado: Validando credenciales y descifrando...", text_color="white")

        threading.Thread(target=self.tarea_descifrar, args=(self.ruta_archivo, self.entrada_password.get()), daemon=True).start()

    def tarea_descifrar(self, ruta, password):
        try:
            with open(ruta, "rb") as archivo_cifrado:
                contenido = archivo_cifrado.read()

            salt = contenido[:16]
            datos_cifrados = contenido[16:]

            llave = generar_llave_desde_password(password, salt)
            f = Fernet(llave)

            datos_descifrados = f.decrypt(datos_cifrados)

            nombre_original = ruta.replace(".enc", "")
            with open(nombre_original, "wb") as archivo_descifrado:
                archivo_descifrado.write(datos_descifrados)

            os.remove(ruta)
            self.after(500, self.finalizar_operacion, "Descifrado", True, "")
        except Exception:
            self.after(500, self.finalizar_operacion, "Descifrado", False, "Contraseña incorrecta o el archivo está corrupto.")

    def finalizar_operacion(self, operacion, exito, error_msg):
        """Detiene la barra de progreso y restaura la interfaz"""
        self.progressbar.stop()
        self.progressbar.pack_forget() # Ocultamos la barra
        self.bloquear_ui(False)

        if exito:
            self.limpiar_ui()
            self.lbl_estado.configure(text=f"Estado: Archivo {operacion.lower()} exitosamente.", text_color="#27AE60")
            messagebox.showinfo("Operación Exitosa", f"El archivo ha sido {operacion.lower()} con éxito.")
        else:
            self.lbl_estado.configure(text="Estado: Error crítico / Acceso denegado.", text_color="#C0392B")
            messagebox.showerror("Error", error_msg)

    def validar_entradas(self, es_descifrado=False):
        if not self.ruta_archivo:
            messagebox.showwarning("Aviso", "Selecciona un archivo primero.")
            return False
        if es_descifrado and not self.ruta_archivo.endswith(".enc"):
            messagebox.showerror("Error", "Debes seleccionar un archivo cifrado (.enc).")
            return False
        if not self.entrada_password.get():
            messagebox.showwarning("Aviso", "Ingresa una contraseña maestra.")
            return False
        return True

    def limpiar_ui(self):
        self.ruta_archivo = None
        self.lbl_archivo.configure(text="Ningún archivo seleccionado", text_color="#BDC3C7")
        self.entrada_password.delete(0, 'end')
        self.chk_mostrar_pass.deselect()
        self.entrada_password.configure(show="*")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()