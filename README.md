# 🛡️ CRYPTO-VAULT

**Motor de encriptación local con interfaz gráfica (GUI) de grado militar.**

Crypto-Vault es una herramienta diseñada para asegurar archivos confidenciales y **directorios completos (Batch Processing)** mediante cifrado simétrico avanzado, protegiendo la información en entornos locales.

---

## ⚙️ ESPECIFICACIONES TÉCNICAS

- **Algoritmo Core:** `AES-256` (Advanced Encryption Standard), operando a través de la librería criptográfica nativa de Python.
- **Derivación de Claves (KDF):** Implementa `PBKDF2HMAC` utilizando `SHA-256` con 480,000 iteraciones automáticas y *salt* aleatorio.
- **Procesamiento Masivo (V4.0):** Integración de `os.walk` para el escaneo y encriptación recursiva de directorios completos de forma simultánea.
- **Arquitectura GUI:** Construida sobre `CustomTkinter` utilizando manejo de hilos (*threading*) asíncronos para aislar el motor matemático de la interfaz visual.

---

## 📦 DESPLIEGUE E INSTALACIÓN

Requiere **Python 3.8** o superior.

```bash
pip install cryptography customtkinter

git clone https://github.com/tu-usuario/crypto-vault.git
cd crypto-vault
```

---

## 🚀 MANUAL DE OPERACIÓN

```bash
python vault.py
```

### Flujo de Trabajo

#### 1. Target
Selecciona si deseas procesar un solo **Archivo** o una **Carpeta** completa.

#### 2. Master Key
Ingresa tu credencial o utiliza el generador interno (**⚡ Generar**) para crear un token seguro.

#### 3. Ejecución
El sistema procesará el objetivo seleccionado, destruyendo los originales (`os.remove`) y dejando únicamente los artefactos `.enc`.

---

> [!WARNING]
> **CRITICAL DATA LOSS**
>
> La arquitectura opera bajo políticas **Zero-Knowledge**. La pérdida de la `master_key` resulta en la pérdida irreversible de todos los archivos y carpetas procesados.