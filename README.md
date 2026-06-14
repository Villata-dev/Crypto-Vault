# [ 🛡️ CRYPTO-VAULT V7.0 ]

**Bóveda criptográfica local con arquitectura Zero-Trust y contramedidas forenses.**
Herramienta de encriptación diseñada para proteger archivos y directorios mediante cifrado simétrico AES-256, esteganografía y protocolos de autodestrucción.

---

### ⚙️ ESPECIFICACIONES TÉCNICAS (V7.0)

* **Motor Core:** Cifrado `AES-256` con derivación de claves `PBKDF2HMAC` (480k iteraciones + Salt dinámico).
* **2FA Físico (Keyfile):** Soporte para autenticación de dos factores utilizando bytes arbitrarios de cualquier archivo local (MP3, JPG, PDF) fusionados con la `master_key`.
* **Esteganografía (Stego-Payload):** Capacidad de ofuscar datos cifrados inyectándolos en la capa final del código binario de imágenes portadoras (`.png`, `.jpg`).
* **Borrado Forense (Shredding):** Sobrescritura en disco con ruido estático previo a la eliminación mediante `os.remove` para mitigar recuperación de datos.
* **Protocolo Anti-Fuerza Bruta (Modo Pánico):** Auto-destrucción irreversible de payloads tras 3 intentos de descifrado fallidos.

---

### 📦 COMPILACIÓN Y DESPLIEGUE

El proyecto ha sido empaquetado en un binario independiente (`.exe`) sin dependencias externas usando PyInstaller. 
*(Nota: Los binarios no se alojan en este repositorio por políticas de seguridad).*

```bash
# Compilación manual desde código fuente
pip install requirements.txt
pyinstaller --noconsole --onefile --clean vault.py