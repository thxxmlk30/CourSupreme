import pandas as pd
import random
from faker import Faker
from datetime import datetime
import os

faker = Faker('fr_FR')

PRENOMS_MASCULINS = ["Mamadou", "Ibrahima", "Abdoulaye", "Ousmane", "Alioune", "Cheikh", "Saliou", "Modou", "Fallou", "Amadou", "Babacar", "Moussa", "Serigne"]
PRENOMS_FEMININS = ["Aissatou", "Fatou", "Aminata", "Mariama", "Ndeye", "Khady", "Binta", "Coumba", "Awa", "Oumou", "Astou", "Mame", "Rama"]
NOMS_DE_FAMILLE = ["Ndiaye", "Diop", "Fall", "Faye", "Gueye", "Sall", "Ba", "Sow", "Diallo", "Seck", "Thiam", "Diagne", "Touré", "Cissé", "Sy", "Mbaye", "Sarr", "Wade", "Gningue", "Ndoye"]
VILLES_SENEGAL = ["Dakar", "Thiès", "Saint-Louis", "Ziguinchor", "Diourbel", "Kaolack", "Louga", "Tambacounda", "Kolda", "Fatick", "Matam", "Kaffrine", "Kédougou", "Sédhiou", "Touba", "Rufisque", "Mbour", "Tivaouane"]

def generer_fichier_electoral(nom_fichier="fichier_electoral.xlsx", nombre_electeurs=10000):
    print(f"Génération du fichier électoral avec {nombre_electeurs} électeurs...")
    donnees = []
    for _ in range(nombre_electeurs):
        sexe = random.choice(['M', 'F'])
        if sexe == 'M':
            prenom = random.choice(PRENOMS_MASCULINS)
        else:
            prenom = random.choice(PRENOMS_FEMININS)
        
        nom = random.choice(NOMS_DE_FAMILLE)
        
        # Âge entre 18 et 90 ans
        date_naissance = faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%d/%m/%Y')
        lieu_naissance = random.choice(VILLES_SENEGAL)
        
        # Le Numéro d'Identification Nationale (NIN) au Sénégal fait 13 chiffres (exemple)
        # Typiquement: 1 (ou 2 pour femme) + année de naissance (4) + code centre (4) + numéro d'ordre (4)
        annee = date_naissance[-4:]
        premier_chiffre = '1' if sexe == 'M' else '2'
        reste_nin = str(faker.random_number(digits=8, fix_len=True))
        nin = premier_chiffre + annee + reste_nin
        
        adresse = f"Quartier {faker.word().capitalize()}, {lieu_naissance}"
        
        donnees.append({
            'Prénom': prenom,
            'Nom': nom,
            'Date de naissance': date_naissance,
            'Sexe': sexe,
            'Lieu de naissance': lieu_naissance,
            'Numéro d\'identification nationale': nin,
            'Adresse': adresse
        })
    
    df = pd.DataFrame(donnees)
    df.to_excel(nom_fichier, index=False)
    print(f"Fichier sauvegardé : {nom_fichier}")
    return df

def generer_fichier_parrainages(df_electoral, nom_fichier="parrainages.xlsx", nombre_parrains=500, nombre_corrompus=0):
    print(f"Génération du fichier de parrainage avec {nombre_parrains} valides et {nombre_corrompus} non inscrits...")
    
    # Sélectionner des parrains valides depuis le fichier électoral
    parrains_valides = df_electoral.sample(n=nombre_parrains).copy()
    
    # Générer des faux parrains (qui ne sont pas dans le fichier)
    donnees_invalides = []
    for _ in range(nombre_corrompus):
        sexe = random.choice(['M', 'F'])
        prenom = random.choice(PRENOMS_MASCULINS) if sexe == 'M' else random.choice(PRENOMS_FEMININS)
        nom = random.choice(NOMS_DE_FAMILLE)
        date_naissance = faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%d/%m/%Y')
        lieu_naissance = random.choice(VILLES_SENEGAL)
        nin = "9" + str(faker.random_number(digits=12, fix_len=True)) # Faux NIN qui commence par 9
        adresse = f"Quartier {faker.word().capitalize()}, {lieu_naissance}"
        
        donnees_invalides.append({
            'Prénom': prenom,
            'Nom': nom,
            'Date de naissance': date_naissance,
            'Sexe': sexe,
            'Lieu de naissance': lieu_naissance,
            'Numéro d\'identification nationale': nin,
            'Adresse': adresse
        })
    
    if donnees_invalides:
        df_invalide = pd.DataFrame(donnees_invalides)
        df_final = pd.concat([parrains_valides, df_invalide]).sample(frac=1).reset_index(drop=True)
    else:
        df_final = parrains_valides.sample(frac=1).reset_index(drop=True)
        
    df_final.to_excel(nom_fichier, index=False)
    print(f"Fichier sauvegardé : {nom_fichier}")

if __name__ == "__main__":
    fichier_principal = "fichier_electoral.xlsx"
    if not os.path.exists(fichier_principal):
        df_electoral = generer_fichier_electoral(fichier_principal, 10000)
    else:
        print(f"Chargement de {fichier_principal} existant...")
        df_electoral = pd.read_excel(fichier_principal)
        
    # Entre 0.8% et 1% de 10000 = entre 80 et 100
    generer_fichier_parrainages(df_electoral, "parrainages_candidat1_valide.xlsx", nombre_parrains=90, nombre_corrompus=0)
    generer_fichier_parrainages(df_electoral, "parrainages_candidat2_insuffisant.xlsx", nombre_parrains=50, nombre_corrompus=0)
    generer_fichier_parrainages(df_electoral, "parrainages_candidat3_exces.xlsx", nombre_parrains=150, nombre_corrompus=0)
    generer_fichier_parrainages(df_electoral, "parrainages_candidat4_faux_nins.xlsx", nombre_parrains=70, nombre_corrompus=20)
