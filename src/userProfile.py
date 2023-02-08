from operator import add
import numpy as np
from operator import add
import pandas as pd

FILE="data_antoine.tsv"
NOM_AGE=["18-25","25-35","35-45","45-55","55-70","70+"]
BABIES=["YES","NO"]
RESTAURANTS=["cheap","medium","expensive"]
ADJUSTED_TYPES=[
 "Artistic",
 "Convenience",
 "Drinks",
 "AffordableAccomodation",
 "HotelAccomodation",
 "Leisure",
 "LocalCulture",
 "NaturalHeritage",
 "Neutral",
 "SitDown",
 "SportsPlace",
 "TakeAway",
 "Tour",
 "CulturalBuilding"]


 
def get_meta_profiles(file):
    colnames=[" "*k for k in range(11) ] 
    df = pd.read_csv(file,names=colnames, sep="\t")   # read dummy .tsv file into memory
    a = df.values
    for row in range(len(a)):
        for elem in range(len(a[row])):
            a[row,elem]=float(str(a[row,elem]).replace(",","."))
    profils_age,profils_babies,profil_restaurants={},{},{}
    i=0
    for k in range(len(NOM_AGE)):
        profils_age[NOM_AGE[k]]=a[:,k]
        i+=1
    for k in range(len(BABIES)):
        profils_babies[BABIES[k]]=a[:,i]
        i+=1
    for k in range(len(RESTAURANTS)):
        profil_restaurants[RESTAURANTS[k]]=a[:,i]
        i+=1
    profils_category={}
    for k in range(len(ADJUSTED_TYPES)):
        profils_category[ADJUSTED_TYPES[k]]=[1 if i==k else 0 for i in range(len(ADJUSTED_TYPES)) ]
    return profils_age,profils_babies,profil_restaurants,profils_category




def genere_profil_utilisateur(age_group,children,affordable,categories,file=FILE):
    profils_age,profils_babies,profil_restaurants ,profils_category= get_meta_profiles(file)
    profil_age,profil_child,profil_affordable=np.array(profils_age[age_group]),np.array(profils_babies[children]),np.array(profil_restaurants[affordable])
    profil_category = [0 for k in profil_age]
    total = 0
    for k in range(len(categories)):
        profil=categories[k]
        #its more complicated than needed but it works. good enough
        profil_category= [profil_category[i]+profil[1]*profils_category[profil[0]][i] for i in range(len(profil_category))]
    profil_category=np.array(profil_category)
    profil=np.multiply(np.multiply(profil_age,profil_child),profil_affordable) + profil_category  
    return profil



# here is what the different inputs are programmed to take
# age_group="18-25"         #["18-25","25-35","35-45","45-55","55-70","70+"]
# children="NO"
# categories=[("Artistic",5),("NaturalHeritage",3),("LocalCulture",2)]               # choose k among CATEGORIES_AVAILABLE_IN_Q4 : "Artistic", "Drinks", "Leisure", "LocalCulture", "NaturalHeritage", "SportsPlace", "Tour", "CulturalBuilding"
# affordable = "cheap"  