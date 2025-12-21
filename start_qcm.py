#!/usr/bin/env python3
"""
Lanceur QCM Chiropraxie

Double-cliquez sur ce fichier pour lancer l'application.
Ouvre automatiquement le navigateur sur l'interface de quiz.
"""

import http.server
import os
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

PORT = 8080
APP_PATH = "/app.html"


def find_free_port(start_port: int = 8080, max_tries: int = 100) -> int:
    """Trouve un port libre à partir de start_port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Aucun port libre trouvé entre {start_port} et {start_port + max_tries}")


def main():
    # Se placer dans le répertoire du script
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)
    
    # Vérifier que app.html existe
    if not (script_dir / "app.html").exists():
        print("❌ Erreur: app.html non trouvé")
        print(f"   Répertoire actuel: {script_dir}")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
    
    # Vérifier que la banque existe
    bank_path = script_dir / "web" / "bank" / "bank.json"
    if not bank_path.exists():
        print("⚠️  Attention: bank.json non trouvé")
        print(f"   Chemin attendu: {bank_path}")
        print("   Exécutez d'abord: python3 -m bank.build_bank --sources-config sources/sources.yaml")
        print()
    
    # Trouver un port libre
    try:
        port = find_free_port(PORT)
    except RuntimeError as e:
        print(f"❌ Erreur: {e}")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
    
    # Créer le serveur HTTP
    handler = http.server.SimpleHTTPRequestHandler
    handler.extensions_map.update({
        ".js": "application/javascript",
        ".json": "application/json",
        ".html": "text/html",
        ".css": "text/css",
    })
    
    # Permettre la réutilisation du port
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    except OSError as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
    
    url = f"http://127.0.0.1:{port}{APP_PATH}"
    
    # Afficher les informations
    print("=" * 50)
    print("🦴 QCM Chiropraxie")
    print("=" * 50)
    print()
    print(f"✅ Serveur démarré sur le port {port}")
    print(f"🌐 URL: {url}")
    print()
    print("📝 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 50)
    
    # Ouvrir le navigateur dans un thread séparé (avec délai)
    def open_browser():
        import time
        time.sleep(0.5)
        webbrowser.open(url)
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Lancer le serveur
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté. À bientôt !")
        httpd.shutdown()


if __name__ == "__main__":
    main()
