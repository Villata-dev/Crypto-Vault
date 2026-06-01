import os
import argparse
from cryptography.fernet import Fernet

def generar_llave():
    """Genera una llave de encriptación y la guarda en un archivo."""
    llave = Fernet.generate_key()
    with open("secret.key", "wb") as archivo_llave:
        archivo_llave.write(llave)
    print("[+] Llave maestra generada y guardada en 'secret.key'")
    print("[!] ADVERTENCIA: No pierdas este archivo, o no podrás recuperar tus datos.")

def cargar_llave():
    """Carga la llave de encriptación desde el archivo."""
    if not os.path.exists("secret.key"):
        print("[-] Error: No se encontró 'secret.key'. Usa -g para generar una primero.")
        exit(1)
    return open("secret.key", "rb").read()

def cifrar_archivo(ruta_archivo):
    """Toma un archivo y lo encripta."""
    if not os.path.exists(ruta_archivo):
        print(f"[-] Error: El archivo '{ruta_archivo}' no existe.")
        return

    llave = cargar_llave()
    f = Fernet(llave)

    with open(ruta_archivo, "rb") as archivo:
        datos_originales = archivo.read()

    datos_cifrados = f.encrypt(datos_originales)
    
    nuevo_nombre = ruta_archivo + ".enc"
    with open(nuevo_nombre, "wb") as archivo_cifrado:
        archivo_cifrado.write(datos_cifrados)
    
    # Opcional: eliminar el archivo original sin cifrar
    os.remove(ruta_archivo)
    print(f"[+] Archivo encriptado con éxito: {nuevo_nombre}")

def descifrar_archivo(ruta_archivo):
    """Toma un archivo encriptado y lo restaura a su estado original."""
    if not os.path.exists(ruta_archivo) or not ruta_archivo.endswith(".enc"):
        print(f"[-] Error: Archivo inválido. Debe existir y terminar en '.enc'.")
        return

    llave = cargar_llave()
    f = Fernet(llave)

    with open(ruta_archivo, "rb") as archivo_cifrado:
        datos_cifrados = archivo_cifrado.read()

    try:
        datos_descifrados = f.decrypt(datos_cifrados)
    except Exception:
        print("[-] Error crítico: La llave no coincide o el archivo está corrupto.")
        return

    nombre_original = ruta_archivo.replace(".enc", "")
    with open(nombre_original, "wb") as archivo_descifrado:
        archivo_descifrado.write(datos_descifrados)

    # Eliminamos la versión cifrada
    os.remove(ruta_archivo)
    print(f"[+] Archivo desencriptado y restaurado: {nombre_original}")

def main():
    parser = argparse.ArgumentParser(description="Crypto-Vault: Herramienta de Cifrado de Archivos AES")
    parser.add_argument("-g", "--generar", action="store_true", help="Genera una nueva llave de encriptación (secret.key)")
    parser.add_argument("-e", "--encrypt", type=str, help="Ruta del archivo a encriptar")
    parser.add_argument("-d", "--decrypt", type=str, help="Ruta del archivo a desencriptar (.enc)")

    args = parser.parse_args()

    print("========================================")
    print("             CRYPTO-VAULT               ")
    print("========================================")

    if args.generar:
        generar_llave()
    elif args.encrypt:
        cifrar_archivo(args.encrypt)
    elif args.decrypt:
        descifrar_archivo(args.decrypt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()