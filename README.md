# 🛡️ CRYPTO-VAULT

**Motor de encriptación local con interfaz gráfica (GUI) de grado militar.**

Crypto-Vault es una herramienta diseñada para asegurar archivos confidenciales (*targets*) mediante cifrado simétrico avanzado, protegiendo la información contra accesos no autorizados en entornos locales.

---

## ⚙️ ESPECIFICACIONES TÉCNICAS

* **Algoritmo Core:** `AES-256` (*Advanced Encryption Standard*), operando a través de la librería criptográfica nativa de Python.
* **Derivación de Claves (KDF):** Implementa `PBKDF2HMAC` utilizando `SHA-256`.
* **Resistencia Brute-Force:** 480.000 iteraciones automáticas combinadas con la inyección de un *salt* criptográfico aleatorio de 16 bytes por cada archivo.
* **Arquitectura GUI:** Construida sobre `CustomTkinter`, utilizando manejo de hilos (*threading*) asíncronos para aislar el motor matemático de la interfaz visual, previniendo cuelgues del sistema durante el procesamiento de *payloads* pesados.

---

## 📦 DESPLIEGUE E INSTALACIÓN

### Dependencias del entorno

Requiere **Python 3.8** o superior.

```bash
pip install cryptography customtkinter
```

### Clonado del repositorio

```bash
git clone https://github.com/tu-usuario/crypto-vault.git
cd crypto-vault
```

---

## 🚀 MANUAL DE OPERACIÓN

### Ejecución del entorno visual

```bash
python vault.py
```

### Flujo de Encriptación / Desencriptación

1. **Target:** Selecciona el archivo objetivo desde el directorio del sistema.
2. **Master Key:** Ingresa tu credencial de acceso o utiliza el generador interno (**⚡ Generar**) para crear un token seguro de 16 caracteres.
3. **Ejecución:** Inicia el proceso. El sistema destruirá el archivo original (`os.remove`) y generará un artefacto seguro con extensión `.enc`.

---

> [!WARNING]
> **CRITICAL DATA LOSS**
>
> La arquitectura de Crypto-Vault opera bajo políticas de **Zero-Knowledge**. El *salt* se incrusta en el archivo cifrado, pero la contraseña **no se almacena en ninguna parte del sistema**.
>
> La pérdida de la **master key** implica la pérdida irreversible del archivo.

---

**Desarrollado y mantenido para entornos locales de alta privacidad.**
