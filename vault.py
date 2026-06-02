import os
import base64
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

# --- INTERFAZ GRÁFICA ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title("Crypto-Vault | Bóveda AES-256")
        self.geometry("450x450")
        self.resizable(False, False)
        
        # Tema visual moderno y oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables de estado
        self.ruta_archivo = None

        # --- DISEÑO DE LA INTERFAZ (UI) ---
        
        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="🛡️ CRYPTO-VAULT", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 5))
        
        self.lbl_subtitulo = ctk.CTkLabel(self, text="Cifrado de Grado Militar", text_color="gray")
        self.lbl_subtitulo.pack(pady=(0, 20))

        # Botón para buscar archivo
        self.btn_seleccionar = ctk.CTkButton(self, text="📂 Seleccionar Archivo", command=self.seleccionar_archivo)
        self.btn_seleccionar.pack(pady=10)

        # Etiqueta para mostrar el archivo seleccionado
        self.lbl_archivo = ctk.CTkLabel(self, text="Ningún archivo seleccionado", text_color="gray", wraplength=400)
        self.lbl_archivo.pack(pady=(0, 20))

        # Campo de Contraseña
        self.entrada_password = ctk.CTkEntry(self, placeholder_text="Contraseña maestra", show="*", width=250)
        self.entrada_password.pack(pady=10)

        # Botones de Acción
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=20)

        self.btn_cifrar = ctk.CTkButton(self.frame_botones, text="🔒 Cifrar Archivo", fg_color="#C0392B", hover_color="#922B21", command=self.cifrar)
        self.btn_cifrar.grid(row=0, column=0, padx=10)

        self.btn_descifrar = ctk.CTkButton(self.frame_botones, text="🔓 Descifrar Archivo", fg_color="#27AE60", hover_color="#1E8449", command=self.descifrar)
        self.btn_descifrar.grid(row=0, column=1, padx=10)

    # --- FUNCIONES DE LA INTERFAZ ---

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo")
        if ruta:
            self.ruta_archivo = ruta
            nombre_corto = os.path.basename(ruta)
            self.lbl_archivo.configure(text=f"Seleccionado: {nombre_corto}", text_color="white")

    def cifrar(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar un archivo.")
            return
        
        password = self.entrada_password.get()
        if not password:
            messagebox.showwarning("Advertencia", "Debes ingresar una contraseña.")
            return

        try:
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
            
            # Limpiar la UI
            self.ruta_archivo = None
            self.lbl_archivo.configure(text="Ningún archivo seleccionado", text_color="gray")
            self.entrada_password.delete(0, 'end')
            
            messagebox.showinfo("Éxito", "¡Archivo cifrado y asegurado correctamente!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cifrar: {str(e)}")

    def descifrar(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar un archivo.")
            return
        
        if not self.ruta_archivo.endswith(".enc"):
            messagebox.showerror("Error", "El archivo debe tener la extensión '.enc' para ser descifrado.")
            return

        password = self.entrada_password.get()
        if not password:
            messagebox.showwarning("Advertencia", "Debes ingresar la contraseña de descifrado.")
            return

        try:
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
            
            # Limpiar la UI
            self.ruta_archivo = None
            self.lbl_archivo.configure(text="Ningún archivo seleccionado", text_color="gray")
            self.entrada_password.delete(0, 'end')

            messagebox.showinfo("Éxito", "¡Archivo restaurado correctamente!")

        except Exception:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta o archivo corrupto.")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()