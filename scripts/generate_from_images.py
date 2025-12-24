#!/usr/bin/env python3
"""
Script de génération de QCM à partir des descriptions d'images et colorations
Génère des questions sur les colorations histologiques, les schémas anatomiques,
et les caractéristiques visuelles décrites dans les PDFs.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


# Questions basées sur les colorations et techniques histologiques
# décrites dans le PDF "Tissus Conjonctifs"
IMAGE_BASED_QUESTIONS = [
    # Colorations histologiques
    {
        "prompt": "La coloration à l'orcéine met en évidence quel type de fibres conjonctives ?",
        "choices": [
            {"key": "A", "text": "Fibres élastiques (couleur brun-violet)"},
            {"key": "B", "text": "Fibres collagènes (couleur rose)"},
            {"key": "C", "text": "Fibres réticulées (couleur noire)"},
            {"key": "D", "text": "Fibres de fibrine (couleur jaune)"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Techniques histologiques",
        "image_reference": "Schéma coloration orcéine"
    },
    {
        "prompt": "L'imprégnation argentique (coloration de Gomori) permet de visualiser :",
        "choices": [
            {"key": "A", "text": "Les fibres réticulées (réticuline) en noir"},
            {"key": "B", "text": "Les fibres élastiques en brun"},
            {"key": "C", "text": "Les fibres collagènes en bleu"},
            {"key": "D", "text": "Le noyau des cellules en violet"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Techniques histologiques",
        "image_reference": "Imprégnation argentique"
    },
    {
        "prompt": "En coloration HES (Hématoxyline-Éosine-Safran), les fibres collagènes apparaissent :",
        "choices": [
            {"key": "A", "text": "En rose (éosinophiles)"},
            {"key": "B", "text": "En bleu-violet (basophiles)"},
            {"key": "C", "text": "En noir (argentophiles)"},
            {"key": "D", "text": "En jaune (chromophiles)"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Techniques histologiques"
    },
    {
        "prompt": "Les granulations des mastocytes sont mises en évidence par :",
        "choices": [
            {"key": "A", "text": "Le bleu de toluidine (métachromasie)"},
            {"key": "B", "text": "L'orcéine"},
            {"key": "C", "text": "L'imprégnation argentique"},
            {"key": "D", "text": "La coloration de Masson"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Mastocytes"
    },
    {
        "prompt": "Le phénomène de métachromasie observé avec le bleu de toluidine est dû à :",
        "choices": [
            {"key": "A", "text": "La forte concentration de GAG sulfatés dans les granulations"},
            {"key": "B", "text": "La présence de collagène de type I"},
            {"key": "C", "text": "L'accumulation de lipides"},
            {"key": "D", "text": "La richesse en fibres élastiques"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Mastocytes"
    },
    
    # Caractéristiques morphologiques des cellules
    {
        "prompt": "Sur une coupe histologique, un adipocyte blanc se reconnaît par :",
        "choices": [
            {"key": "A", "text": "Une grande vacuole lipidique unique avec noyau refoulé en périphérie"},
            {"key": "B", "text": "De multiples petites vacuoles et un noyau central"},
            {"key": "C", "text": "Un cytoplasme basophile avec REG abondant"},
            {"key": "D", "text": "L'absence de membrane plasmique visible"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Adipocytes",
        "image_reference": "Schéma adipocyte blanc vs brun"
    },
    {
        "prompt": "Sur une coupe histologique, un adipocyte brun se caractérise par :",
        "choices": [
            {"key": "A", "text": "Multiples vacuoles lipidiques et nombreuses mitochondries"},
            {"key": "B", "text": "Une seule grande vacuole lipidique"},
            {"key": "C", "text": "Un noyau excentré et peu de cytoplasme"},
            {"key": "D", "text": "L'absence de mitochondries"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Adipocytes"
    },
    {
        "prompt": "Le fibroblaste actif se distingue du fibrocyte par :",
        "choices": [
            {"key": "A", "text": "Un REG développé et un noyau euchromatique (clair)"},
            {"key": "B", "text": "Un noyau hétérochromatique (sombre) et peu de cytoplasme"},
            {"key": "C", "text": "La présence de vacuoles lipidiques"},
            {"key": "D", "text": "Des granulations métachromatiques"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Fibroblastes"
    },
    {
        "prompt": "Le myofibroblaste se reconnaît en microscopie électronique par :",
        "choices": [
            {"key": "A", "text": "La présence de filaments d'actine et de myosine"},
            {"key": "B", "text": "L'absence de REG"},
            {"key": "C", "text": "Des vacuoles lipidiques multiples"},
            {"key": "D", "text": "Un noyau polylobé"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Myofibroblastes"
    },
    {
        "prompt": "Sur une coupe histologique, un plasmocyte se reconnaît par :",
        "choices": [
            {"key": "A", "text": "Un noyau excentré en 'cadran d'horloge' et cytoplasme basophile"},
            {"key": "B", "text": "Des granulations métachromatiques"},
            {"key": "C", "text": "Une grande vacuole lipidique unique"},
            {"key": "D", "text": "Un noyau polylobé et cytoplasme acidophile"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Plasmocytes"
    },
    
    # Organisation tissulaire
    {
        "prompt": "Sur une coupe de TC dense orienté (tendon), les fibres collagènes apparaissent :",
        "choices": [
            {"key": "A", "text": "Parallèles les unes aux autres, dans le même sens"},
            {"key": "B", "text": "Entrecroisées dans toutes les directions"},
            {"key": "C", "text": "En réseau autour des cellules"},
            {"key": "D", "text": "Absentes, remplacées par de l'élastine"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - TC dense",
        "image_reference": "Coupe de tendon"
    },
    {
        "prompt": "Sur une coupe de derme (TC dense non orienté), les fibres collagènes sont :",
        "choices": [
            {"key": "A", "text": "Entrecroisées dans toutes les directions"},
            {"key": "B", "text": "Strictement parallèles"},
            {"key": "C", "text": "Absentes, remplacées par des fibres élastiques"},
            {"key": "D", "text": "Organisées en réseau régulier hexagonal"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - TC dense"
    },
    {
        "prompt": "Le TC lâche se reconnaît histologiquement par :",
        "choices": [
            {"key": "A", "text": "Une substance fondamentale abondante et des fibres peu denses"},
            {"key": "B", "text": "Des fibres collagènes très serrées et parallèles"},
            {"key": "C", "text": "L'absence de cellules"},
            {"key": "D", "text": "Une prédominance de fibres élastiques"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - TC lâche"
    },
    {
        "prompt": "Le TC réticulé (stroma des organes hématopoïétiques) se caractérise par :",
        "choices": [
            {"key": "A", "text": "Un réseau de fibres réticulées (collagène III) formant une trame"},
            {"key": "B", "text": "Des fibres collagènes denses et orientées"},
            {"key": "C", "text": "Une prédominance d'adipocytes"},
            {"key": "D", "text": "L'absence de substance fondamentale"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - TC réticulé"
    },
    
    # Cartilage
    {
        "prompt": "Sur une coupe de cartilage hyalin, les chondrocytes sont disposés :",
        "choices": [
            {"key": "A", "text": "En groupes isogéniques (chondrones) dans des lacunes"},
            {"key": "B", "text": "De façon isolée et dispersée"},
            {"key": "C", "text": "En colonnes parallèles uniquement"},
            {"key": "D", "text": "À la surface du cartilage exclusivement"}
        ],
        "answer": "A",
        "tags": ["Histologie_Cartilage"],
        "source": "PDF Tissus Conjonctifs - Cartilage",
        "image_reference": "Coupe cartilage hyalin"
    },
    {
        "prompt": "Le périchondre entoure le cartilage et contient :",
        "choices": [
            {"key": "A", "text": "Une couche externe fibreuse et une couche interne chondrogène"},
            {"key": "B", "text": "Uniquement des adipocytes"},
            {"key": "C", "text": "Des chondrocytes matures exclusivement"},
            {"key": "D", "text": "Du tissu osseux compact"}
        ],
        "answer": "A",
        "tags": ["Histologie_Cartilage"],
        "source": "PDF Tissus Conjonctifs - Cartilage"
    },
    {
        "prompt": "Le cartilage élastique se distingue du cartilage hyalin par :",
        "choices": [
            {"key": "A", "text": "La présence de fibres élastiques visibles à l'orcéine"},
            {"key": "B", "text": "L'absence de chondrocytes"},
            {"key": "C", "text": "Une vascularisation abondante"},
            {"key": "D", "text": "La présence de fibres collagènes de type I"}
        ],
        "answer": "A",
        "tags": ["Histologie_Cartilage"],
        "source": "PDF Tissus Conjonctifs - Types de cartilage"
    },
    {
        "prompt": "Le fibrocartilage (cartilage fibreux) se caractérise par :",
        "choices": [
            {"key": "A", "text": "La présence de fibres collagènes de type I entre les chondrocytes"},
            {"key": "B", "text": "L'absence totale de collagène"},
            {"key": "C", "text": "Une matrice entièrement élastique"},
            {"key": "D", "text": "Un périchondre très développé"}
        ],
        "answer": "A",
        "tags": ["Histologie_Cartilage"],
        "source": "PDF Tissus Conjonctifs - Types de cartilage"
    },
    
    # Tissus spécialisés
    {
        "prompt": "Sur un frottis sanguin, les hématies se reconnaissent par :",
        "choices": [
            {"key": "A", "text": "Leur forme de disque biconcave et l'absence de noyau"},
            {"key": "B", "text": "Leur noyau polylobé"},
            {"key": "C", "text": "Leurs granulations basophiles"},
            {"key": "D", "text": "Leur grande taille (50 µm)"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Tissu sanguin",
        "image_reference": "Frottis sanguin"
    },
    {
        "prompt": "Le cordon ombilical contient un type particulier de TC appelé :",
        "choices": [
            {"key": "A", "text": "TC muqueux (gelée de Wharton)"},
            {"key": "B", "text": "TC dense orienté"},
            {"key": "C", "text": "TC adipeux brun"},
            {"key": "D", "text": "TC réticulé"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - TC muqueux",
        "image_reference": "Coupe cordon ombilical"
    },
    
    # Schémas anatomiques du MS
    {
        "prompt": "Sur un schéma de la fosse axillaire, l'espace quadrangulaire laisse passer :",
        "choices": [
            {"key": "A", "text": "Le n. axillaire et les vaisseaux circonflexes postérieurs de l'humérus"},
            {"key": "B", "text": "Le n. radial et l'artère brachiale profonde"},
            {"key": "C", "text": "Le n. médian et l'artère brachiale"},
            {"key": "D", "text": "Le n. ulnaire et l'artère ulnaire"}
        ],
        "answer": "A",
        "tags": ["Neurologie_MS", "Angiologie_MS"],
        "source": "PDF UE2.2 - Espaces axillaires",
        "image_reference": "Schéma espaces axillaires"
    },
    {
        "prompt": "L'espace huméro-tricipital (triangulaire inférieur) laisse passer :",
        "choices": [
            {"key": "A", "text": "Le n. radial et l'artère brachiale profonde"},
            {"key": "B", "text": "Le n. axillaire et les vaisseaux circonflexes"},
            {"key": "C", "text": "Le n. médian et l'artère brachiale"},
            {"key": "D", "text": "Le n. musculo-cutané"}
        ],
        "answer": "A",
        "tags": ["Neurologie_MS", "Angiologie_MS"],
        "source": "PDF UE2.2 - Espaces axillaires"
    },
    {
        "prompt": "Sur un schéma du plexus brachial, les racines proviennent de :",
        "choices": [
            {"key": "A", "text": "C5, C6, C7, C8 et T1"},
            {"key": "B", "text": "C1, C2, C3, C4 et C5"},
            {"key": "C", "text": "T1, T2, T3, T4 et T5"},
            {"key": "D", "text": "L1, L2, L3, L4 et L5"}
        ],
        "answer": "A",
        "tags": ["Neurologie_MS"],
        "source": "PDF UE2.2 - Plexus brachial",
        "image_reference": "Schéma plexus brachial"
    },
    {
        "prompt": "Sur un schéma du plexus brachial, les troncs primaires sont au nombre de :",
        "choices": [
            {"key": "A", "text": "3 (supérieur, moyen, inférieur)"},
            {"key": "B", "text": "2 (antérieur, postérieur)"},
            {"key": "C", "text": "5 (un par racine)"},
            {"key": "D", "text": "4 (latéral, médial, postérieur, antérieur)"}
        ],
        "answer": "A",
        "tags": ["Neurologie_MS"],
        "source": "PDF UE2.2 - Plexus brachial"
    },
    {
        "prompt": "Le canal carpien contient tous ces éléments SAUF :",
        "choices": [
            {"key": "A", "text": "Le nerf ulnaire"},
            {"key": "B", "text": "Le nerf médian"},
            {"key": "C", "text": "Les tendons des fléchisseurs des doigts"},
            {"key": "D", "text": "Le tendon du long fléchisseur du pouce"}
        ],
        "answer": "A",
        "tags": ["Neurologie_MS"],
        "source": "PDF UE2.2 - Canal carpien",
        "image_reference": "Coupe transversale du poignet"
    },
    
    # Schémas du MI
    {
        "prompt": "Sur un schéma de l'os coxal, l'acétabulum est formé par la jonction de :",
        "choices": [
            {"key": "A", "text": "L'ilium, l'ischium et le pubis"},
            {"key": "B", "text": "L'ilium et le sacrum"},
            {"key": "C", "text": "L'ischium et le coccyx"},
            {"key": "D", "text": "Le pubis et le sacrum"}
        ],
        "answer": "A",
        "tags": ["Osteologie_MI"],
        "source": "PDF UE2.2 - Os coxal",
        "image_reference": "Schéma os coxal"
    },
    {
        "prompt": "Sur un schéma du fémur, le petit trochanter reçoit l'insertion de :",
        "choices": [
            {"key": "A", "text": "Le muscle ilio-psoas"},
            {"key": "B", "text": "Le muscle grand fessier"},
            {"key": "C", "text": "Le muscle quadriceps"},
            {"key": "D", "text": "Le muscle sartorius"}
        ],
        "answer": "A",
        "tags": ["Osteologie_MI", "Myologie_MI"],
        "source": "PDF UE2.2 - Fémur",
        "image_reference": "Schéma fémur proximal"
    },
    
    # Tissu Nerveux
    {
        "prompt": "Sur une coupe de nerf périphérique, l'endonèvre entoure :",
        "choices": [
            {"key": "A", "text": "Chaque fibre nerveuse individuellement"},
            {"key": "B", "text": "Un fascicule entier de fibres"},
            {"key": "C", "text": "Le nerf entier"},
            {"key": "D", "text": "La gaine de myéline uniquement"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Nerveux", "Neurologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC nerveux"
    },
    {
        "prompt": "Le périnèvre entoure :",
        "choices": [
            {"key": "A", "text": "Un fascicule de fibres nerveuses"},
            {"key": "B", "text": "Chaque fibre nerveuse"},
            {"key": "C", "text": "Le nerf entier"},
            {"key": "D", "text": "Le corps cellulaire du neurone"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Nerveux", "Neurologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC nerveux"
    },
    {
        "prompt": "L'épinèvre constitue :",
        "choices": [
            {"key": "A", "text": "L'enveloppe conjonctive externe du nerf entier"},
            {"key": "B", "text": "La gaine de myéline"},
            {"key": "C", "text": "L'enveloppe de chaque fibre"},
            {"key": "D", "text": "La membrane du corps cellulaire"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Nerveux", "Neurologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC nerveux"
    },
    
    # Tissu Musculaire
    {
        "prompt": "Sur une coupe transversale de muscle strié squelettique, l'endomysium entoure :",
        "choices": [
            {"key": "A", "text": "Chaque fibre musculaire"},
            {"key": "B", "text": "Un fascicule musculaire"},
            {"key": "C", "text": "Le muscle entier"},
            {"key": "D", "text": "Le tendon"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Musculaire", "Myologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC musculaire"
    },
    {
        "prompt": "Le périmysium entoure :",
        "choices": [
            {"key": "A", "text": "Un faisceau de fibres musculaires"},
            {"key": "B", "text": "Chaque fibre musculaire"},
            {"key": "C", "text": "Le muscle entier"},
            {"key": "D", "text": "Le sarcomère"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Musculaire", "Myologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC musculaire"
    },
    {
        "prompt": "L'épimysium constitue :",
        "choices": [
            {"key": "A", "text": "L'enveloppe conjonctive du muscle entier"},
            {"key": "B", "text": "La membrane de chaque fibre"},
            {"key": "C", "text": "La lame basale du sarcolemme"},
            {"key": "D", "text": "Le disque Z du sarcomère"}
        ],
        "answer": "A",
        "tags": ["Histologie_Tissu_Musculaire", "Myologie_MS"],
        "source": "PDF Tissus Conjonctifs - TC musculaire"
    },
    
    # Jonctions et lame basale
    {
        "prompt": "Sur un schéma de lame basale, la lamina densa est composée principalement de :",
        "choices": [
            {"key": "A", "text": "Collagène de type IV"},
            {"key": "B", "text": "Collagène de type I"},
            {"key": "C", "text": "Élastine"},
            {"key": "D", "text": "Réticuline"}
        ],
        "answer": "A",
        "tags": ["Histologie_Jonctions", "Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Lame basale",
        "image_reference": "Schéma lame basale"
    },
    {
        "prompt": "Les intégrines sont des récepteurs transmembranaires qui permettent :",
        "choices": [
            {"key": "A", "text": "L'adhésion des cellules à la matrice extracellulaire"},
            {"key": "B", "text": "Le transport des ions"},
            {"key": "C", "text": "La synthèse de collagène"},
            {"key": "D", "text": "La dégradation des GAG"}
        ],
        "answer": "A",
        "tags": ["Histologie_Jonctions", "Histologie_Tissu_Conjonctif"],
        "source": "PDF Tissus Conjonctifs - Intégrines"
    },
]

# Questions supplémentaires sur Biologie Cellulaire et Embryologie
BIOLOGY_QUESTIONS = [
    # Biologie Cellulaire
    {
        "prompt": "La membrane plasmique est principalement constituée de :",
        "choices": [
            {"key": "A", "text": "Une bicouche de phospholipides avec des protéines"},
            {"key": "B", "text": "Une couche simple de collagène"},
            {"key": "C", "text": "Du cytosquelette d'actine"},
            {"key": "D", "text": "De l'ADN et des histones"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Les mitochondries sont responsables de :",
        "choices": [
            {"key": "A", "text": "La production d'ATP par phosphorylation oxydative"},
            {"key": "B", "text": "La synthèse des protéines"},
            {"key": "C", "text": "Le stockage du calcium uniquement"},
            {"key": "D", "text": "La division cellulaire"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Le réticulum endoplasmique rugueux (REG) est caractérisé par :",
        "choices": [
            {"key": "A", "text": "La présence de ribosomes sur sa membrane"},
            {"key": "B", "text": "L'absence de membrane"},
            {"key": "C", "text": "La synthèse des lipides"},
            {"key": "D", "text": "La production d'ATP"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "L'appareil de Golgi a pour fonction principale :",
        "choices": [
            {"key": "A", "text": "La modification et le tri des protéines"},
            {"key": "B", "text": "La synthèse de l'ADN"},
            {"key": "C", "text": "La production d'énergie"},
            {"key": "D", "text": "La division cellulaire"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Les lysosomes contiennent :",
        "choices": [
            {"key": "A", "text": "Des enzymes hydrolytiques pour la digestion intracellulaire"},
            {"key": "B", "text": "De l'ADN mitochondrial"},
            {"key": "C", "text": "Des ribosomes"},
            {"key": "D", "text": "Du calcium uniquement"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Le noyau cellulaire contient :",
        "choices": [
            {"key": "A", "text": "L'ADN et le nucléole"},
            {"key": "B", "text": "Les mitochondries"},
            {"key": "C", "text": "L'appareil de Golgi"},
            {"key": "D", "text": "Les lysosomes"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Le cytosquelette est composé de :",
        "choices": [
            {"key": "A", "text": "Microfilaments d'actine, microtubules et filaments intermédiaires"},
            {"key": "B", "text": "Collagène uniquement"},
            {"key": "C", "text": "ADN et ARN"},
            {"key": "D", "text": "Phospholipides"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    {
        "prompt": "Les ribosomes sont responsables de :",
        "choices": [
            {"key": "A", "text": "La synthèse des protéines"},
            {"key": "B", "text": "La réplication de l'ADN"},
            {"key": "C", "text": "La production d'ATP"},
            {"key": "D", "text": "Le stockage des lipides"}
        ],
        "answer": "A",
        "tags": ["Biologie_Cellulaire"],
        "source": "Biologie cellulaire"
    },
    
    # Embryologie
    {
        "prompt": "La gastrulation permet la formation de :",
        "choices": [
            {"key": "A", "text": "Trois feuillets embryonnaires (ectoblaste, mésoblaste, endoblaste)"},
            {"key": "B", "text": "La morula"},
            {"key": "C", "text": "Le blastocyste uniquement"},
            {"key": "D", "text": "Les annexes extra-embryonnaires"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "Le mésoblaste donne naissance à :",
        "choices": [
            {"key": "A", "text": "Les tissus conjonctifs, muscles et système cardiovasculaire"},
            {"key": "B", "text": "L'épiderme et le système nerveux"},
            {"key": "C", "text": "L'épithélium digestif"},
            {"key": "D", "text": "L'épithélium respiratoire"}
        ],
        "answer": "A",
        "tags": ["Embryologie", "Histologie_Tissu_Conjonctif"],
        "source": "Embryologie"
    },
    {
        "prompt": "L'ectoblaste donne naissance à :",
        "choices": [
            {"key": "A", "text": "L'épiderme et le système nerveux"},
            {"key": "B", "text": "Les muscles et le squelette"},
            {"key": "C", "text": "L'épithélium digestif"},
            {"key": "D", "text": "Le cœur et les vaisseaux"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "L'endoblaste donne naissance à :",
        "choices": [
            {"key": "A", "text": "L'épithélium du tube digestif et des voies respiratoires"},
            {"key": "B", "text": "Le système nerveux"},
            {"key": "C", "text": "Les muscles squelettiques"},
            {"key": "D", "text": "Le derme"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "La neurulation correspond à :",
        "choices": [
            {"key": "A", "text": "La formation du tube neural à partir de l'ectoblaste"},
            {"key": "B", "text": "La formation du cœur"},
            {"key": "C", "text": "La segmentation de l'œuf"},
            {"key": "D", "text": "L'implantation du blastocyste"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "Les somites dérivent du :",
        "choices": [
            {"key": "A", "text": "Mésoblaste para-axial"},
            {"key": "B", "text": "Ectoblaste"},
            {"key": "C", "text": "Endoblaste"},
            {"key": "D", "text": "Trophoblaste"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "Le blastocyste est composé de :",
        "choices": [
            {"key": "A", "text": "Le trophoblaste et l'embryoblaste (masse cellulaire interne)"},
            {"key": "B", "text": "Uniquement de cellules musculaires"},
            {"key": "C", "text": "Le tube neural"},
            {"key": "D", "text": "Les trois feuillets embryonnaires"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
    {
        "prompt": "L'implantation du blastocyste se fait au niveau de :",
        "choices": [
            {"key": "A", "text": "L'endomètre utérin"},
            {"key": "B", "text": "Les trompes de Fallope"},
            {"key": "C", "text": "L'ovaire"},
            {"key": "D", "text": "Le col de l'utérus"}
        ],
        "answer": "A",
        "tags": ["Embryologie"],
        "source": "Embryologie"
    },
]


def main():
    print("=" * 60)
    print("🖼️ Génération de QCM basées sur images et colorations")
    print("=" * 60)
    
    # Combiner toutes les questions
    all_questions = IMAGE_BASED_QUESTIONS + BIOLOGY_QUESTIONS
    print(f"\n📊 {len(all_questions)} questions générées")
    
    # Compter par tag
    tag_counts = {}
    for q in all_questions:
        for tag in q.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\n📈 Distribution par thème:")
    for tag, count in sorted(tag_counts.items()):
        print(f"  - {tag}: {count}")
    
    # Écrire dans un fichier Deck
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / "web" / "decks" / "Deck_Generated_Images.md"
    
    lines = [
        "# Deck: Questions basées sur images et colorations",
        "",
        f"**Générées automatiquement** : {len(all_questions)} questions",
        "**Sources** : PDFs Tissus Conjonctifs et UE2.2 - Descriptions visuelles",
        "",
        "---",
        ""
    ]
    
    for i, q in enumerate(all_questions, 1):
        tags_str = f" [Tags: {', '.join(q.get('tags', []))}]"
        lines.append(f"{i}) {q['prompt']}{tags_str}")
        for choice in q.get("choices", []):
            lines.append(f"- {choice['key']}. {choice['text']}")
        lines.append(f"**Réponse** : {q.get('answer', 'A')}")
        if q.get("image_reference"):
            lines.append(f"*Référence image* : {q['image_reference']}")
        lines.append("")
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Écrit {len(all_questions)} questions dans {output_path.name}")
    
    # Écrire aussi en JSON
    json_output = repo_root / "sources" / "generated_images.json"
    json_output.parent.mkdir(exist_ok=True)
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump({"questions": all_questions}, f, ensure_ascii=False, indent=2)
    print(f"✅ Écrit JSON dans {json_output.name}")
    
    print("\n✅ Génération terminée!")
    print("💡 Exécutez 'python3 bank/build_bank.py' pour intégrer ces questions")


if __name__ == "__main__":
    main()
