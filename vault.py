import os
import base64
import threading
import string
import secrets
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

# --- INTERFAZ GRÁFICA V3.2 (CYBER-TERMINAL + FIX DE ESPACIADO) ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto-Vault | Grado Militar")
        self.geometry("500x680")
        self.resizable(False, False)
        
        self.configure(fg_color="#0B0E14")
        ctk.set_appearance_mode("dark")

        self.ruta_archivo = None

        self.font_title = ctk.CTkFont(family="Consolas", size=26, weight="bold")
        self.font_bold = ctk.CTkFont(family="Consolas", size=13, weight="bold")
        self.font_mono = ctk.CTkFont(family="Consolas", size=12)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#151A22", corner_radius=4, border_width=1, border_color="#2A3241")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 1. CABECERA (Alineación perfecta anti-bugs de espaciado)
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(pady=(30, 5))

        self.lbl_corchete_izq = ctk.CTkLabel(self.title_frame, text="[ ", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_izq.pack(side="left")

        # Usamos una fuente genérica solo para el emoji para que no se rompa el espaciado
        self.lbl_escudo = ctk.CTkLabel(self.title_frame, text="🛡️ ", font=ctk.CTkFont(size=22)) 
        self.lbl_escudo.pack(side="left", pady=(0, 2))
        
        self.lbl_texto = ctk.CTkLabel(self.title_frame, text="CRYPTO-VAULT", font=self.font_title, text_color="#00E5FF")
        self.lbl_texto.pack(side="left")

        self.lbl_corchete_der = ctk.CTkLabel(self.title_frame, text=" ]", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_der.pack(side="left")
        
        self.lbl_subtitulo = ctk.CTkLabel(self.main_frame, text="MOTOR AES-256 // PBKDF2", text_color="#5C6B89", font=self.font_mono)
        self.lbl_subtitulo.pack(pady=(0, 25))

        # --- SECCIÓN DE ARCHIVO ---
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E2430", corner_radius=2)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_file_title = ctk.CTkLabel(self.file_frame, text="[ TARGET FILE ]", font=self.font_bold, text_color="#8B9BB4")
        self.lbl_file_title.pack(pady=(15, 5))

        self.btn_seleccionar = ctk.CTkButton(self.file_frame, text="Explorar Directorio", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#3B82F6", text_color="#3B82F6", hover_color="#1E3A8A", corner_radius=2, command=self.seleccionar_archivo)
        self.btn_seleccionar.pack(pady=10)

        self.lbl_archivo = ctk.CTkLabel(self.file_frame, text=">_ Esperando archivo...", text_color="#4B5563", font=self.font_mono, wraplength=400)
        self.lbl_archivo.pack(pady=(0, 15))

        # --- SECCIÓN DE SEGURIDAD ---
        self.security_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E2430", corner_radius=2)
        self.security_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_sec_title = ctk.CTkLabel(self.security_frame, text="[ SECURITY KEY ]", font=self.font_bold, text_color="#8B9BB4")
        self.lbl_sec_title.pack(pady=(15, 5))

        self.pass_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.pass_frame.pack(pady=5)

        self.entrada_password = ctk.CTkEntry(self.pass_frame, placeholder_text="Ingresa master_key", show="*", width=200, height=35, font=self.font_mono, fg_color="#0F1219", border_color="#374151", corner_radius=2)
        self.entrada_password.grid(row=0, column=0, padx=(0, 10))

        self.btn_generar = ctk.CTkButton(self.pass_frame, text="⚡ Generar", width=90, height=35, font=self.font_bold, fg_color="transparent", border_width=1, border_color="#8B5CF6", text_color="#8B5CF6", hover_color="#4C1D95", corner_radius=2, command=self.generar_password)
        self.btn_generar.grid(row=0, column=1)

        self.chk_mostrar_pass = ctk.CTkCheckBox(self.security_frame, text="Visibilidad", font=self.font_mono, text_color="#9CA3AF", fg_color="#00E5FF", hover_color="#00B3CC", corner_radius=2, checkbox_width=16, checkbox_height=16, border_width=1, command=self.toggle_password)
        self.chk_mostrar_pass.pack(pady=(10, 15))

        # --- SECCIÓN DE ACCIÓN (Botones Ghost/Outline) ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(pady=25)

        # Botón Encriptar
        self.btn_cifrar = ctk.CTkButton(self.action_frame, text="[ 🔒 ENCRIPTAR ]", fg_color="transparent", border_width=1, border_color="#EF4444", text_color="#EF4444", hover_color="#7F1D1D", font=self.font_bold, width=150, height=42, corner_radius=2, command=self.iniciar_cifrado)
        self.btn_cifrar.grid(row=0, column=0, padx=10)

        # Botón Desencriptar
        self.btn_descifrar = ctk.CTkButton(self.action_frame, text="[ 🔓 DESENCRIPTAR ]", fg_color="transparent", border_width=1, border_color="#10B981", text_color="#10B981", hover_color="#064E3B", font=self.font_bold, width=150, height=42, corner_radius=2, command=self.iniciar_descifrado)
        self.btn_descifrar.grid(row=0, column=1, padx=10)

        # --- BARRA DE PROGRESO ---
        self.progressbar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", width=350, progress_color="#00E5FF", fg_color="#1E2430")
        self.progressbar.set(0)

        # --- BARRA DE ESTADO ---
        self.lbl_estado = ctk.CTkLabel(self, text="SYS_STATUS: INACTIVO", text_color="#4B5563", font=self.font_mono)
        self.lbl_estado.pack(side="bottom", pady=15)

    # --- FUNCIONES DE LA INTERFAZ ---

    def generar_password(self):
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_+="
        password_segura = ''.join(secrets.choice(caracteres) for _ in range(16))
        
        self.entrada_password.delete(0, 'end')
        self.entrada_password.insert(0, password_segura)
        
        self.chk_mostrar_pass.select()
        self.entrada_password.configure(show="")
        self.lbl_estado.configure(text="SYS_STATUS: KEY GENERADA. GUARDAR EN LUGAR SEGURO.", text_color="#F59E0B")

    def toggle_password(self):
        if self.chk_mostrar_pass.get() == 1:
            self.entrada_password.configure(show="")
        else:
            self.entrada_password.configure(show="*")

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo target")
        if ruta:
            self.ruta_archivo = ruta
            nombre_corto = os.path.basename(ruta)
            self.lbl_archivo.configure(text=f">_ {nombre_corto}", text_color="#00E5FF")
            self.lbl_estado.configure(text="SYS_STATUS: TARGET ADQUIRIDO.")

    def bloquear_ui(self, bloqueado: bool):
        estado = "disabled" if bloqueado else "normal"
        self.btn_cifrar.configure(state=estado)
        self.btn_descifrar.configure(state=estado)
        self.btn_seleccionar.configure(state=estado)
        self.btn_generar.configure(state=estado)

    # --- LÓGICA DE HILOS PARA CIFRADO ---
    def iniciar_cifrado(self):
        if not self.validar_entradas(): return
        
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: ENCRIPTANDO DATOS...", text_color="#00E5FF")
        
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
            self.after(500, self.finalizar_operacion, "ENCRIPTADO", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "ERROR", False, str(e))

    # --- LÓGICA DE HILOS PARA DESCIFRADO ---
    def iniciar_descifrado(self):
        if not self.validar_entradas(es_descifrado=True): return

        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: VALIDANDO CREDENCIALES...", text_color="#00E5FF")

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
            self.after(500, self.finalizar_operacion, "DESENCRIPTADO", True, "")
        except Exception:
            self.after(500, self.finalizar_operacion, "ERROR", False, "ACCESO DENEGADO: Clave incorrecta.")

    def finalizar_operacion(self, operacion, exito, error_msg):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.bloquear_ui(False)

        if exito:
            self.limpiar_ui()
            self.lbl_estado.configure(text=f"SYS_STATUS: {operacion} EXITOSAMENTE.", text_color="#10B981")
            messagebox.showinfo("SYS_MSG", f"Operación completada: Archivo {operacion.lower()}.")
        else:
            self.lbl_estado.configure(text="SYS_STATUS: ACCESO DENEGADO / CORRUPCIÓN", text_color="#DC2626")
            messagebox.showerror("SYS_ERR", error_msg)

    def validar_entradas(self, es_descifrado=False):
        if not self.ruta_archivo:
            messagebox.showwarning("SYS_WARN", "Target no seleccionado.")
            return False
        if es_descifrado and not self.ruta_archivo.endswith(".enc"):
            messagebox.showerror("SYS_ERR", "Formato inválido. Se requiere archivo .enc")
            return False
        if not self.entrada_password.get():
            messagebox.showwarning("SYS_WARN", "Se requiere master_key.")
            return False
        return True

    def limpiar_ui(self):
        self.ruta_archivo = None
        self.lbl_archivo.configure(text=">_ Esperando archivo...", text_color="#4B5563")
        self.entrada_password.delete(0, 'end')
        self.chk_mostrar_pass.deselect()
        self.entrada_password.configure(show="*")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()