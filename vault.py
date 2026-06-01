import os
import argparse
import getpass
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generar_llave_desde_password(password: str, salt: bytes) -> bytes:
    """Deriva una llave segura de 32 bytes a partir de una contraseña humana y un 'salt' aleatorio."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000, # Grado militar: hace que ataques de fuerza bruta sean lentísimos
    )
    # Fernet requiere que la llave esté codificada en base64
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def cifrar_archivo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"[-] Error: El archivo '{ruta_archivo}' no existe.")
        return

    # Usamos getpass para que la contraseña no se vea en la terminal al escribirla
    password = getpass.getpass("[?] Ingresa una contraseña maestra para cifrar: ")
    confirmacion = getpass.getpass("[?] Confirma tu contraseña: ")

    if password != confirmacion:
        print("[-] Error: Las contraseñas no coinciden. Operación cancelada.")
        return

    # Generamos un "Salt" aleatorio de 16 bytes. Es crucial para evitar ataques de diccionario.
    salt = os.urandom(16)
    llave = generar_llave_desde_password(password, salt)
    f = Fernet(llave)

    with open(ruta_archivo, "rb") as archivo:
        datos_originales = archivo.read()

    datos_cifrados = f.encrypt(datos_originales)
    
    nuevo_nombre = ruta_archivo + ".enc"
    with open(nuevo_nombre, "wb") as archivo_cifrado:
        # TRUCO MAESTRO: Guardamos el 'salt' en los primeros 16 bytes del archivo
        # No es secreto, pero es necesario para que el algoritmo pueda descifrarlo después.
        archivo_cifrado.write(salt + datos_cifrados)
    
    os.remove(ruta_archivo)
    print(f"[+] Archivo cifrado con éxito: {nuevo_nombre}")

def descifrar_archivo(ruta_archivo):
    if not os.path.exists(ruta_archivo) or not ruta_archivo.endswith(".enc"):
        print(f"[-] Error: Archivo inválido. Debe existir y terminar en '.enc'.")
        return

    password = getpass.getpass("[?] Ingresa la contraseña para descifrar: ")

    with open(ruta_archivo, "rb") as archivo_cifrado:
        contenido = archivo_cifrado.read()

    # Extraemos el 'salt' (los primeros 16 bytes) y el resto son los datos cifrados
    salt = contenido[:16]
    datos_cifrados = contenido[16:]

    llave = generar_llave_desde_password(password, salt)
    f = Fernet(llave)

    try:
        datos_descifrados = f.decrypt(datos_cifrados)
    except Exception:
        print("[-] Acceso Denegado: Contraseña incorrecta o archivo corrupto.")
        return

    nombre_original = ruta_archivo.replace(".enc", "")
    with open(nombre_original, "wb") as archivo_descifrado:
        archivo_descifrado.write(datos_descifrados)

    os.remove(ruta_archivo)
    print(f"[+] Acceso Concedido: Archivo restaurado a {nombre_original}")

def main():
    parser = argparse.ArgumentParser(description="Crypto-Vault: Bóveda de archivos AES-256")
    parser.add_argument("-e", "--encrypt", type=str, help="Ruta del archivo a encriptar")
    parser.add_argument("-d", "--decrypt", type=str, help="Ruta del archivo a desencriptar (.enc)")

    args = parser.parse_args()

    print("========================================")
    print("             CRYPTO-VAULT               ")
    print("========================================")

    if args.encrypt:
        cifrar_archivo(args.encrypt)
    elif args.decrypt:
        descifrar_archivo(args.decrypt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()