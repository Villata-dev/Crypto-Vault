import os
import base64
import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- LÓGICA CRIPTOGRÁFICA (Intacta, grado militar) ---

def generar_llave_desde_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# --- INTERFAZ GRÁFICA V2 (PRO) ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración principal de la ventana
        self.title("Crypto-Vault | Advanced Security")
        self.geometry("500x620")
        self.resizable(False, False)
        
        # Tema visual moderno
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ruta_archivo = None

        # --- CONTENEDOR PRINCIPAL (Efecto Tarjeta) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 1. CABECERA
        self.lbl_icono = ctk.CTkLabel(self.main_frame, text="🛡️", font=ctk.CTkFont(size=40))
        self.lbl_icono.pack(pady=(20, 5))
        
        self.lbl_titulo = ctk.CTkLabel(self.main_frame, text="CRYPTO-VAULT", font=ctk.CTkFont(size=24, weight="bold", letter_spacing=2))
        self.lbl_titulo.pack()
        
        self.lbl_subtitulo = ctk.CTkLabel(self.main_frame, text="Cifrado AES-256 PBKDF2", text_color="#7F8C8D", font=ctk.CTkFont(size=12))
        self.lbl_subtitulo.pack(pady=(0, 20))

        # 2. SECCIÓN DE ARCHIVO (Sub-tarjeta)
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_file_title = ctk.CTkLabel(self.file_frame, text="1. Selección de Archivo", font=ctk.CTkFont(weight="bold"))
        self.lbl_file_title.pack(pady=(10, 5))

        self.btn_seleccionar = ctk.CTkButton(self.file_frame, text="📂 Explorar Sistema...", command=self.seleccionar_archivo, fg_color="#2980B9", hover_color="#1A5276")
        self.btn_seleccionar.pack(pady=5)

        self.lbl_archivo = ctk.CTkLabel(self.file_frame, text="Ningún archivo seleccionado", text_color="#BDC3C7", wraplength=400, font=ctk.CTkFont(slant="italic"))
        self.lbl_archivo.pack(pady=(5, 10))

        # 3. SECCIÓN DE SEGURIDAD (Sub-tarjeta)
        self.security_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        self.security_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_sec_title = ctk.CTkLabel(self.security_frame, text="2. Credenciales de Acceso", font=ctk.CTkFont(weight="bold"))
        self.lbl_sec_title.pack(pady=(10, 5))

        self.entrada_password = ctk.CTkEntry(self.security_frame, placeholder_text="Contraseña maestra", show="*", width=250, height=35)
        self.entrada_password.pack(pady=5)

        # Toggle para mostrar/ocultar contraseña
        self.chk_mostrar_pass = ctk.CTkCheckBox(self.security_frame, text="Mostrar contraseña", font=ctk.CTkFont(size=11), command=self.toggle_password, checkbox_width=18, checkbox_height=18)
        self.chk_mostrar_pass.pack(pady=(5, 10))

        # 4. SECCIÓN DE ACCIÓN (Botones)
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(pady=20)

        self.btn_cifrar = ctk.CTkButton(self.action_frame, text="🔒 Cifrar", fg_color="#C0392B", hover_color="#922B21", font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.cifrar)
        self.btn_cifrar.grid(row=0, column=0, padx=10)

        self.btn_descifrar = ctk.CTkButton(self.action_frame, text="🔓 Descifrar", fg_color="#27AE60", hover_color="#1E8449", font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.descifrar)
        self.btn_descifrar.grid(row=0, column=1, padx=10)

        # 5. BARRA DE ESTADO (Footer)
        self.lbl_estado = ctk.CTkLabel(self, text="Estado: Esperando acción...", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_estado.pack(side="bottom", pady=10)

    # --- FUNCIONES DE LA INTERFAZ ---

    def toggle_password(self):
        # Muestra u oculta los asteriscos de la contraseña
        if self.chk_mostrar_pass.get() == 1:
            self.entrada_password.configure(show="")
        else:
            self.entrada_password.configure(show="*")

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo")
        if ruta:
            self.ruta_archivo = ruta
            nombre_corto = os.path.basename(ruta)
            self.lbl_archivo.configure(text=nombre_corto, text_color="#F1C40F") # Amarillo para destacar
            self.lbl_estado.configure(text="Estado: Archivo cargado en memoria.")

    def cifrar(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Aviso", "Selecciona un archivo primero.")
            return
        
        password = self.entrada_password.get()
        if not password:
            messagebox.showwarning("Aviso", "Ingresa una contraseña maestra.")
            return

        try:
            self.lbl_estado.configure(text="Estado: Cifrando archivo...")
            self.update() # Fuerza a la interfaz a actualizar el texto

            salt = os.urandom(16)
            llave = generar_llave_desde_password(password, salt)
            f = Fernet(llave)

            with open(self.ruta_archivo, "rb") as archivo:
                datos_originales = archivo.read()

            datos_cifrados = f.encrypt(datos_originales)
            nuevo_nombre = self.ruta_archivo + ".enc"
            
            with open(nuevo_nombre, "wb") as archivo_cifrado:
                archivo_cifrado.write(salt + datos_cifrados)
            
            os.remove(self.ruta_archivo)
            
            self.limpiar_ui()
            self.lbl_estado.configure(text="Estado: Archivo protegido exitosamente.", text_color="#27AE60")
            messagebox.showinfo("Bóveda Segura", "El archivo ha sido encriptado con éxito.")
            
        except Exception as e:
            self.lbl_estado.configure(text="Estado: Error crítico.", text_color="#C0392B")
            messagebox.showerror("Error", f"Ocurrió un error al cifrar: {str(e)}")

    def descifrar(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Aviso", "Selecciona un archivo primero.")
            return
        
        if not self.ruta_archivo.endswith(".enc"):
            messagebox.showerror("Error", "Debes seleccionar un archivo cifrado (.enc).")
            return

        password = self.entrada_password.get()
        if not password:
            messagebox.showwarning("Aviso", "Ingresa la contraseña para descifrar.")
            return

        try:
            self.lbl_estado.configure(text="Estado: Descifrando archivo...")
            self.update()

            with open(self.ruta_archivo, "rb") as archivo_cifrado:
                contenido = archivo_cifrado.read()

            salt = contenido[:16]
            datos_cifrados = contenido[16:]

            llave = generar_llave_desde_password(password, salt)
            f = Fernet(llave)

            datos_descifrados = f.decrypt(datos_cifrados)

            nombre_original = self.ruta_archivo.replace(".enc", "")
            with open(nombre_original, "wb") as archivo_descifrado:
                archivo_descifrado.write(datos_descifrados)

            os.remove(self.ruta_archivo)
            
            self.limpiar_ui()
            self.lbl_estado.configure(text="Estado: Archivo restaurado exitosamente.", text_color="#27AE60")
            messagebox.showinfo("Acceso Concedido", "El archivo ha sido desencriptado y restaurado.")

        except Exception:
            self.lbl_estado.configure(text="Estado: Acceso denegado.", text_color="#C0392B")
            messagebox.showerror("Bloqueo de Seguridad", "Contraseña incorrecta o el archivo está corrupto.")

    def limpiar_ui(self):
        """Restablece los campos de la interfaz a su estado original."""
        self.ruta_archivo = None
        self.lbl_archivo.configure(text="Ningún archivo seleccionado", text_color="#BDC3C7")
        self.entrada_password.delete(0, 'end')
        self.chk_mostrar_pass.deselect()
        self.entrada_password.configure(show="*")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()