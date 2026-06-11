import os
import base64
import threading
import string
import secrets
import logging
import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- CONFIGURACIÓN DEL SISTEMA DE LOGS ---
logging.basicConfig(
    filename="vault_history.log", 
    level=logging.INFO, 
    format="%(asctime)s | [%(levelname)s] | %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- LÓGICA CRIPTOGRÁFICA Y DE SEGURIDAD ---

def generar_llave_desde_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def borrado_seguro(ruta_archivo, pases=3):
    try:
        tamano = os.path.getsize(ruta_archivo)
        with open(ruta_archivo, "r+b") as archivo:
            for _ in range(pases):
                archivo.seek(0)
                archivo.write(os.urandom(tamano))
        os.remove(ruta_archivo)
    except Exception:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

# --- INTERFAZ GRÁFICA V4.2 (CYBER-TERMINAL + SHREDDER + LOGS) ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto-Vault | Grado Militar")
        self.geometry("500x680")
        self.resizable(False, False)
        
        self.configure(fg_color="#0B0E14")
        ctk.set_appearance_mode("dark")

        self.ruta_target = None
        self.es_carpeta = False

        self.font_title = ctk.CTkFont(family="Consolas", size=26, weight="bold")
        self.font_bold = ctk.CTkFont(family="Consolas", size=13, weight="bold")
        self.font_mono = ctk.CTkFont(family="Consolas", size=12)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#151A22", corner_radius=4, border_width=1, border_color="#2A3241")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 1. CABECERA
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(pady=(30, 5))

        self.lbl_corchete_izq = ctk.CTkLabel(self.title_frame, text="[ ", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_izq.pack(side="left")

        self.lbl_escudo = ctk.CTkLabel(self.title_frame, text="🛡️ ", font=ctk.CTkFont(size=22)) 
        self.lbl_escudo.pack(side="left", pady=(0, 2))
        
        self.lbl_texto = ctk.CTkLabel(self.title_frame, text="CRYPTO-VAULT", font=self.font_title, text_color="#00E5FF")
        self.lbl_texto.pack(side="left")

        self.lbl_corchete_der = ctk.CTkLabel(self.title_frame, text=" ]", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_der.pack(side="left")
        
        self.lbl_subtitulo = ctk.CTkLabel(self.main_frame, text="MOTOR AES-256 // AUDIT LOGGING", text_color="#5C6B89", font=self.font_mono)
        self.lbl_subtitulo.pack(pady=(0, 25))

        # --- SECCIÓN DE ARCHIVO / CARPETA ---
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E2430", corner_radius=2)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_file_title = ctk.CTkLabel(self.file_frame, text="[ TARGET SELECTION ]", font=self.font_bold, text_color="#8B9BB4")
        self.lbl_file_title.pack(pady=(15, 5))

        self.btn_select_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.btn_select_frame.pack(pady=10)

        self.btn_sel_archivo = ctk.CTkButton(self.btn_select_frame, text="Archivo", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#3B82F6", text_color="#3B82F6", hover_color="#1E3A8A", corner_radius=2, width=100, command=lambda: self.seleccionar_target(tipo="archivo"))
        self.btn_sel_archivo.grid(row=0, column=0, padx=5)

        self.btn_sel_carpeta = ctk.CTkButton(self.btn_select_frame, text="Carpeta", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#8B5CF6", text_color="#8B5CF6", hover_color="#4C1D95", corner_radius=2, width=100, command=lambda: self.seleccionar_target(tipo="carpeta"))
        self.btn_sel_carpeta.grid(row=0, column=1, padx=5)

        self.lbl_archivo = ctk.CTkLabel(self.file_frame, text=">_ Esperando target...", text_color="#4B5563", font=self.font_mono, wraplength=400)
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

        # --- SECCIÓN DE ACCIÓN ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(pady=25)

        self.btn_cifrar = ctk.CTkButton(self.action_frame, text="[ 🔒 ENCRIPTAR ]", fg_color="transparent", border_width=1, border_color="#EF4444", text_color="#EF4444", hover_color="#7F1D1D", font=self.font_bold, width=150, height=42, corner_radius=2, command=self.iniciar_cifrado)
        self.btn_cifrar.grid(row=0, column=0, padx=10)

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
        logging.info("Clave segura generada mediante el generador interno.")

    def toggle_password(self):
        if self.chk_mostrar_pass.get() == 1:
            self.entrada_password.configure(show="")
        else:
            self.entrada_password.configure(show="*")

    def seleccionar_target(self, tipo):
        if tipo == "archivo":
            ruta = filedialog.askopenfilename(title="Selecciona un archivo target")
            self.es_carpeta = False
        else:
            ruta = filedialog.askdirectory(title="Selecciona un directorio target")
            self.es_carpeta = True

        if ruta:
            self.ruta_target = ruta
            nombre_corto = os.path.basename(ruta)
            prefijo = "[DIR]" if self.es_carpeta else "[FILE]"
            self.lbl_archivo.configure(text=f">_ {prefijo} {nombre_corto}", text_color="#00E5FF")
            self.lbl_estado.configure(text=f"SYS_STATUS: TARGET {prefijo} ADQUIRIDO.")

    def bloquear_ui(self, bloqueado: bool):
        estado = "disabled" if bloqueado else "normal"
        self.btn_cifrar.configure(state=estado)
        self.btn_descifrar.configure(state=estado)
        self.btn_sel_archivo.configure(state=estado)
        self.btn_sel_carpeta.configure(state=estado)
        self.btn_generar.configure(state=estado)

    def obtener_lista_archivos(self, es_descifrado=False):
        archivos_a_procesar = []
        if not self.es_carpeta:
            archivos_a_procesar.append(self.ruta_target)
        else:
            for raiz, _, archivos in os.walk(self.ruta_target):
                for arch in archivos:
                    ruta_completa = os.path.join(raiz, arch)
                    if es_descifrado:
                        if ruta_completa.endswith(".enc"):
                            archivos_a_procesar.append(ruta_completa)
                    else:
                        if not ruta_completa.endswith(".enc"):
                            archivos_a_procesar.append(ruta_completa)
        return archivos_a_procesar

    # --- LÓGICA BATCH PARA CIFRADO ---
    def iniciar_cifrado(self):
        if not self.validar_entradas(): return
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: ENCRIPTANDO Y DESTRUYENDO ORIGINALES...", text_color="#00E5FF")
        threading.Thread(target=self.tarea_cifrar_batch, args=(self.entrada_password.get(),), daemon=True).start()

    def tarea_cifrar_batch(self, password):
        try:
            archivos = self.obtener_lista_archivos(es_descifrado=False)
            if not archivos:
                raise Exception("No se encontraron archivos válidos para encriptar.")

            for ruta in archivos:
                salt = os.urandom(16)
                llave = generar_llave_desde_password(password, salt)
                f = Fernet(llave)

                with open(ruta, "rb") as archivo:
                    datos_originales = archivo.read()

                datos_cifrados = f.encrypt(datos_originales)
                nuevo_nombre = ruta + ".enc"
                
                with open(nuevo_nombre, "wb") as archivo_cifrado:
                    archivo_cifrado.write(salt + datos_cifrados)
                
                borrado_seguro(ruta)
            
            self.after(500, self.finalizar_operacion, f"ENCRIPTADOS {len(archivos)} ARCHIVOS", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "ERROR BATCH ENCRIPTACION", False, str(e))

    # --- LÓGICA BATCH PARA DESCIFRADO ---
    def iniciar_descifrado(self):
        if not self.validar_entradas(es_descifrado=True): return
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: VALIDANDO BATCH CREDENCIALES...", text_color="#00E5FF")
        threading.Thread(target=self.tarea_descifrar_batch, args=(self.entrada_password.get(),), daemon=True).start()

    def tarea_descifrar_batch(self, password):
        try:
            archivos = self.obtener_lista_archivos(es_descifrado=True)
            if not archivos:
                raise Exception("No se encontraron archivos .enc en el target.")

            errores = 0
            for ruta in archivos:
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

                    borrado_seguro(ruta)
                except Exception:
                    errores += 1
            
            if errores > 0:
                self.after(500, self.finalizar_operacion, "ADVERTENCIA", False, f"Proceso terminado. {errores} archivos fallaron (Clave incorrecta/Corruptos).")
            else:
                self.after(500, self.finalizar_operacion, f"DESENCRIPTADOS {len(archivos)} ARCHIVOS", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "ERROR BATCH DESENCRIPTACION", False, str(e))

    def finalizar_operacion(self, operacion, exito, error_msg):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.bloquear_ui(False)
        
        target_registrado = self.ruta_target

        if exito:
            logging.info(f"Operacion: {operacion} | Target: {target_registrado} | Estado: EXITO")
            self.limpiar_ui()
            self.lbl_estado.configure(text=f"SYS_STATUS: {operacion} EXITOSAMENTE.", text_color="#10B981")
            messagebox.showinfo("SYS_MSG", f"Operación Batch completada: {operacion}.")
        else:
            logging.error(f"Operacion: {operacion} | Target: {target_registrado} | Estado: FALLIDO | Causa: {error_msg}")
            self.lbl_estado.configure(text="SYS_STATUS: ADVERTENCIA / ERROR BATCH", text_color="#DC2626")
            messagebox.showerror("SYS_ERR", error_msg)

    def validar_entradas(self, es_descifrado=False):
        if not self.ruta_target:
            messagebox.showwarning("SYS_WARN", "Target no seleccionado.")
            return False
        if not self.es_carpeta and es_descifrado and not self.ruta_target.endswith(".enc"):
            messagebox.showerror("SYS_ERR", "Formato inválido. Selecciona una carpeta o un archivo .enc")
            return False
        if not self.entrada_password.get():
            messagebox.showwarning("SYS_WARN", "Se requiere master_key.")
            return False
        return True

    def limpiar_ui(self):
        self.ruta_target = None
        self.es_carpeta = False
        self.lbl_archivo.configure(text=">_ Esperando target...", text_color="#4B5563")
        self.entrada_password.delete(0, 'end')
        self.chk_mostrar_pass.deselect()
        self.entrada_password.configure(show="*")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()