import customtkinter as ctk
import os
from functii_voce import creaza_folder_utilizator, inregistreaza_voce, salveaza_voce, extract_mfcc, salveaza_caracteristici_mfcc, compara_caracteristici,sterge_inregistrare

class Aplicatie(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Recunoastere vocala- autentificare")
        self.geometry("800x600")
        self.base_path = 'C:\\Users\\calit\\Music\\MPT_Proiect\\Voce'
        self.nume_utilizator = None
        self.folder_utilizator = None

        self.main_menu = ctk.CTkFrame(self)
        self.main_menu.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(self.main_menu, text="Selectează opțiunea:", font=("Arial", 18))
        self.label.pack(pady=20)

        self.new_user_btn = ctk.CTkButton(self.main_menu, text="Utilizator Nou", command=self.utilizator_nou)
        self.new_user_btn.pack(pady=10)

        self.existing_user_btn = ctk.CTkButton(self.main_menu, text="Utilizator Existent", command=self.utilizator_existent)
        self.existing_user_btn.pack(pady=10)

    def utilizator_nou(self):
        self.main_menu.pack_forget()
        self.afiseaza_formular("Utilizator Nou")

    def utilizator_existent(self):
        self.main_menu.pack_forget()
        self.afiseaza_formular("Utilizator Existent")

    def afiseaza_formular(self, tip_utilizator):
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="both", expand=True)

        mesaj = f"{tip_utilizator}: Introdu numele tău"
        self.label = ctk.CTkLabel(self.form_frame, text=mesaj, font=("Arial", 18))
        self.label.pack(pady=20)

        self.nume_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Numele utilizatorului")
        self.nume_entry.pack(pady=10, padx=20)

        self.confirm_btn = ctk.CTkButton(self.form_frame, text="Confirmă", command=lambda: self.confirmare_nume(tip_utilizator))
        self.confirm_btn.pack(pady=20)

        self.back_btn = ctk.CTkButton(self.form_frame, text="Înapoi", command=self.revenire_meniu)
        self.back_btn.pack(pady=10)

    def confirmare_nume(self, tip_utilizator):
        nume = self.nume_entry.get().strip()
        if nume:
            self.nume_utilizator = nume
            self.folder_utilizator = os.path.join(self.base_path, nume)

            if tip_utilizator == "Utilizator Nou":
                creaza_folder_utilizator(base_path=self.base_path, nume_utilizator=nume)
                self.afiseaza_inregistrare()
            elif tip_utilizator == "Utilizator Existent":
                if os.path.exists(self.folder_utilizator):
                    self.afiseaza_verificare()
                else:
                    self.afiseaza_mesaj(f"Utilizatorul '{nume}' nu există!")
        else:
            self.afiseaza_mesaj("Nume invalid!")

    def afiseaza_inregistrare(self):
        self.form_frame.pack_forget()
        self.record_frame = ctk.CTkFrame(self)
        self.record_frame.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(self.record_frame, text="Pentru a accesa baza noastra de date, este necesar să înregistrezi un mesaj vocal de 10 secunde", font=("Arial", 18))
        self.label.pack(pady=20)

        self.record_btn = ctk.CTkButton(self.record_frame, text="Înregistreaza (10s)", command=self.inregistrare_voce)
        self.record_btn.pack(pady=10)

    def inregistrare_voce(self):
        try:
            voce = inregistreaza_voce(duration=10, sample_rate=44100)
            save_path = os.path.join(self.folder_utilizator, f"{self.nume_utilizator}.wav")
            salveaza_voce(voce, 44100, save_path)

            mfcc_features = extract_mfcc(voce.flatten(), 44100)
            salveaza_caracteristici_mfcc(mfcc_features, self.folder_utilizator, self.nume_utilizator)

            self.afiseaza_mesaj("Înregistrare completă! Acum te afli in baza de date!")
        except Exception as e:
            self.afiseaza_mesaj(f"Eroare la înregistrare: {str(e)}")

    def afiseaza_verificare(self):
        self.form_frame.pack_forget()
        self.verify_frame = ctk.CTkFrame(self)
        self.verify_frame.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(self.verify_frame, text="Pentru a continua vă rugăm să înregistrați un mesaj vocal", font=("Arial", 18))
        self.label.pack(pady=20)

        self.verify_btn = ctk.CTkButton(self.verify_frame, text="Verificare voce", command=self.verificare_voce)
        self.verify_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self.verify_frame, text="Înapoi", command=self.revenire_meniu)
        self.back_btn.pack(pady=10)

    def verificare_voce(self):
        try:
            rezultat, similaritate = compara_caracteristici(
                base_path=self.base_path,
                nume_utilizator=self.nume_utilizator,
                duration=10,
                sample_rate=44100,
                n_mfcc=20
            )

            if rezultat:
                self.afiseaza_mesaj(f"Vocea este similara, cu o similaritate: {similaritate:.2f}")
                self.afiseaza_optiuni_autentificat()
            else:
                self.afiseaza_mesaj(f"Vocea nu este similara. Similaritate: {similaritate:.2f}")
        except Exception as e:
            self.afiseaza_mesaj(f"Eroare la verificare: {str(e)}")

    def afiseaza_optiuni_autentificat(self):
        """
        Afișează opțiunile de gestionare a înregistrării doar dacă utilizatorul este autentificat.
        """
        for widget in self.winfo_children():
            widget.pack_forget()

        self.authenticated_frame = ctk.CTkFrame(self)
        self.authenticated_frame.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(self.authenticated_frame, text="Meniu", font=("Arial", 18))
        self.label.pack(pady=20)

        self.replace_btn = ctk.CTkButton(self.authenticated_frame, text="Înlocuiește inregistrarea cu una noua", command=self.inlocuieste_inregistrarea)
        self.replace_btn.pack(pady=10)

        self.delete_folder_btn = ctk.CTkButton(self.authenticated_frame, text="Șterge inregistrarea", command=self.sterge_folder)
        self.delete_folder_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self.authenticated_frame, text="Înapoi", command=self.revenire_meniu)
        self.back_btn.pack(pady=10)
    

    def inlocuieste_inregistrarea(self):
        try:
            sterge_inregistrare(self.folder_utilizator, self.nume_utilizator)

            voce = inregistreaza_voce(duration=10, sample_rate=44100)
            save_path = os.path.join(self.folder_utilizator, f"{self.nume_utilizator}.wav")
            salveaza_voce(voce, 44100, save_path)

            mfcc_features = extract_mfcc(voce.flatten(), 44100)
            salveaza_caracteristici_mfcc(mfcc_features, self.folder_utilizator, self.nume_utilizator)

            self.afiseaza_mesaj("Înregistrarea a fost înlocuită cu succes.")
        except Exception as e:
            self.afiseaza_mesaj(f"Eroare la înlocuire: {str(e)}")

    def afiseaza_mesaj(self, mesaj):
        for widget in self.winfo_children():
            widget.pack_forget()

        final_frame = ctk.CTkFrame(self)
        final_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(final_frame, text=mesaj, font=("Arial", 18))
        label.pack(pady=50)

    def sterge_folder(self):
        """
        Șterge întregul folder al utilizatorului.
        """
        try:
            sterge_inregistrare(self.folder_utilizator, self.nume_utilizator, sterge_folder=True)
            self.afiseaza_mesaj("Folderul utilizatorului a fost șters cu succes.")
        except Exception as e:
            self.afiseaza_mesaj(f"Eroare la ștergerea folderului: {str(e)}")



    def revenire_meniu(self):
        for widget in self.winfo_children():
            widget.pack_forget()

        self.main_menu.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()