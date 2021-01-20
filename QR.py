import pyzbar.pyzbar as pyzbar
import cv2
import json
import sys
import shutil, os

def main():
    #Prélèvement du chemin associé au répertoire contenant les documents à traiter
    pathdir = sys.argv[1]
    pathdir = os.path.abspath(pathdir)

    # scan des fichier contenus dans le répertoire choisi et sockage de leurs noms dans une liste
    filelist = os.listdir(pathdir)

    # Création des répertoires ARCHIVES et JSON s'ils n'existe pas
    pathdirarchives = pathdir+"/ARCHIVES"
    pathdirjsonfiles = pathdir+"/JSON"
    try:
        os.mkdir(pathdirarchives)
    except OSError:
        if not os.path.isdir(pathdirarchives):
            raise

    try:
        os.mkdir(pathdirjsonfiles)
    except OSError:
        if not os.path.isdir(pathdirjsonfiles):
            raise


    # Liste des types de fichier supportés par le script
    filetypesaccepted = ["png","PNG"]

    #Initialisation des compteurs de fichiers traités et de QR codes scannés
    countfile = 0
    countscan = 0


    #Traitement des docuements trouvés dans le répertoire choisi
    for documentname in filelist:
        # vérification du type du fichier afin de ne traiter seulement les documents png
        filetab = documentname.split(".")

        if filetab[-1] not in filetypesaccepted:
            continue

        countfile += 1

        # Préparation du nom du fichier Json associé au document en cours de traiement
        namejsonfile = filetab[0] + "_" + filetab[1] + ".json"
        pathfile = pathdir+"/"+documentname



        # dictionnaire dans lequel les données des QR codes contenus dans celui-ci seront stockées
        documentdict = {}
        documentdict["filename"] = documentname
        documentdict["QRCODES"] = []

        # Lecture du fichier png
        img = cv2.imread(pathfile)
        # Extraction des QR Codes contenus dans le document encours de traitement et leur stockage dans une liste
        QRcodesList = pyzbar.decode(img)

        #Initialisation du compteur de QR codes scannés
        countscancode = 0

        #Traitement des QR codes contenus dans le document en cours de traitement
        for QRcode in QRcodesList:
            countscancode += 1

            #Extraction des données contenues dans le QR code en cours de traitement et conversion de celui-ci en dictionnaire
            data = QRcode.data.decode("utf-8")
            datadict = json.loads(data)

            #Construction d'un dictionnaire accueillant les données du QR Code en cours de traitement
            dataqrcodestructured = {}
            dataqrcodestructured["numdos"] = datadict["data"]["numdos"]
            dataqrcodestructured["version"] = datadict["version"]
            dataqrcodestructured["context"] = datadict["context"]
            dataqrcodestructured["typedoc"] = datadict["data"]["typedoc"]

            # Ajout du dictionnaire du QRCode en cours de traiteùent dans le dictionnaire associé au docuement en cours de traitement
            documentdict["QRCODES"].append(dataqrcodestructured)

        # Création et écriture sur disque du fichier JSON contenant les données du document en cours de traitement
        with open(pathdirjsonfiles+"/"+namejsonfile, "w") as f:
            json.dump(documentdict,f, indent=4)

        # Déplacement du document traité dans répertoire ARCHIVE, ce document est titré du préfixe READ_
        shutil.move(pathfile, pathdir+"/ARCHIVES/"+"READ_"+documentname)

        countscan += countscancode

    # Affichage du repporting  sur console

    print(str(countfile) + " files found")
    print(str(countscan) + " QR code scanned")
    print("END")


if __name__ == "__main__":
    main()
