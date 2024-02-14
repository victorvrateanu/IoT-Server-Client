import time
import cv2
import face_recognition
import sys, os
import numpy as np
import math
import threading


def recunoastere(distanta, fata_gasita_threshold=0.6):
    range = (1.0 - fata_gasita_threshold)
    val_liniara = (1.0 - distanta) / (range * 2.0)

    if distanta > fata_gasita_threshold:
        return str(round(val_liniara * 100, 2)) + "%"
    else:
        valoare = (val_liniara + ((1.0 - val_liniara) * math.pow((val_liniara - 0.5) * 2, 0.2))) * 100
        return str(round(valoare, 2)) + "%"


class RecunoastereFaciala:
    locatie_fete = []
    fete_encodings = []
    fate_nume = []
    fete_cunoscute_encodings = []
    fete_cunoscute_nume = []
    procesare_fata_curenta = True
    flagTrimitereEmail = False

    def __init__(self):
        self.encode_fete()

    def encode_fete(self):
        for poze in os.listdir('detectare'):
            imagine_fata = face_recognition.load_image_file(f'detectare/{poze}')
            poze_encoding = face_recognition.face_encodings(imagine_fata)[0]

            self.fete_cunoscute_encodings.append(poze_encoding)
            self.fete_cunoscute_nume.append(poze)
        print(self.fete_cunoscute_nume)

    def setareFlag(self):
        self.flagTrimitereEmail = True
        time.sleep(30)
        self.flagTrimitereEmail = False

    def configurare_camera(self):
        flagDeTestare = False
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Camera nu a fost gasita")

        while True:

            ret, fereastra = camera.read()

            if self.procesare_fata_curenta:
                # fereastra pentru imagine mica si rgb
                fereastra_mica = cv2.resize(fereastra, (0, 0), fx=0.25, fy=0.25)
                rgb_fereastra_mica = cv2.cvtColor(fereastra_mica, cv2.COLOR_BGR2RGB)

                # gaseste fetele din imagine
                self.locatie_fete = face_recognition.face_locations(rgb_fereastra_mica)
                self.fete_encodings = face_recognition.face_encodings(rgb_fereastra_mica, self.locatie_fete)
                self.nume_fete = []
                for fete_encodings in self.fete_encodings:
                    recunoaste = face_recognition.compare_faces(self.fete_cunoscute_encodings, fete_encodings)
                    nume = 'Necunoscut'
                    rata_recunoastere = 'Necunoscut'

                    distanta_fata = face_recognition.face_distance(self.fete_cunoscute_encodings, fete_encodings)
                    best_recunoastere_index = np.argmin(distanta_fata)

                    if recunoaste[best_recunoastere_index]:
                        nume = self.fete_cunoscute_nume[best_recunoastere_index]
                        nume = nume.split('.')
                        nume = nume[0]
                        rata_recunoastere = recunoastere(distanta_fata[best_recunoastere_index])
                    # verifcia daca exista necunoscuti ca sa se salveze imaginea
                    if nume == 'Necunoscut' and self.flagTrimitereEmail is False:
                        cv2.imwrite('necunoscut.jpg', fereastra)
                        # thread care se asigura ca nu se trimit emailuri in intervale mai mici de 30 de secunde
                        threadFlag = threading.Thread(target=self.setareFlag)
                        threadFlag.start()
                    self.nume_fete.append(f'{nume}   ({rata_recunoastere})')
            self.procesare_fata_curenta = not self.procesare_fata_curenta

            # Arata informatii
            for (sus, dreapta, jos, stanga), nume in zip(self.locatie_fete, self.nume_fete):
                sus *= 4
                dreapta *= 4
                jos *= 4
                stanga *= 4

                cv2.rectangle(fereastra, (stanga, sus), (dreapta, jos), (0, 0, 255), 2)
                cv2.rectangle(fereastra, (stanga, jos - 35), (dreapta, jos), (0, 0, 255), -1)
                cv2.putText(fereastra, nume, (stanga + 6, jos - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Recunoastere faciala', fereastra)

            # iesire manuala
            if not flagDeTestare:
                flagDeTestare = True
                while True:
                    if cv2.waitKey(1) == ord('s'):
                        break
            if cv2.waitKey(1) == ord('q'):
                break
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    fr = RecunoastereFaciala()
    fr.configurare_camera()
