import os
import sounddevice 
import sounddevice as sd
import soundfile as sf
import librosa
import numpy
from sklearn.metrics.pairwise import cosine_similarity

import shutil


def creaza_folder_utilizator(base_path='C:\\Users\\calit\\Music\\MPT_Proiect\\Voce', nume_utilizator=None):
    user_folder = os.path.join(base_path, nume_utilizator)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


def inregistreaza_voce(duration=10, sample_rate=44100):
    voce_captata = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return voce_captata


def salveaza_voce(voce, sample_rate, save_path):
    sf.write(save_path, voce, sample_rate)


def extract_mfcc(audio, sample_rate, n_mfcc=20):
    mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta_delta = librosa.feature.delta(mfcc, order=2)
    features = numpy.concatenate((numpy.mean(mfcc.T, axis=0),
                                   numpy.mean(delta.T, axis=0),
                                   numpy.mean(delta_delta.T, axis=0)))
    return features


def salveaza_caracteristici_mfcc(mfcc_features, folder_utilizator, nume_utilizator):
    mfcc_path = os.path.join(folder_utilizator, f"{nume_utilizator}_mfcc.txt")
    with open(mfcc_path, 'w') as f:
        f.write("\n".join(map(str, mfcc_features)))


def preproceseaza_audio(audio, sample_rate):
    audio_trimmed, _ = librosa.effects.trim(audio)
    if len(audio_trimmed) == 0:
        raise ValueError("Semnalul audio este gol după eliminarea pauzelor.")
    audio_normalized = librosa.util.normalize(audio_trimmed)
    return audio_normalized


def compara_caracteristici(base_path, nume_utilizator, duration=10, sample_rate=44100, n_mfcc=20, prag=0.98):
    folder_utilizator = os.path.join(base_path, nume_utilizator)
    mfcc_path = os.path.join(folder_utilizator, f"{nume_utilizator}_mfcc.txt")

    if not os.path.exists(mfcc_path):
        raise FileNotFoundError(f"Fișierul MFCC pentru utilizatorul '{nume_utilizator}' nu există.")

    voce_captata = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()

    audio_flat = voce_captata.flatten()
    audio_preprocessed = preproceseaza_audio(audio_flat, sample_rate)
    mfcc_nou = extract_mfcc(audio_preprocessed, sample_rate, n_mfcc)

    with open(mfcc_path, 'r') as f:
        mfcc_salvat = numpy.array([float(line.strip()) for line in f.readlines()])

    if len(mfcc_nou) != len(mfcc_salvat):
        raise ValueError("Dimensiunea caracteristicilor MFCC nu este compatibilă.")

    similaritate = cosine_similarity([mfcc_nou], [mfcc_salvat])[0][0]
    if similaritate >= prag:
        return True, similaritate
    else:
        return False, similaritate


def sterge_inregistrare(folder_utilizator, nume_utilizator, sterge_folder=False):
    """
    Șterge fișierele asociate utilizatorului: fișierul audio și caracteristicile MFCC.
    """
    try:
        if sterge_folder:
            # Șterge întregul folder
            if os.path.exists(folder_utilizator):
                shutil.rmtree(folder_utilizator)
                print(f"Folderul {folder_utilizator} a fost șters.")
            else:
                print(f"Folderul {folder_utilizator} nu există.")
        else:
            # Șterge doar fișierele individuale
            audio_path = os.path.join(folder_utilizator, f"{nume_utilizator}.wav")
            mfcc_path = os.path.join(folder_utilizator, f"{nume_utilizator}_mfcc.txt")

            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Fișierul audio {audio_path} a fost șters.")
            if os.path.exists(mfcc_path):
                os.remove(mfcc_path)
                print(f"Fișierul MFCC {mfcc_path} a fost șters.")
    except Exception as e:
        print(f"Eroare la ștergerea fișierelor sau folderului: {e}")

        