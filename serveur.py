
##################################Lien github:https://github.com/TchoupiRay/Examen-chat-serveur.git################################
import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QLabel, QTextEdit, QPushButton, QGridLayout

class serveur(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Le serveur de tchat")

        self.widget_central = QWidget(self)
        self.setCentralWidget(self.widget_central)

        self.layout = QGridLayout(self.widget_central)

        self.label_serveur = QLabel("Serveur", self)
        self.champ_serveur = QLineEdit("localhost", self)

        self.label_port = QLabel("Port", self)
        self.champ_port = QLineEdit("4200", self)

        self.label_clients = QLabel("Nombre de clients maximun", self)
        self.champ_clients = QLineEdit("5", self)

        self.zone_texte_clients = QTextEdit(self)
        self.zone_texte_clients.setReadOnly(True)

        self.bouton_demarrer = QPushButton("Démarrage du serveur", self)
        self.bouton_demarrer.clicked.connect(self.on_off_serveur)

        self.bouton_quitter = QPushButton("Quitter", self)
        self.bouton_quitter.clicked.connect(self.close)

        self.layout.addWidget(self.label_serveur, 0, 0)
        self.layout.addWidget(self.champ_serveur, 0, 1)

        self.layout.addWidget(self.label_port, 1, 0)
        self.layout.addWidget(self.champ_port, 1, 1)

        self.layout.addWidget(self.label_clients, 2, 0)
        self.layout.addWidget(self.champ_clients, 2, 1)

        self.layout.addWidget(self.bouton_demarrer, 3, 0, 1, 2)

        self.layout.addWidget(self.zone_texte_clients, 4, 0, 1, 2)

        self.layout.addWidget(self.bouton_quitter, 5, 0, 1, 2)

        self.socket_serveur = None
        self.sockets_clients = []
        self.serveur_en_cours = False

    def on_off_serveur(self):
        if self.serveur_en_cours:
            self.arreter_serveur()
        else:
            self.demarrer_serveur()

    def demarrer_serveur(self):
        ip_serveur = self.champ_serveur.text()
        port = int(self.champ_port.text())
        max_clients = int(self.champ_clients.text())

        try:
            self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_serveur.bind((ip_serveur, port))
            self.socket_serveur.listen(max_clients)

            self.serveur_en_cours = True
            self.bouton_demarrer.setText("Arrêt du serveur")
            self.zone_texte_clients.append(f"Serveur démarré en {ip_serveur}:{port}.\n")

            thread_accepter_clients = threading.Thread(target=self.accepter_clients)
            thread_accepter_clients.start()

        except Exception as e:
            self.zone_texte_clients.append(f"Erreur de démarrage du serveur : {e}\n")

    def arreter_serveur(self):
        if self.socket_serveur:
            self.socket_serveur.close()
            self.serveur_en_cours = False
            self.bouton_demarrer.setText("Démarrage du serveur")
            self.zone_texte_clients.append("Serveur arrêté.\n")

            for socket_client in self.sockets_clients:
                socket_client.close()

    def accepter_clients(self):
        while self.serveur_en_cours:
            try:
                socket_client, adresse_client = self.socket_serveur.accept()
                self.sockets_clients.append(socket_client)

                self.zone_texte_clients.append(f"Client connecté: {adresse_client}\n")

                thread_client = threading.Thread(target=self.recevoir_messages, args=(socket_client,))
                thread_client.start()

            except Exception as e:
                if self.serveur_en_cours:
                    self.zone_texte_clients.append(f"Erreur d'un client: {e}\n")

    def recevoir_messages(self, socket_client):
        while self.serveur_en_cours:
            try:
                message = socket_client.recv(1024).decode("utf-8")

                if message == "deco-server":
                    self.zone_texte_clients.append("Client déconnecté.\n")
                    self.sockets_clients.remove(socket_client)
                    socket_client.close()
                    break
                elif message:
                    self.zone_texte_clients.append(f"Message reçu: {message}\n")

            except Exception as e:
                self.zone_texte_clients.append(f"Erreur de réception d'un message: {e}\n")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = serveur()
    fenetre.show()
    sys.exit(app.exec())
