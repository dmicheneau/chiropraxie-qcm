#!/usr/bin/env python3
"""
Lanceur QCM Chiropraxie

Double-cliquez sur ce fichier pour lancer l'application.
Ouvre automatiquement le navigateur sur l'interface de quiz.

Options:
  --debug    Affiche les logs détaillés dans la console
  --port N   Utilise le port N au lieu de 8080
"""

import http.server
import logging
import os
import socket
import socketserver
import sys
import threading
import traceback
import webbrowser
from datetime import datetime
from pathlib import Path

PORT = 8080
APP_PATH = "/app.html"

# Configuration logging
logger = logging.getLogger("QCM_Chiropraxie")


def get_base_path() -> Path:
    """Retourne le chemin de base des ressources.
    
    Gère le cas PyInstaller (_MEIPASS) et le cas script normal.
    """
    if getattr(sys, 'frozen', False):
        # Exécution depuis un bundle PyInstaller
        # Les ressources sont dans _MEIPASS
        base = Path(sys._MEIPASS)
        logger.debug(f"Mode PyInstaller: _MEIPASS = {base}")
    else:
        # Exécution normale (script Python)
        base = Path(__file__).parent.resolve()
        logger.debug(f"Mode script: base = {base}")
    return base


def get_log_path() -> Path:
    """Retourne le chemin du fichier de log."""
    if sys.platform == "darwin":
        log_dir = Path.home() / "Library" / "Logs" / "QCM_Chiropraxie"
    else:
        log_dir = Path.home() / ".qcm_chiropraxie" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"qcm_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logging(debug: bool = False):
    """Configure le système de logging."""
    log_path = get_log_path()
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler fichier (toujours actif)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler console (uniquement si --debug)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Configuration du logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("=" * 50)
    logger.info("QCM Chiropraxie - Démarrage")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    if debug:
        logger.info("Mode DEBUG activé")
    logger.info("=" * 50)


def find_free_port(start_port: int = 8080, max_tries: int = 100) -> int:
    """Trouve un port libre à partir de start_port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                logger.debug(f"Port {port} disponible")
                return port
            except OSError:
                logger.debug(f"Port {port} occupé")
                continue
    raise RuntimeError(f"Aucun port libre trouvé entre {start_port} et {start_port + max_tries}")


def show_error_dialog(title: str, message: str):
    """Affiche une boîte de dialogue d'erreur macOS."""
    try:
        import subprocess
        script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon stop'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception as e:
        logger.error(f"Impossible d'afficher la boîte de dialogue: {e}")


def main():
    # Parser les arguments
    debug_mode = "--debug" in sys.argv
    
    # Chercher --port N
    port_arg = PORT
    if "--port" in sys.argv:
        try:
            idx = sys.argv.index("--port")
            port_arg = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            pass
    
    # Configurer le logging
    setup_logging(debug=debug_mode)
    
    try:
        # Obtenir le chemin de base (gère PyInstaller)
        base_path = get_base_path()
        logger.info(f"Base path: {base_path}")
        
        # Lister les fichiers pour debug
        if debug_mode:
            logger.debug("Contenu du répertoire de base:")
            for item in sorted(base_path.iterdir()):
                logger.debug(f"  {item.name}{'/' if item.is_dir() else ''}")
        
        # Changer vers le répertoire de base
        os.chdir(base_path)
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Vérifier que app.html existe
        app_html = base_path / "app.html"
        if not app_html.exists():
            error_msg = f"app.html non trouvé dans {base_path}"
            logger.error(error_msg)
            show_error_dialog("Erreur QCM Chiropraxie", error_msg)
            sys.exit(1)
        logger.info(f"app.html trouvé: {app_html}")
        
        # Vérifier que la banque existe
        bank_path = base_path / "web" / "bank" / "bank.json"
        if not bank_path.exists():
            logger.warning(f"bank.json non trouvé: {bank_path}")
        else:
            logger.info(f"bank.json trouvé: {bank_path}")
        
        # Trouver un port libre
        port = find_free_port(port_arg)
        logger.info(f"Port sélectionné: {port}")
        
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
        
        httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
        logger.info("Serveur HTTP créé")
        
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
        if debug_mode:
            print(f"📋 Logs: {get_log_path()}")
        print("=" * 50)
        
        # Ouvrir le navigateur dans un thread séparé (avec délai)
        def open_browser():
            import time
            time.sleep(0.5)
            logger.info(f"Ouverture du navigateur: {url}")
            webbrowser.open(url)
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Lancer le serveur
        logger.info("Démarrage du serveur HTTP...")
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur (Ctrl+C)")
        print("\n\n👋 Serveur arrêté. À bientôt !")
    except Exception as e:
        error_msg = f"Erreur fatale: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        show_error_dialog("Erreur QCM Chiropraxie", str(e))
        if debug_mode:
            traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("Fin du programme")


if __name__ == "__main__":
    main()
