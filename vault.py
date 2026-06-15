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

STEGO_SEPARATOR = b"||CV_STEGO_PAYLOAD||"

# --- LÓGICA CRIPTOGRÁFICA Y DE SEGURIDAD ---

def generar_llave_desde_password(password: str, salt: bytes, ruta_keyfile: str = None) -> bytes:
    material_base = password.encode()
    if ruta_keyfile and os.path.exists(ruta_keyfile):
        try:
            with open(ruta_keyfile, "rb") as f:
                bytes_keyfile = f.read(65536) 
            material_base += bytes_keyfile
        except Exception as e:
            logging.error(f"Error leyendo Keyfile: {e}")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(material_base))

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

# --- INTERFAZ GRÁFICA V8.0 (CYBER-TERMINAL + AUDIT CONSOLE) ---

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto-Vault | Grado Militar")
        self.geometry("500x850")  # Ajuste de tamaño para la consola integrada
        self.resizable(False, False)
        
        self.configure(fg_color="#0B0E14")
        ctk.set_appearance_mode("dark")

        self.ruta_target = None
        self.ruta_keyfile = None
        self.ruta_portador = None
        self.es_carpeta = False
        
        self.intentos_fallidos = 0
        self.max_intentos = 3

        self.font_title = ctk.CTkFont(family="Consolas", size=26, weight="bold")
        self.font_bold = ctk.CTkFont(family="Consolas", size=13, weight="bold")
        self.font_mono = ctk.CTkFont(family="Consolas", size=12)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#151A22", corner_radius=4, border_width=1, border_color="#2A3241")
        self.main_frame.pack(pady=15, padx=20, fill="both", expand=True)

        # CABECERA
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(pady=(15, 5))

        self.lbl_corchete_izq = ctk.CTkLabel(self.title_frame, text="[ ", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_izq.pack(side="left")

        self.lbl_escudo = ctk.CTkLabel(self.title_frame, text="🛡️ ", font=ctk.CTkFont(size=22)) 
        self.lbl_escudo.pack(side="left", pady=(0, 2))
        
        self.lbl_texto = ctk.CTkLabel(self.title_frame, text="CRYPTO-VAULT", font=self.font_title, text_color="#00E5FF")
        self.lbl_texto.pack(side="left")

        self.lbl_corchete_der = ctk.CTkLabel(self.title_frame, text=" ]", font=self.font_title, text_color="#00E5FF")
        self.lbl_corchete_der.pack(side="left")
        
        self.lbl_subtitulo = ctk.CTkLabel(self.main_frame, text="MOTOR AES-256 // CONSOLE AUDIT", text_color="#5C6B89", font=self.font_mono)
        self.lbl_subtitulo.pack(pady=(0, 10))

        # --- SECCIÓN DE TARGET ---
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E2430", corner_radius=2)
        self.file_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_file_title = ctk.CTkLabel(self.file_frame, text="[ TARGET SELECTION ]", font=self.font_bold, text_color="#8B9BB4")
        self.lbl_file_title.pack(pady=(10, 5))

        self.btn_select_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.btn_select_frame.pack(pady=5)

        self.btn_sel_archivo = ctk.CTkButton(self.btn_select_frame, text="Archivo", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#3B82F6", text_color="#3B82F6", hover_color="#1E3A8A", corner_radius=2, width=100, command=lambda: self.seleccionar_target(tipo="archivo"))
        self.btn_sel_archivo.grid(row=0, column=0, padx=5)

        self.btn_sel_carpeta = ctk.CTkButton(self.btn_select_frame, text="Carpeta", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#8B5CF6", text_color="#8B5CF6", hover_color="#4C1D95", corner_radius=2, width=100, command=lambda: self.seleccionar_target(tipo="carpeta"))
        self.btn_sel_carpeta.grid(row=0, column=1, padx=5)

        self.lbl_archivo = ctk.CTkLabel(self.file_frame, text=">_ Esperando target...", text_color="#4B5563", font=self.font_mono, wraplength=400)
        self.lbl_archivo.pack(pady=(0, 10))

        # --- SECCIÓN DE CREDENCIALES ---
        self.security_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E2430", corner_radius=2)
        self.security_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_sec_title = ctk.CTkLabel(self.security_frame, text="[ CREDENTIALS & TACTICS ]", font=self.font_bold, text_color="#8B9BB4")
        self.lbl_sec_title.pack(pady=(10, 5))

        self.pass_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.pass_frame.pack(pady=5)

        self.entrada_password = ctk.CTkEntry(self.pass_frame, placeholder_text="Ingresa master_key", show="*", width=200, height=35, font=self.font_mono, fg_color="#0F1219", border_color="#374151", corner_radius=2)
        self.entrada_password.grid(row=0, column=0, padx=(0, 10))

        self.btn_generar = ctk.CTkButton(self.pass_frame, text="⚡ Generar", width=90, height=35, font=self.font_bold, fg_color="transparent", border_width=1, border_color="#8B5CF6", text_color="#8B5CF6", hover_color="#4C1D95", corner_radius=2, command=self.generar_password)
        self.btn_generar.grid(row=0, column=1)

        self.chk_mostrar_pass = ctk.CTkCheckBox(self.security_frame, text="Visibilidad", font=self.font_mono, text_color="#9CA3AF", fg_color="#00E5FF", hover_color="#00B3CC", corner_radius=2, checkbox_width=16, checkbox_height=16, border_width=1, command=self.toggle_password)
        self.chk_mostrar_pass.pack(pady=(5, 5))

        self.tools_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.tools_frame.pack(pady=5)

        self.btn_keyfile = ctk.CTkButton(self.tools_frame, text="🔑 Keyfile", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#F59E0B", text_color="#F59E0B", hover_color="#B45309", corner_radius=2, width=120, command=self.seleccionar_keyfile)
        self.btn_keyfile.grid(row=0, column=0, padx=5)

        self.btn_portador = ctk.CTkButton(self.tools_frame, text="🖼️ Portador", font=self.font_bold, fg_color="transparent", border_width=1, border_color="#EC4899", text_color="#EC4899", hover_color="#BE185D", corner_radius=2, width=120, command=self.seleccionar_portador)
        self.btn_portador.grid(row=0, column=1, padx=5)
        
        self.switch_autodestruccion = ctk.CTkSwitch(self.security_frame, text="💣 Protocolo Auto-Destrucción", font=self.font_bold, text_color="#EF4444", progress_color="#EF4444", button_color="#7F1D1D", button_hover_color="#991B1B")
        self.switch_autodestruccion.pack(pady=(5, 5))

        self.lbl_status_avanzado = ctk.CTkLabel(self.security_frame, text="[ 2FA: OFF ] | [ STEGO: OFF ]", text_color="#4B5563", font=self.font_mono)
        self.lbl_status_avanzado.pack(pady=(0, 5))

        # --- SECCIÓN DE ACCIÓN Y CONSOLA ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(pady=10)

        self.btn_cifrar = ctk.CTkButton(self.action_frame, text="[ 🔒 ENCRIPTAR ]", fg_color="transparent", border_width=1, border_color="#EF4444", text_color="#EF4444", hover_color="#7F1D1D", font=self.font_bold, width=140, height=42, corner_radius=2, command=self.iniciar_cifrado)
        self.btn_cifrar.grid(row=0, column=0, padx=5)

        self.btn_descifrar = ctk.CTkButton(self.action_frame, text="[ 🔓 DESENCRIPTAR ]", fg_color="transparent", border_width=1, border_color="#10B981", text_color="#10B981", hover_color="#064E3B", font=self.font_bold, width=140, height=42, corner_radius=2, command=self.iniciar_descifrado)
        self.btn_descifrar.grid(row=0, column=1, padx=5)

        self.btn_logs = ctk.CTkButton(self.action_frame, text="[ 📑 AUDIT ]", fg_color="transparent", border_width=1, border_color="#00E5FF", text_color="#00E5FF", hover_color="#0F3846", font=self.font_bold, width=100, height=42, corner_radius=2, command=self.toggle_consola_logs)
        self.btn_logs.grid(row=0, column=2, padx=5)

        # CONSOLA DE TEXTO (Desplegable internamente)
        self.txt_consola = ctk.CTkTextbox(self.main_frame, height=140, font=self.font_mono, fg_color="#090B10", text_color="#10B981", border_width=1, border_color="#2A3241", corner_radius=2, state="disabled")

        # --- BARRA DE PROGRESO ---
        self.progressbar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", width=350, progress_color="#00E5FF", fg_color="#1E2430")
        self.progressbar.set(0)

        # --- BARRA DE ESTADO ---
        self.lbl_estado = ctk.CTkLabel(self, text="SYS_STATUS: INACTIVO", text_color="#4B5563", font=self.font_mono)
        self.lbl_estado.pack(side="bottom", pady=5)
        
        # Cargar los registros existentes al iniciar
        self.actualizar_consola_logs()

    # --- FUNCIONES DE LA INTERFAZ ---

    def toggle_consola_logs(self):
        """Muestra u oculta la terminal de logs en la UI"""
        if self.txt_consola.winfo_manager():
            self.txt_consola.pack_forget()
            self.lbl_estado.configure(text="SYS_STATUS: CONSOLA OCULTA.")
        else:
            self.actualizar_consola_logs()
            self.txt_consola.pack(pady=10, padx=20, fill="x", before=self.progressbar)
            self.txt_consola.see("end")
            self.lbl_estado.configure(text="SYS_STATUS: MONITOR DE AUDITORÍA ACTIVO.")

    def actualizar_consola_logs(self):
        """Lee el archivo log e inyecta las líneas en el textbox estilo hacker"""
        if os.path.exists("vault_history.log"):
            with open("vault_history.log", "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            self.txt_consola.configure(state="normal")
            self.txt_consola.delete("1.0", "end")
            # Mostramos las últimas 30 líneas para no sobrecargar el buffer
            self.txt_consola.insert("1.0", "".join(lineas[-30:]))
            self.txt_consola.configure(state="disabled")
            self.txt_consola.see("end")

    def actualizar_status_avanzado(self):
        kf_status = "ON" if self.ruta_keyfile else "OFF"
        st_status = "ON" if self.ruta_portador else "OFF"
        color = "#F59E0B" if (self.ruta_keyfile or self.ruta_portador) else "#4B5563"
        self.lbl_status_avanzado.configure(text=f"[ 2FA: {kf_status} ] | [ STEGO: {st_status} ]", text_color=color)

    def seleccionar_keyfile(self):
        ruta = filedialog.askopenfilename(title="Selecciona Keyfile")
        if ruta:
            self.ruta_keyfile = ruta
            self.actualizar_status_avanzado()

    def seleccionar_portador(self):
        ruta = filedialog.askopenfilename(title="Selecciona Portador (JPG/PNG)", filetypes=[("Imágenes", "*.jpg *.jpeg *.png")])
        if ruta:
            self.ruta_portador = ruta
            self.actualizar_status_avanzado()

    def generar_password(self):
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_+="
        password_segura = ''.join(secrets.choice(caracteres) for _ in range(16))
        self.entrada_password.delete(0, 'end')
        self.entrada_password.insert(0, password_segura)
        self.chk_mostrar_pass.select()
        self.entrada_password.configure(show="")

    def toggle_password(self):
        if self.chk_mostrar_pass.get() == 1:
            self.entrada_password.configure(show="")
        else:
            self.entrada_password.configure(show="*")

    def seleccionar_target(self, tipo):
        if tipo == "archivo":
            ruta = filedialog.askopenfilename(title="Selecciona target")
            self.es_carpeta = False
        else:
            ruta = filedialog.askdirectory(title="Selecciona directorio target")
            self.es_carpeta = True

        if ruta:
            self.ruta_target = ruta
            nombre_corto = os.path.basename(ruta)
            prefijo = "[DIR]" if self.es_carpeta else "[FILE]"
            self.lbl_archivo.configure(text=f">_ {prefijo} {nombre_corto}", text_color="#00E5FF")

    def bloquear_ui(self, bloqueado: bool):
        estado = "disabled" if bloqueado else "normal"
        self.btn_cifrar.configure(state=estado)
        self.btn_descifrar.configure(state=estado)
        self.btn_sel_archivo.configure(state=estado)
        self.btn_sel_carpeta.configure(state=estado)
        self.btn_generar.configure(state=estado)
        self.btn_keyfile.configure(state=estado)
        self.btn_portador.configure(state=estado)
        self.switch_autodestruccion.configure(state=estado)
        self.btn_logs.configure(state=estado)

    def obtener_lista_archivos(self, es_descifrado=False):
        archivos_a_procesar = []
        if not self.es_carpeta:
            archivos_a_procesar.append(self.ruta_target)
        else:
            for raiz, _, archivos in os.walk(self.ruta_target):
                for arch in archivos:
                    ruta_completa = os.path.join(raiz, arch)
                    if es_descifrado:
                        if ruta_completa.endswith((".enc", ".png", ".jpg", ".jpeg")):
                            archivos_a_procesar.append(ruta_completa)
                    else:
                        if not ruta_completa.endswith((".enc", ".png", ".jpg", ".jpeg")):
                            archivos_a_procesar.append(ruta_completa)
        return archivos_a_procesar

    def iniciar_cifrado(self):
        if not self.validar_entradas(): return
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: PROCESANDO DATOS...", text_color="#00E5FF")
        threading.Thread(target=self.tarea_cifrar_batch, args=(self.entrada_password.get(), self.ruta_keyfile, self.ruta_portador), daemon=True).start()

    def tarea_cifrar_batch(self, password, keyfile, portador):
        try:
            archivos = self.obtener_lista_archivos(es_descifrado=False)
            for ruta in archivos:
                salt = os.urandom(16)
                llave = generar_llave_desde_password(password, salt, keyfile)
                f = Fernet(llave)
                with open(ruta, "rb") as archivo:
                    datos_originales = archivo.read()
                datos_cifrados = f.encrypt(datos_originales)
                payload_seguro = salt + datos_cifrados

                if portador:
                    with open(portador, "rb") as img:
                        bytes_imagen = img.read()
                    with open(ruta + "_secure.png", "wb") as stego_file:
                        stego_file.write(bytes_imagen + STEGO_SEPARATOR + payload_seguro)
                else:
                    with open(ruta + ".enc", "wb") as archivo_cifrado:
                        archivo_cifrado.write(payload_seguro)
                borrado_seguro(ruta)
            
            self.after(500, self.finalizar_operacion, f"ENCRIPTADOS {len(archivos)} ARCHIVOS", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "ERROR ENCRIPTACION", False, str(e))

    def iniciar_descifrado(self):
        if not self.validar_entradas(es_descifrado=True): return
        self.bloquear_ui(True)
        self.progressbar.pack(pady=(0, 5))
        self.progressbar.start()
        self.lbl_estado.configure(text="SYS_STATUS: VALIDANDO CREDENCIALES...", text_color="#00E5FF")
        threading.Thread(target=self.tarea_descifrar_batch, args=(self.entrada_password.get(), self.ruta_keyfile, self.switch_autodestruccion.get()), daemon=True).start()

    def tarea_descifrar_batch(self, password, keyfile, autodestruccion_activa):
        try:
            archivos = self.obtener_lista_archivos(es_descifrado=True)
            errores = 0
            procesados = 0

            for ruta in archivos:
                try:
                    with open(ruta, "rb") as target_file:
                        contenido = target_file.read()
                    
                    if STEGO_SEPARATOR in contenido:
                        _, payload = contenido.split(STEGO_SEPARATOR, 1)
                    else:
                        payload = contenido

                    salt = payload[:16]
                    datos_cifrados = payload[16:]
                    llave = generar_llave_desde_password(password, salt, keyfile)
                    f = Fernet(llave)
                    datos_descifrados = f.decrypt(datos_cifrados)

                    nombre_original = ruta.replace("_secure.png", "").replace(".enc", "")
                    with open(nombre_original, "wb") as archivo_descifrado:
                        archivo_descifrado.write(datos_descifrados)

                    borrado_seguro(ruta)
                    procesados += 1
                except Exception:
                    errores += 1
            
            if errores > 0 and procesados == 0:
                self.intentos_fallidos += 1
                if autodestruccion_activa == 1 and self.intentos_fallidos >= self.max_intentos:
                    for ruta in archivos:
                        borrado_seguro(ruta)
                    logging.critical("PANIC MODE TRIGGERED: ARCHIVOS ANIQUILADOS POR FUERZA BRUTA.")
                    self.intentos_fallidos = 0
                    self.after(500, self.finalizar_operacion, "PROTOCOLO DE AUTO-DESTRUCCIÓN", False, "ATENCIÓN: Múltiples fallos detectados. Los archivos encriptados han sido destruidos irreversiblemente.")
                    return

                msg_error = f"Credenciales denegadas. Intento {self.intentos_fallidos}/{self.max_intentos} antes de Auto-Destrucción." if autodestruccion_activa == 1 else "Las credenciales fallaron."
                self.after(500, self.finalizar_operacion, "ERROR CRÍTICO", False, msg_error)
            elif errores > 0:
                self.after(500, self.finalizar_operacion, "ADVERTENCIA", False, f"Proceso parcial. {errores} archivos fallaron.")
            else:
                self.intentos_fallidos = 0
                self.after(500, self.finalizar_operacion, f"DESENCRIPTADOS {procesados} ARCHIVOS", True, "")
        except Exception as e:
            self.after(500, self.finalizar_operacion, "ERROR DESENCRIPTACION", False, str(e))

    def finalizar_operacion(self, operacion, exito, error_msg):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.bloquear_ui(False)
        
        target_registrado = self.ruta_target
        usando_2fa = "SI" if self.ruta_keyfile else "NO"
        usando_stego = "SI" if self.ruta_portador else "NO"

        if exito:
            logging.info(f"Operacion: {operacion} | Target: {target_registrado} | 2FA: {usando_2fa} | STEGO: {usando_stego} | Estado: EXITO")
            self.limpiar_ui()
            self.lbl_estado.configure(text=f"SYS_STATUS: {operacion} EXITOSAMENTE.", text_color="#10B981")
            messagebox.showinfo("SYS_MSG", f"Operación completada: {operacion}.")
        else:
            logging.error(f"Operacion: {operacion} | Target: {target_registrado} | 2FA: {usando_2fa} | STEGO: {usando_stego} | Causa: {error_msg}")
            color_alerta = "#DC2626"
            if "AUTO-DESTRUCCIÓN" in operacion:
                color_alerta = "#991B1B"
            self.lbl_estado.configure(text=f"SYS_STATUS: {operacion}", text_color=color_alerta)
            messagebox.showerror("SYS_ERR", error_msg)
        
        # Sincronizar inmediatamente la consola visual con el nuevo log generado
        self.actualizar_consola_logs()

    def validar_entradas(self, es_descifrado=False):
        if not self.ruta_target:
            messagebox.showwarning("SYS_WARN", "Target no seleccionado.")
            return False
        if not self.entrada_password.get():
            messagebox.showwarning("SYS_WARN", "Se requiere master_key.")
            return False
        return True

    def limpiar_ui(self):
        self.ruta_target = None
        self.es_carpeta = False
        self.ruta_keyfile = None
        self.ruta_portador = None
        self.lbl_archivo.configure(text=">_ Esperando target...", text_color="#4B5563")
        self.actualizar_status_avanzado()
        self.entrada_password.delete(0, 'end')
        self.chk_mostrar_pass.deselect()
        self.entrada_password.configure(show="*")

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()