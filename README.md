# 🛡️ Crypto Vault

Crypto Vault es una aplicación de escritorio para cifrar y descifrar archivos de forma local utilizando algoritmos criptográficos modernos. Su objetivo es proteger documentos, imágenes y cualquier tipo de archivo mediante una contraseña maestra, evitando que terceros puedan acceder a su contenido.

## Características

### 🔐 Cifrado AES-256

Utiliza la librería `cryptography` de Python para aplicar cifrado simétrico AES-256 sobre los archivos seleccionados, garantizando un alto nivel de seguridad.

### 🔑 Derivación segura de claves

La contraseña ingresada por el usuario no se usa directamente como clave de cifrado. En su lugar, se genera una clave mediante PBKDF2-HMAC con SHA-256, un salt aleatorio y 480.000 iteraciones, dificultando ataques de fuerza bruta o diccionario.

### 🎨 Interfaz gráfica

La aplicación cuenta con una interfaz desarrollada con `CustomTkinter`, incluyendo:

* Modo oscuro.
* Selección de archivos mediante explorador.
* Mensajes de estado y confirmación.
* Manejo de errores mediante ventanas emergentes.

### 🗑️ Eliminación del archivo original

Una vez completado el proceso de cifrado o descifrado, el archivo original es eliminado para reducir el riesgo de exposición accidental de información.

---

## Requisitos

* Python 3.10 o superior
* Dependencias:

```bash
pip install cryptography customtkinter
```

## Instalación

Clona el repositorio y accede al directorio del proyecto:

```bash
git clone https://github.com/tu-usuario/crypto-vault.git
cd crypto-vault
```

---

## Ejecución

Para iniciar la aplicación:

```bash
python vault.py
```

---

## Cómo usarlo

### 1. Selecciona un archivo

Haz clic en **Seleccionar Archivo** y elige el archivo que deseas cifrar o descifrar.

### 2. Ingresa una contraseña

Escribe una contraseña segura. Esta contraseña será necesaria para recuperar el archivo posteriormente.

> Importante: si la contraseña se pierde, el archivo cifrado no podrá recuperarse.

### 3. Cifra o descifra

**Cifrar**

* Selecciona cualquier archivo.
* Presiona **Cifrar**.
* Se generará una versión con extensión `.enc`.

**Descifrar**

* Selecciona un archivo `.enc`.
* Introduce la contraseña utilizada durante el cifrado.
* Presiona **Descifrar** para restaurar el archivo original.

---

## Consideraciones de seguridad

* Las contraseñas nunca se almacenan.
* El salt criptográfico se genera automáticamente y se incorpora dentro del archivo cifrado.
* No existe ningún mecanismo de recuperación de contraseñas.
* Si la contraseña es incorrecta o se pierde, el contenido cifrado será inaccesible.

---

## Tecnologías utilizadas

* Python
* Cryptography
* CustomTkinter
* AES-256
* PBKDF2-HMAC (SHA-256)

---

## Licencia

Proyecto desarrollado con fines educativos y de aprendizaje sobre criptografía aplicada en Python.
