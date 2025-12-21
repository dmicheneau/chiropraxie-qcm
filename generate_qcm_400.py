from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass(frozen=True)
class QItem:
    stem: str
    options: Tuple[str, str, str, str]
    answer_index: int  # 0..3
    explanation: str


LETTERS = ("A", "B", "C", "D")


def _q(stem: str, options: List[str], answer_index: int, explanation: str = "") -> QItem:
    if len(options) != 4:
        raise ValueError("Each question must have 4 options")
    if not (0 <= answer_index <= 3):
        raise ValueError("answer_index must be 0..3")
    return QItem(stem=stem.strip(), options=tuple(o.strip() for o in options), answer_index=answer_index, explanation=explanation.strip())


def _shuffle_options(rng: random.Random, item: QItem) -> QItem:
    opts = list(item.options)
    correct = opts[item.answer_index]
    rng.shuffle(opts)
    new_answer = opts.index(correct)
    return QItem(stem=item.stem, options=tuple(opts), answer_index=new_answer, explanation=item.explanation)


def build_connective_tissue_bank() -> List[QItem]:
    # Basé sur le PDF “Tissus conjonctifs” fourni (extraction texte).
    bank: List[QItem] = []

    # Généralités
    bank += [
        _q(
            "Sur le plan embryologique, les tissus conjonctifs dérivent principalement :",
            [
                "Du mésoblaste via le mésenchyme",
                "Du neuroectoderme",
                "De l’endoderme",
                "D’un tissu épithélial spécialisé",
            ],
            0,
            "Le cours précise la dérivation du mésoblaste via le mésenchyme.",
        ),
        _q(
            "Dans un tissu conjonctif, les 3 grandes catégories d’éléments sont :",
            [
                "Fibres conjonctives, substance fondamentale, cellules conjonctives",
                "Cellules épithéliales, hématies, cartilage",
                "Fibres musculaires, myéline, ostéons",
                "Synapses, neurones, microglie",
            ],
            0,
            "Fibres + substance fondamentale + cellules.",
        ),
        _q(
            "La matrice extracellulaire (MEC) est constituée de :",
            [
                "Fibres + substance fondamentale",
                "Cellules résidentes + cellules importées",
                "Fibroblastes + mastocytes uniquement",
                "Vaisseaux + nerfs uniquement",
            ],
            0,
            "Le cours définit MEC = fibres + substance fondamentale.",
        ),
        _q(
            "Une fonction métabolique des tissus conjonctifs est liée surtout à :",
            [
                "Leur richesse en vaisseaux sanguins",
                "L’absence de substance fondamentale",
                "La présence exclusive de fibres élastiques",
                "La minéralisation de la matrice",
            ],
            0,
            "Fonction métabolique = échanges nutritifs via vascularisation.",
        ),
        _q(
            "La fonction de défense des tissus conjonctifs est liée notamment à :",
            [
                "La présence de cellules immunitaires de passage",
                "La présence d’ostéocytes",
                "La présence de chondrocytes",
                "La présence de kératinocytes",
            ],
            0,
            "Cellules mobiles/importées (immunité) participent à la défense.",
        ),
    ]

    # Substance fondamentale / GAG / protéoglycanes
    bank += [
        _q(
            "La substance fondamentale d’un tissu conjonctif est classiquement décrite comme :",
            [
                "Semi-fluide, située entre cellules et fibres",
                "Toujours rigide et minéralisée",
                "Absente de la MEC",
                "Exclusivement constituée de collagène",
            ],
            0,
            "Le cours: consistance semi-fluide entre cellules et fibres.",
        ),
        _q(
            "Les glycosaminoglycanes (GAG) sont :",
            [
                "De longues chaînes glucidiques non ramifiées",
                "Des protéines globulaires",
                "Des lipides membranaires",
                "Des acides nucléiques",
            ],
            0,
            "Définition donnée dans le cours.",
        ),
        _q(
            "Un disaccharide de base des GAG comporte typiquement :",
            [
                "Un acide uronique et une hexosamine",
                "Un acide aminé et un ribose",
                "Un phosphate et un cholestérol",
                "Une base azotée et un désoxyribose",
            ],
            0,
            "Le cours mentionne acide uronique + hexosamine.",
        ),
        _q(
            "Parmi les GAG, lequel est spécifiquement décrit comme non sulfaté et présent dans tous les TC ?",
            [
                "Acide hyaluronique",
                "Dermatane sulfate",
                "Chondroïtine sulfate",
                "Héparane sulfate",
            ],
            0,
            "Acide hyaluronique: non sulfaté, ubiquitaire.",
        ),
        _q(
            "Concernant l’acide hyaluronique (cours) :",
            [
                "Il ne se fixe pas à des protéines et ne constitue pas de protéoglycanes",
                "Il est toujours sulfaté",
                "Il est spécifique de la lame basale",
                "Il est un type de collagène",
            ],
            0,
            "Le cours: ne se fixe pas à des protéines.",
        ),
        _q(
            "L’enzyme citée qui hydrolyse l’acide hyaluronique est :",
            [
                "Hyaluronidase",
                "Collagénase",
                "Élastase",
                "Amylase",
            ],
            0,
            "Le cours mentionne l’hyaluronidase.",
        ),
        _q(
            "L’hydrolyse de l’acide hyaluronique tend à :",
            [
                "Diminuer la viscosité et augmenter la perméabilité tissulaire",
                "Augmenter la viscosité et diminuer la perméabilité",
                "Minéraliser la matrice",
                "Supprimer les fibres collagènes",
            ],
            0,
            "Effet décrit dans le cours.",
        ),
        _q(
            "Un protéoglycane est (cours) :",
            [
                "Des chaînes de GAG fixées à une protéine porteuse par liaisons covalentes",
                "Une fibre de collagène",
                "Une intégrine membranaire",
                "Une hématie an nucléée",
            ],
            0,
            "Définition du cours.",
        ),
        _q(
            "Les agrégats de protéoglycanes se fixent sur une molécule de :",
            [
                "Acide hyaluronique (liaisons non covalentes)",
                "Collagène IV",
                "Fibrilline",
                "Élastine",
            ],
            0,
            "Organisation en agrégats sur acide hyaluronique.",
        ),
        _q(
            "Les protéoglycanes sont très hydrophiles principalement en raison de :",
            [
                "Leur richesse en charges négatives",
                "Leur absence de glucides",
                "Leur forte teneur en lipides",
                "La présence de collagène IV",
            ],
            0,
            "Charges négatives = pièges à eau.",
        ),
        _q(
            "Dans le cours, l’importance des protéoglycanes pour le cartilage est surtout liée à :",
            [
                "La résistance aux forces de compression",
                "La résistance exclusive à la traction",
                "La conduction nerveuse",
                "La minéralisation osseuse",
            ],
            0,
            "Pièges à eau → propriétés mécaniques en compression.",
        ),
        _q(
            "Une mucopolysaccharidose est décrite comme :",
            [
                "Une maladie de surcharge lysosomiale par déficit enzymatique",
                "Une infection bactérienne aiguë",
                "Un cancer épithélial spécifique",
                "Une fracture de fatigue",
            ],
            0,
            "Déficit enzymatique → accumulation de GAG.",
        ),
    ]

    # Glycoprotéines / intégrines
    bank += [
        _q(
            "Les glycoprotéines de la MEC (cours) participent surtout à :",
            [
                "L’ancrage des cellules sur la MEC",
                "La minéralisation du tissu osseux",
                "La formation des hématies",
                "La conduction des potentiels d’action",
            ],
            0,
            "Rôle d’adhérence/ancrage.",
        ),
        _q(
            "Exemple correct (cours) de glycoprotéine reliant cellules et collagène :",
            [
                "Fibronectine",
                "Élastine",
                "Réticuline",
                "Chondroïtine sulfate",
            ],
            0,
            "Fibronectine: liaison cellules–collagène.",
        ),
        _q(
            "Les laminines sont décrites comme spécifiques de :",
            [
                "La lame basale",
                "La diaphyse humérale",
                "Le plasma sanguin",
                "Les ostéons",
            ],
            0,
            "Cours: laminines spécifiques de la lame basale.",
        ),
        _q(
            "Dans le cours, la fibrilline est associée à :",
            [
                "Les fibres élastiques",
                "Les fibres réticulées",
                "Les fibres collagènes type II uniquement",
                "Les protéoglycanes sulfatés",
            ],
            0,
            "Fibrilline = composante des fibres élastiques.",
        ),
        _q(
            "Les intégrines (rappel du cours) sont :",
            [
                "Des récepteurs membranaires dimériques (sous-unités α et β)",
                "Des enzymes lysosomiales",
                "Des hormones de satiété",
                "Des fibres de collagène",
            ],
            0,
            "Cours: dimères α/β.",
        ),
    ]

    # Fibres conjonctives / collagènes
    bank += [
        _q(
            "Les fibres conjonctives se déclinent (cours) en trois variétés principales :",
            [
                "Collagènes, réticulées, élastiques",
                "Osseuses, cartilagineuses, nerveuses",
                "Épithéliales, musculaires, sanguines",
                "Minéralisées, non minéralisées, kératinisées",
            ],
            0,
            "Trois variétés: collagènes, réticulées, élastiques.",
        ),
        _q(
            "Les collagènes confèrent surtout :",
            [
                "Une résistance mécanique à la traction",
                "Une conductivité électrique",
                "Une capacité de phagocytose",
                "Une élasticité pure sans résistance",
            ],
            0,
            "Traction.",
        ),
        _q(
            "Dans le cours, le collagène de type I représente environ :",
            [
                "90% du collagène de l’organisme",
                "5% du collagène de l’organisme",
                "Uniquement le collagène du cartilage",
                "Uniquement le collagène de la lame basale",
            ],
            0,
            "Cours: type I ~90%.",
        ),
        _q(
            "Le collagène de type II est localisé principalement :",
            [
                "Dans le cartilage",
                "Dans la lame basale",
                "Uniquement dans le sang",
                "Uniquement dans l’épiderme",
            ],
            0,
            "Type II: cartilage.",
        ),
        _q(
            "Le collagène de type III correspond à :",
            [
                "La réticuline (fibres réticulées)",
                "L’élastine",
                "La fibronectine",
                "La kératine",
            ],
            0,
            "Type III = réticuline.",
        ),
        _q(
            "Le collagène de type IV (cours) :",
            [
                "Est spécifique des lames basales et ne forme pas de fibres",
                "Constitue le tendon et le ligament",
                "Est le collagène principal du cartilage",
                "Est un GAG sulfaté",
            ],
            0,
            "Type IV: lame basale, larges mailles.",
        ),
        _q(
            "Les fibres réticulées (réticulines) :",
            [
                "S’assemblent en réseaux anastomosés",
                "Sont exclusivement présentes dans la peau",
                "Ne sont jamais associées aux organes lymphoïdes",
                "Sont constituées d’élastine",
            ],
            0,
            "Réseaux anastomosés.",
        ),
        _q(
            "Localisation typique des fibres réticulées (cours) :",
            [
                "Organes hématopoïétiques/lymphoïdes (ex. moelle osseuse)",
                "Cornée uniquement",
                "Épiderme uniquement",
                "Dents uniquement",
            ],
            0,
            "Moelle osseuse, thymus, rate, ganglions…",
        ),
        _q(
            "Les fibres élastiques (cours) sont mises en évidence par une coloration à :",
            [
                "L’orcéine",
                "L’hématoxyline-éosine uniquement",
                "La PAS uniquement",
                "Le rouge Congo",
            ],
            0,
            "Cours: orcéine.",
        ),
        _q(
            "Les fibres élastiques sont constituées :",
            [
                "D’un cœur d’élastine et d’une périphérie de fibrilline",
                "D’un cœur de collagène I et d’une périphérie de collagène II",
                "De GAG sulfatés uniquement",
                "D’actine et de myosine",
            ],
            0,
            "Ultrastructure: élastine centrale, fibrilline périphérique.",
        ),
        _q(
            "Une propriété décrite des fibres élastiques (cours) :",
            [
                "Elles ne se renouvellent pas",
                "Elles se renouvellent en quelques jours",
                "Elles sont minéralisées",
                "Elles sont exclusivement intracellulaires",
            ],
            0,
            "Cours: pas de renouvellement → rides.",
        ),
    ]

    # Cellules conjonctives
    bank += [
        _q(
            "Les cellules conjonctives résidentes incluent :",
            [
                "Fibroblastes, myofibroblastes, adipocytes",
                "Hématies, plaquettes, lymphocytes",
                "Chondrocytes uniquement",
                "Neurones et astrocytes",
            ],
            0,
            "Résidentes: fibroblastes, myofibroblastes, adipocytes.",
        ),
        _q(
            "Les cellules conjonctives importées sont principalement :",
            [
                "D’origine médullaire hématopoïétique",
                "D’origine épithéliale",
                "D’origine cartilagineuse",
                "D’origine endodermique",
            ],
            0,
            "Cours: origine médullaire hématopoïétique.",
        ),
        _q(
            "Le fibroblaste se distingue du fibrocyte (cours) par :",
            [
                "Une activité métabolique plus élevée",
                "L’absence de noyau",
                "Une fonction de transport d’oxygène",
                "Une localisation exclusive dans le sang",
            ],
            0,
            "Fibroblaste actif vs fibrocyte quiescent.",
        ),
        _q(
            "Les fibroblastes synthétisent :",
            [
                "Toutes les macromolécules constitutives de la MEC",
                "Uniquement l’histamine",
                "Uniquement les anticorps",
                "Uniquement l’hémoglobine",
            ],
            0,
            "Cours: synthèse MEC; surproduction → fibrose.",
        ),
        _q(
            "Les myofibroblastes possèdent notamment :",
            [
                "Des filaments contractiles d’actine et de myosine",
                "De la myéline",
                "Des disques intercalaires",
                "De l’hémoglobine",
            ],
            0,
            "Morphologie intermédiaire muscle lisse/fibroblaste.",
        ),
        _q(
            "Dans le cours, un rôle des myofibroblastes est :",
            [
                "Participation à la réparation/guérison et à l’inflammation",
                "Transport des gaz respiratoires",
                "Production d’anticorps",
                "Conduction synaptique",
            ],
            0,
            "Réparation, chimiotactisme, inflammation.",
        ),
        _q(
            "Les macrophages (histiocytes) sont décrits comme :",
            [
                "Des monocytes sortis du sang et différenciés dans les tissus",
                "Des fibroblastes quiescents",
                "Des adipocytes plurivacuolaires",
                "Des hématies anucléées",
            ],
            0,
            "Monocytes → macrophages; phagocytose.",
        ),
        _q(
            "Les plasmocytes sont :",
            [
                "Des lymphocytes B maturés sécrétant des Ig",
                "Des cellules musculaires lisses",
                "Des cellules endothéliales",
                "Des cellules épithéliales",
            ],
            0,
            "Cours: défense spécifique, anticorps.",
        ),
        _q(
            "Les mastocytes sont classiquement :",
            [
                "Riches en granulations basophiles contenant de l’histamine",
                "Riches en hémoglobine",
                "Dépourvus de granulations",
                "Exclusivement intra-osseux",
            ],
            0,
            "Cours: histamine, réactions allergiques.",
        ),
    ]

    # Adipocytes / sang
    bank += [
        _q(
            "Concernant l’adipocyte blanc (cours) :",
            [
                "Univacuolaire et de grande taille (≈100 µm)",
                "Plurivacuolaire et riche en mitochondries",
                "Toujours entouré d’une lame basale épaisse minéralisée",
                "Exclusivement présent chez le fœtus",
            ],
            0,
            "Adipocyte blanc: univacuolaire, grand.",
        ),
        _q(
            "Concernant l’adipocyte brun (cours) :",
            [
                "Plurivacuolaire, nombreuses mitochondries, thermogenèse",
                "Univacuolaire, sans mitochondries",
                "Uniquement chez l’adulte",
                "Fonction principale: production d’Ig",
            ],
            0,
            "Graisse brune: chaleur (fœtus/nouveau-né).",
        ),
        _q(
            "Le tissu sanguin est décrit comme un tissu conjonctif spécialisé caractérisé par :",
            [
                "Une matrice liquide (plasma)",
                "Une matrice minéralisée",
                "Une matrice cartilagineuse",
                "Une absence totale de cellules",
            ],
            0,
            "Plasma = matrice liquide.",
        ),
        _q(
            "Dans le cours, la proportion des éléments figurés du sang est d’environ :",
            [
                "45%",
                "5%",
                "90%",
                "100%",
            ],
            0,
            "Cours: 45% éléments figurés, 55% plasma.",
        ),
        _q(
            "Les hématies sont décrites comme :",
            [
                "Des cellules anucléées",
                "Des cellules plurinucléées",
                "Des fragments cellulaires",
                "Des cellules sécrétrices d’histamine",
            ],
            0,
            "Hématies = anucléées.",
        ),
        _q(
            "Les plaquettes (thrombocytes) sont :",
            [
                "Des fragments cellulaires",
                "Des cellules épithéliales",
                "Des fibres de collagène",
                "Des GAG sulfatés",
            ],
            0,
            "Cours: fragments cellulaires.",
        ),
    ]

    # Types de tissus conjonctifs
    bank += [
        _q(
            "Le tissu conjonctif muqueux est surtout important :",
            [
                "Chez l’embryon (cordon ombilical)",
                "Chez l’adulte au niveau des tendons",
                "Uniquement dans la moelle osseuse",
                "Uniquement dans la lame basale",
            ],
            0,
            "Cours: cordon ombilical.",
        ),
        _q(
            "Le tissu conjonctif lâche est caractérisé (cours) par :",
            [
                "Une substance fondamentale prédominante et des fibres non orientées",
                "Une absence de substance fondamentale",
                "Une matrice minéralisée",
                "Des faisceaux de collagène orientés dans une seule direction",
            ],
            0,
            "TC lâche: SF majeure, fibres sans orientation.",
        ),
        _q(
            "Localisation citée du tissu conjonctif lâche (cours) :",
            [
                "Entre les cellules musculaires striées (endomysium)",
                "Uniquement dans la dure-mère",
                "Uniquement dans le stroma cornéen",
                "Uniquement dans les ligaments jaunes",
            ],
            0,
            "Endomysium.",
        ),
        _q(
            "Le tissu conjonctif dense irrégulier (non orienté) présente :",
            [
                "Des faisceaux de collagène dans toutes les directions",
                "Des fibres orientées dans une seule direction",
                "Une matrice liquide",
                "Une prédominance cellulaire (adipocytes)",
            ],
            0,
            "Cours: faisceaux épais multi-directionnels.",
        ),
        _q(
            "Exemple de localisation d’un TC dense irrégulier (cours) :",
            [
                "Dure-mère",
                "Cordon ombilical",
                "Plasma sanguin",
                "Cartilage hyalin",
            ],
            0,
            "Dure-mère et gaines de gros nerfs.",
        ),
        _q(
            "Le TC dense régulier unitendu est typiquement retrouvé dans :",
            [
                "Tendons et ligaments",
                "Derme papillaire",
                "Moelle osseuse",
                "Parois des grosses artères élastiques uniquement",
            ],
            0,
            "Fibres orientées 1 direction.",
        ),
        _q(
            "Le TC dense régulier bitendu est cité dans le cours comme :",
            [
                "Stroma cornéen / aponévroses",
                "Cordon ombilical",
                "Ganglion lymphatique",
                "Endomysium",
            ],
            0,
            "Deux directions perpendiculaires.",
        ),
        _q(
            "Le TC fibreux à prédominance de fibres élastiques est cité dans :",
            [
                "Les ligaments jaunes et la paroi des grosses artères élastiques",
                "Le cartilage hyalin uniquement",
                "Le sang uniquement",
                "La lame basale uniquement",
            ],
            0,
            "Cours: ligaments jaunes + artères élastiques.",
        ),
        _q(
            "Le tissu conjonctif réticulé est caractérisé par :",
            [
                "Un maillage de fibres réticulées (collagène type III) et peu/pas de SF",
                "Une matrice minéralisée",
                "Une prédominance d’élastine",
                "Une matrice liquide",
            ],
            0,
            "Charpente réticulée.",
        ),
    ]

    return bank


def build_ue22_upper_limb_bank() -> List[QItem]:
    # Basé sur l’extraction du PDF UE2.2 (plexus brachial + nerfs/angiologie MS).
    bank: List[QItem] = []

    bank += [
        _q(
            "De manière générale, de la moelle émergent :",
            [
                "Une racine antérieure motrice et une racine postérieure sensitive",
                "Deux racines motrices",
                "Deux racines sensitives",
                "Une seule racine mixte",
            ],
            0,
            "PDF UE2.2: antérieure motrice, postérieure sensitive (ganglion spinal).",
        ),
        _q(
            "La branche postérieure du nerf spinal (dans le cours) est aussi appelée :",
            [
                "PPD (posterior primary division)",
                "APD (anterior primary division)",
                "Lame basale",
                "Corde postérieure",
            ],
            0,
            "Terminologie du cours.",
        ),
        _q(
            "Le plexus brachial est formé des APD de :",
            [
                "C5 à T1",
                "C1 à C4",
                "T1 à T5",
                "C3 à C7",
            ],
            0,
            "UE2.2: C5–T1.",
        ),
        _q(
            "Le tronc supérieur du plexus brachial est formé par :",
            [
                "C5 et C6",
                "C7 seul",
                "C8 et T1",
                "C6 et C7",
            ],
            0,
            "C5+C6.",
        ),
        _q(
            "Les divisions postérieures innervent préférentiellement :",
            [
                "Les loges postérieures (extenseurs)",
                "Les loges antérieures (fléchisseurs)",
                "Le diaphragme",
                "La peau palmaire uniquement",
            ],
            0,
            "UE2.2: postérieures = extenseurs.",
        ),
        _q(
            "La corde postérieure est formée :",
            [
                "Des 3 divisions postérieures",
                "Des divisions antérieures des troncs sup et moyen",
                "De la division antérieure du tronc inférieur",
                "Des racines C5 à T1 non mélangées",
            ],
            0,
            "UE2.2: 3 divisions postérieures.",
        ),
        _q(
            "Le nerf musculo-cutané provient :",
            [
                "De la corde latérale",
                "De la corde médiale",
                "De la corde postérieure",
                "Du tronc inférieur directement",
            ],
            0,
            "UE2.2: musculo-cutané = corde latérale.",
        ),
        _q(
            "Le nerf ulnaire provient :",
            [
                "De la corde médiale",
                "De la corde latérale",
                "De la corde postérieure",
                "Du tronc supérieur",
            ],
            0,
            "UE2.2: ulnaire = corde médiale.",
        ),
        _q(
            "Le nerf radial provient :",
            [
                "De la corde postérieure",
                "De la corde médiale",
                "De la corde latérale",
                "Du tronc moyen",
            ],
            0,
            "UE2.2: radial = corde postérieure.",
        ),
        _q(
            "Au niveau des racines, le plexus brachial passe entre :",
            [
                "Scalène antérieur (avant) et scalène moyen (arrière)",
                "Petit pectoral (avant) et grand dorsal (arrière)",
                "Grand pectoral (avant) et biceps (arrière)",
                "Trapèze (avant) et deltoïde (arrière)",
            ],
            0,
            "Défilé des scalènes.",
        ),
        _q(
            "Dans le défilé costo-claviculaire, d’avant en arrière on retrouve :",
            [
                "Veine sous-clavière, artère sous-clavière, divisions du plexus",
                "Artère sous-clavière, veine sous-clavière, divisions du plexus",
                "Divisions du plexus, veine sous-clavière, artère sous-clavière",
                "Veine axillaire, artère axillaire, cordes",
            ],
            0,
            "UE2.2 précise l’ordre.",
        ),
        _q(
            "Le nerf supra-scapulaire (cours) passe dans l’incisure scapulaire :",
            [
                "Sous le ligament transverse de la scapula",
                "Au-dessus du ligament transverse de la scapula",
                "Sans rapport avec un ligament",
                "Dans le canal carpien",
            ],
            0,
            "UE2.2: sous le ligament transverse.",
        ),
        _q(
            "Le nerf musculo-cutané se termine en donnant :",
            [
                "Le nerf cutané antébrachial latéral",
                "Le nerf interosseux antérieur",
                "Le nerf cutané médial du bras",
                "Le nerf supra-scapulaire",
            ],
            0,
            "UE2.2: terminale cutanée antébrachiale latérale.",
        ),
        _q(
            "Le nerf axillaire chemine avec l’artère circonflexe humérale postérieure dans :",
            [
                "L’espace quadrangulaire",
                "Le canal carpien",
                "Le canal de Guyon",
                "Le sillon du nerf ulnaire",
            ],
            0,
            "UE2.2: espace quadrangulaire.",
        ),
        _q(
            "Au coude, le nerf ulnaire passe :",
            [
                "En arrière de l’épicondyle médial (gouttière rétro-épitrochléo-olécranienne)",
                "En avant de l’épicondyle latéral",
                "Dans la tabatière anatomique",
                "Dans le canal carpien",
            ],
            0,
            "Trajet ulnaire.",
        ),
        _q(
            "Le canal de Guyon contient :",
            [
                "Le nerf ulnaire et l’artère ulnaire",
                "Le nerf médian et l’artère radiale",
                "Le nerf radial et l’artère brachiale",
                "Le nerf axillaire et l’artère axillaire",
            ],
            0,
            "UE2.2: canal de Guyon.",
        ),
        _q(
            "Le nerf médian passe entre :",
            [
                "Les deux chefs du pronator teres",
                "Les deux chefs du triceps",
                "Le deltoïde et le petit rond",
                "Le supinateur et le brachio-radial",
            ],
            0,
            "UE2.2: entre les deux chefs du rond pronateur.",
        ),
        _q(
            "Le nerf interosseux antérieur (branche du médian) innerve notamment :",
            [
                "Flexor pollicis longus, 1/2 latérale du flexor digitorum profundus, carré pronateur",
                "Deltoïde et petit rond",
                "Supra-épineux et infra-épineux",
                "Tous les extenseurs de l’avant-bras",
            ],
            0,
            "UE2.2: liste d’innervation.",
        ),
        _q(
            "Dans le cours, une atteinte du médian au canal carpien peut donner :",
            [
                "Fonte du thénar avec “main de singe”",
                "Fonte des espaces interosseux avec “main en griffe”",
                "Paralysie du deltoïde",
                "Anesthésie de la face médiale du bras",
            ],
            0,
            "Description clinique UE2.2.",
        ),
        _q(
            "Le nerf radial plonge avec l’artère brachiale profonde dans :",
            [
                "L’espace huméro-tricipital",
                "L’espace quadrangulaire",
                "Le canal de Guyon",
                "Le défilé des scalènes",
            ],
            0,
            "UE2.2: radial + a. brachiale profonde.",
        ),
        _q(
            "La branche profonde du nerf radial :",
            [
                "Plonge dans le supinateur et innerve la loge postérieure",
                "Est surtout sensitive et se termine en nerfs digitaux palmaires",
                "Passe dans le canal carpien",
                "Se termine en nerf cutané antébrachial latéral",
            ],
            0,
            "UE2.2: branche profonde surtout motrice.",
        ),
    ]

    # Angiologie
    bank += [
        _q(
            "L’irrigation du membre supérieur débute à partir de :",
            [
                "L’artère sous-clavière",
                "L’artère brachiale",
                "L’artère radiale",
                "L’arcade palmaire profonde",
            ],
            0,
            "UE2.2: sous-clavière.",
        ),
        _q(
            "Dans le cours, l’artère sous-clavière passe :",
            [
                "Entre les scalènes antérieur et moyen",
                "En arrière du trapèze",
                "Dans le canal carpien",
                "Dans l’espace quadrangulaire",
            ],
            0,
            "Trajet sous-clavier.",
        ),
        _q(
            "L’artère sous-clavière devient l’artère axillaire :",
            [
                "Au niveau du défilé costo-claviculaire",
                "Au niveau du pli du coude",
                "Au niveau du canal carpien",
                "Au niveau de la tabatière anatomique",
            ],
            0,
            "UE2.2: suite sous-clavière → axillaire.",
        ),
        _q(
            "L’artère axillaire se termine en donnant l’artère brachiale :",
            [
                "Au bord inférieur du muscle grand rond",
                "Au col chirurgical de l’humérus",
                "Au défilé des scalènes",
                "Au sillon du nerf ulnaire",
            ],
            0,
            "UE2.2: bord inf. grand rond.",
        ),
        _q(
            "Après le petit pectoral, un rapport antérieur de l’artère axillaire (cours) est :",
            [
                "Le nerf médian",
                "Le nerf radial",
                "Le nerf axillaire",
                "Le nerf supra-scapulaire",
            ],
            0,
            "UE2.2: en avant = médian.",
        ),
        _q(
            "L’artère brachiale se termine au pli du coude en donnant :",
            [
                "L’artère radiale et l’artère ulnaire",
                "L’artère axillaire et l’artère sous-clavière",
                "L’arcade dorsale et l’arcade palmaire superficielle",
                "L’artère thoraco-acromiale et l’artère subscapulaire",
            ],
            0,
            "UE2.2: radiale + ulnaire.",
        ),
        _q(
            "Dans le cours, le pouls radial peut être palpé :",
            [
                "Dans la tabatière anatomique",
                "En arrière de l’épicondyle médial",
                "Dans le canal de Guyon",
                "Dans la fosse infra-épineuse",
            ],
            0,
            "UE2.2: tabatière anatomique.",
        ),
    ]

    return bank


def build_chiropractic_ifec_bank() -> List[QItem]:
    # S’inspire des objectifs/compétences IFEC (page fournie) + fondamentaux P1 (sécurité, RC, EBP, communication).
    bank: List[QItem] = []

    bank += [
        _q(
            "Selon l’IFEC (objectifs), une priorité centrale de la formation en chiropraxie est :",
            [
                "La qualité et la sécurité des soins",
                "La prescription systématique d’imagerie",
                "La chirurgie en première intention",
                "L’exclusivité du traitement médicamenteux",
            ],
            0,
            "L’IFEC met en avant protection des personnes, sécurité des soins.",
        ),
        _q(
            "Selon l’IFEC, le chiropracteur doit être capable de :",
            [
                "Reconnaître les situations nécessitant une intervention médicale",
                "Éviter tout raisonnement clinique",
                "Traiter toute pathologie sans exception",
                "Prescrire systématiquement une IRM avant toute prise en charge",
            ],
            0,
            "Obligation d’identifier ce qui dépasse ses compétences.",
        ),
        _q(
            "La prise en charge “en premier recours” signifie surtout :",
            [
                "Patient consultant directement sans prescription médicale préalable",
                "Patient consultant uniquement après chirurgie",
                "Patient adressé uniquement par un radiologue",
                "Patient pris en charge uniquement en hospitalisation",
            ],
            0,
            "Premier contact.",
        ),
        _q(
            "Dans les compétences IFEC, “raisonnement clinique” et “pensée critique” impliquent :",
            [
                "Formuler des hypothèses et les tester avec anamnèse + examen",
                "Choisir une technique au hasard",
                "Ne pas réévaluer",
                "Se baser uniquement sur l’imagerie",
            ],
            0,
            "Approche hypothético-déductive.",
        ),
        _q(
            "Une obligation avant technique manuelle est :",
            [
                "Recueillir un consentement éclairé (bénéfices/risques/alternatives)",
                "Éviter toute explication au patient",
                "Réaliser une radio systématique",
                "Ne pas documenter",
            ],
            0,
            "Sécurité/éthique.",
        ),
        _q(
            "Un “red flag” majeur évoquant une queue de cheval est :",
            [
                "Troubles sphinctériens avec anesthésie en selle",
                "Douleur mécanique améliorée par l’exercice",
                "Douleur localisée à l’effort sans irradiation",
                "Raideur matinale brève isolée",
            ],
            0,
            "Urgence neuro.",
        ),
        _q(
            "Le format SOAP correspond à :",
            [
                "Subjectif – Objectif – Analyse – Plan",
                "Screening – Observation – Analyse – Plan",
                "Symptômes – Orientation – Auscultation – Prescription",
                "Squelette – Os – Articulations – Posture",
            ],
            0,
            "Standard de note clinique.",
        ),
        _q(
            "Dans une approche “evidence-based”, la question PICO inclut typiquement :",
            [
                "Patient/Problème, Intervention, Comparateur, Outcome",
                "Placebo, Imagerie, Chirurgie, Ordonnance",
                "Prévalence, Incidence, Coût, Organisation",
                "Posture, Isométrie, Cardio, Ostéopathie",
            ],
            0,
            "Rappel méthodo.",
        ),
        _q(
            "Si une situation dépasse les compétences du chiropracteur (IFEC), la conduite attendue est :",
            [
                "Orienter vers un professionnel médical/paramédical approprié",
                "Poursuivre sans informer le patient",
                "Multiplier les manipulations",
                "Éviter toute collaboration interprofessionnelle",
            ],
            0,
            "Référence/coopération.",
        ),
    ]

    return bank


def expand_with_templates(rng: random.Random, base: List[QItem], target_count: int) -> List[QItem]:
    """Augmente la banque via permutations contrôlées et variantes de formulation.

    Objectif : obtenir ~400 items variés sans inventer de faits nouveaux.
    Stratégie :
    - Dupliquer certains items en changeant l’angle (définition ↔ exemple ↔ propriété).
    - Générer des variantes “Quel item correspond à … ?” et “Quel énoncé est correct ?”
      sur un sous-ensemble de faits stables.

    Pour rester robuste, on utilise un petit jeu de transformations textuelles.
    """

    if target_count <= len(base):
        return base[:target_count]

    bank = list(base)

    # Faits structurés (nom / description / 3 distracteurs minimum)
    # Objectif: un grand espace de combinaisons pour éviter les doublons.
    facts: List[Tuple[str, str, List[str]]] = [
        # Histologie / TC
        ("Mésoblaste (via mésenchyme)", "l’origine embryologique des tissus conjonctifs", ["Neuroectoderme", "Endoderme", "Épiderme"]),
        ("MEC = fibres + substance fondamentale", "la définition de la matrice extracellulaire", ["MEC = cellules résidentes + cellules mobiles", "MEC = plasma", "MEC = myéline"]),
        ("Substance fondamentale", "l’élément de la MEC localisé entre cellules et fibres, de consistance semi-fluide", ["Collagène IV", "Élastine", "Hémoglobine"]),
        ("GAG", "de longues chaînes glucidiques non ramifiées", ["Protéines globulaires", "Lipides", "Acides nucléiques"]),
        ("Acide uronique + hexosamine", "la composition du disaccharide de base des GAG", ["Ribose + base", "Acide aminé + phosphate", "Cholestérol + triglycéride"]),
        ("Acide hyaluronique", "un GAG non sulfaté, ubiquitaire, ne formant pas de protéoglycanes", ["Dermatane sulfate", "Chondroïtine sulfate", "Héparane sulfate"]),
        ("Hyaluronidase", "l’enzyme qui hydrolyse l’acide hyaluronique", ["Élastase", "Collagénase", "Amylase"]),
        ("Charges négatives", "la cause de l’hydrophilie des protéoglycanes", ["Charges positives", "Absence de glucides", "Présence de myosine"]),
        ("Mucopolysaccharidoses", "des maladies de surcharge lysosomiale par déficit enzymatique (accumulation de GAG)", ["Infection virale aiguë", "Fracture traumatique", "Cancer épithélial"]),
        ("Fibronectine", "une glycoprotéine d’adhérence liant cellules et collagène", ["Élastine", "Réticuline", "Albumine"]),
        ("Laminine", "une glycoprotéine spécifique de la lame basale", ["Collagène I", "Chondroïtine sulfate", "Actine"]),
        ("Intégrines (α/β)", "des récepteurs membranaires dimériques impliqués dans l’ancrage à la MEC", ["Enzymes lysosomiales", "GAG sulfatés", "Fibres élastiques"]),
        ("Collagène type I", "le collagène majoritaire (~90%), ubiquitaire", ["Type II", "Type III", "Type IV"]),
        ("Collagène type II", "le collagène du cartilage", ["Type I", "Type III", "Élastine"]),
        ("Collagène type III", "la réticuline (fibres réticulées)", ["Type I", "Type II", "Fibrilline"]),
        ("Collagène type IV", "le collagène des lames basales (mailles, ne forme pas de fibres)", ["Type I", "Type II", "Type III"]),
        ("Orcéine", "la coloration de mise en évidence des fibres élastiques", ["Gram", "PAS", "Rouge Congo"]),
        ("Fibroblaste", "la cellule résidente qui synthétise les macromolécules de la MEC", ["Hématie", "Plasmocyte", "Neurone"]),
        ("Fibrocyte", "la forme quiescente du fibroblaste", ["Mastocyte", "Granulocyte", "Chondrocyte"]),
        ("Myofibroblaste", "cellule avec actine/myosine impliquée dans réparation et inflammation", ["Ostéocyte", "Hématie", "Adipocyte brun"]),
        ("Mastocyte", "cellule proche des capillaires riche en histamine (allergie)", ["Plaquette", "Fibrocyte", "Chondroblaste"]),
        ("Plasmocyte", "lymphocyte B maturé sécrétant des Ig", ["Neutrophile", "Fibroblaste", "Adipocyte"]),
        ("TC muqueux", "tissu conjonctif surtout embryonnaire (cordon ombilical)", ["TC dense régulier", "TC réticulé", "Tissu osseux"]),
        ("TC lâche", "tissu très distribué, rôle de remplissage, fibres sans orientation", ["TC dense régulier", "Sang", "Cartilage"]),
        ("Endomysium", "localisation citée du TC lâche entre fibres musculaires striées", ["Dure-mère", "Stroma cornéen", "Ligaments jaunes"]),
        ("TC dense irrégulier", "collagène en faisceaux orientés dans toutes les directions", ["TC dense régulier unitendu", "TC muqueux", "Sang"]),
        ("Dure-mère", "exemple de localisation de TC dense irrégulier", ["Cordon ombilical", "Moelle osseuse", "Plasma"]),
        ("Tendon/Ligament", "exemples de TC dense régulier unitendu", ["Derme papillaire", "Moelle osseuse", "Lame basale"]),
        ("Stroma cornéen / aponévrose", "exemples de TC dense régulier bitendu", ["Cordon ombilical", "Sang", "Cartilage hyalin"]),
        ("Ligaments jaunes", "exemple de TC à prédominance de fibres élastiques", ["Endomysium", "Cordon ombilical", "Moelle osseuse"]),
        ("Tissu réticulé", "charpente (maillage) en collagène III des organes hématopoïétiques/lymphoïdes", ["TC muqueux", "TC dense régulier", "Cartilage"]),
        ("Hématie", "cellule sanguine anucléée", ["Leucocyte", "Plasmocyte", "Mastocyte"]),
        ("Plaquette", "fragment cellulaire impliqué dans l’hémostase", ["Collagène I", "Fibronectine", "Neurone"]),
        ("Plasma", "matrice liquide du sang (~55%)", ["Matrice minéralisée", "Matrice cartilagineuse", "Matrice fibreuse"]),

        # UE2.2 / Neuro-angiologie MS
        ("Racine antérieure", "la racine motrice du nerf spinal", ["Racine postérieure", "Ganglion spinal", "Corde postérieure"]),
        ("Racine postérieure", "la racine sensitive (avec ganglion spinal)", ["Racine antérieure", "Division antérieure", "Tronc moyen"]),
        ("Plexus brachial (C5–T1)", "le plexus innervant ceinture scapulaire + membre supérieur", ["Plexus lombaire", "Plexus sacré", "Nerfs intercostaux"]),
        ("Tronc supérieur", "formé par C5 et C6", ["C7 seul", "C8–T1", "C6–C7"]),
        ("Divisions postérieures", "innervent préférentiellement les loges postérieures (extenseurs)", ["Loges antérieures", "Thénar", "Diaphragme"]),
        ("Corde postérieure", "formée des 3 divisions postérieures", ["Division antérieure tronc inf", "Divisions antérieures sup+moy", "Racines non mélangées"]),
        ("Nerf musculo-cutané", "branche terminale issue de la corde latérale", ["Nerf ulnaire", "Nerf radial", "Nerf axillaire"]),
        ("Nerf ulnaire", "branche terminale issue de la corde médiale", ["Corde latérale", "Corde postérieure", "Tronc supérieur"]),
        ("Nerf radial", "branche terminale issue de la corde postérieure", ["Corde médiale", "Corde latérale", "Tronc inférieur"]),
        ("Défilé des scalènes", "espace entre scalène antérieur (avant) et moyen (arrière)", ["Canal carpien", "Canal de Guyon", "Espace quadrangulaire"]),
        ("Défilé costo-claviculaire", "où l’ordre antéro-postérieur est veine sous-clavière → artère → divisions", ["Défilé des scalènes", "Défilé du petit pectoral", "Espace huméro-tricipital"]),
        ("Espace quadrangulaire", "où passe le nerf axillaire avec l’a. circonflexe humérale postérieure", ["Canal carpien", "Gouttière ulnaire", "Tabatière anatomique"]),
        ("Canal de Guyon", "où passent le nerf ulnaire et l’artère ulnaire", ["Canal carpien", "Défilé costo-claviculaire", "Sillon du nerf radial"]),
        ("Canal carpien", "zone classique de compression du nerf médian", ["Espace quadrangulaire", "Défilé des scalènes", "Gouttière ulnaire"]),
        ("Espace huméro-tricipital", "où le nerf radial accompagne l’a. brachiale profonde", ["Espace quadrangulaire", "Canal de Guyon", "Tabatière anatomique"]),
        ("Sous-clavière", "l’artère à partir de laquelle commence l’irrigation du membre supérieur", ["Carotide commune", "Artère radiale", "Arcade palmaire profonde"]),
        ("Axillaire", "l’artère faisant suite à la sous-clavière au défilé costo-claviculaire", ["Radiale", "Ulnaire", "Carotide"]),
        ("Brachiale", "l’artère issue de l’axillaire au bord inférieur du grand rond", ["Sous-clavière", "Artère dorsale de la scapula", "Arcade dorsale"]),
        ("Radiale + ulnaire", "les deux terminales de l’artère brachiale au pli du coude", ["Sous-clavière + carotide", "Axillaire + subscapulaire", "Thoraco-acromiale + circonflexe"]),
        ("Tabatière anatomique", "site de palpation du pouls radial cité", ["Gouttière ulnaire", "Espace quadrangulaire", "Canal de Guyon"]),

        # IFEC / compétences
        ("Qualité et sécurité des soins", "un objectif central mis en avant par l’IFEC", ["Chirurgie systématique", "Imagerie obligatoire", "Prescription médicamenteuse exclusive"]),
        ("Reconnaître ses limites", "la capacité à identifier ce qui nécessite une intervention médicale", ["Tout traiter sans exception", "Éviter l’orientation", "Ignorer les red flags"]),
        ("Raisonnement clinique", "formuler des hypothèses et les tester avec anamnèse + examen", ["Choisir la technique avant l’examen", "Se baser uniquement sur l’imagerie", "Ne pas réévaluer"]),
        ("PICO", "Patient/Problème – Intervention – Comparateur – Outcome", ["Placebo–Imagerie–Chirurgie–Ordonnance", "Prévalence–Incidence–Coût–Organisation", "Posture–Isométrie–Cardio–Ostéopathie"]),
        ("Consentement éclairé", "information sur bénéfices/risques/alternatives avant un soin", ["Optionnel", "Réservé à la chirurgie", "Inutile si douleur chronique"]),
        ("SOAP", "Subjectif – Objectif – Analyse – Plan", ["Screening – Observation – Analyse – Plan", "Symptômes – Orientation – Auscultation – Prescription", "Squelette – Os – Articulations – Posture"]),
    ]

    def build_desc_to_name(name: str, desc: str, distractors: List[str]) -> QItem:
        stem = f"Quel élément correspond le mieux à : {desc} ?"
        opts = [name] + distractors[:]
        rng.shuffle(opts)
        ans = opts.index(name)
        return _q(stem, opts[:4], ans, "Variante générée à partir d’un fait de cours.")

    def build_name_to_desc(name: str, desc: str, distractors: List[str]) -> QItem:
        stem = f"Lequel des énoncés décrit correctement : {name} ?"
        opts = [desc] + distractors[:]
        rng.shuffle(opts)
        ans = opts.index(desc)
        return _q(stem, opts[:4], ans, "Variante générée à partir d’un fait de cours.")

    # Prépare aussi une liste de descriptions/distracteurs "réutilisables" pour augmenter la variété.
    all_names = [n for n, _, _ in facts]
    all_descs = [d for _, d, _ in facts]

    def random_other_names(exclude: str, k: int = 3) -> List[str]:
        pool = [n for n in all_names if n != exclude]
        return rng.sample(pool, k)

    def random_other_descs(exclude: str, k: int = 3) -> List[str]:
        pool = [d for d in all_descs if d != exclude]
        return rng.sample(pool, k)

    # Génère à la volée des variantes aléatoires (stems rendus uniques via un tag),
    # pour éviter de cycler un set fini.
    counter = 0
    while len(bank) < target_count:
        counter += 1
        name, desc, distractors = rng.choice(facts)
        variant_type = rng.choice(["desc_to_name", "name_to_desc", "desc_to_name_alt"])

        if variant_type == "desc_to_name":
            item = build_desc_to_name(name, desc, distractors)
            item = QItem(
                stem=f"[V{counter}] {item.stem}",
                options=item.options,
                answer_index=item.answer_index,
                explanation=item.explanation,
            )
        elif variant_type == "name_to_desc":
            item = build_name_to_desc(name, desc, random_other_descs(desc))
            item = QItem(
                stem=f"[V{counter}] {item.stem}",
                options=item.options,
                answer_index=item.answer_index,
                explanation=item.explanation,
            )
        else:
            stem = f"[V{counter}] Parmi les propositions suivantes, laquelle correspond le mieux à : {desc} ?"
            opts = [name] + random_other_names(name)
            rng.shuffle(opts)
            item = _q(stem, opts, opts.index(name), "Variante générée à partir d’un fait de cours.")

        # Petite diversification supplémentaire : mélange des options
        bank.append(_shuffle_options(rng, item))

    return bank


def dedupe(bank: List[QItem]) -> List[QItem]:
    # Déduplication volontairement “légère” : on supprime seulement les stems strictement identiques.
    # (Sinon, avec une génération à base de gabarits, on risque d’écraser trop d’items.)
    seen = set()
    out: List[QItem] = []
    for it in bank:
        key = it.stem
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def write_markdown(questions: List[QItem], md_path: Path) -> None:
    lines: List[str] = []
    lines.append("# QCM complet – Chiropraxie P1 (≈400 questions)")
    lines.append("")
    lines.append("**Consigne** : 1 seule bonne réponse par question (A–D).")
    lines.append("")

    for i, q in enumerate(questions, start=1):
        lines.append(f"{i}) {q.stem}")
        for j, opt in enumerate(q.options):
            lines.append(f"- {LETTERS[j]}. {opt}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_answer_key(questions: List[QItem], md_path: Path) -> None:
    lines: List[str] = []
    lines.append("# Corrigé – QCM complet (réponses)")
    lines.append("")
    lines.append("Format : numéro → lettre (et rappel de l’option correcte).")
    lines.append("")

    for i, q in enumerate(questions, start=1):
        letter = LETTERS[q.answer_index]
        correct = q.options[q.answer_index]
        lines.append(f"{i}) {letter} — {correct}")
        if q.explanation:
            lines.append(f"   Explication : {q.explanation}")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_quizlet_tsv(questions: List[QItem], tsv_path: Path) -> None:
    # Import Quizlet: "Terme<TAB>Définition" par ligne.
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        for i, q in enumerate(questions, start=1):
            term = f"Q{i}: {q.stem}"
            definition = f"Réponse: {LETTERS[q.answer_index]} — {q.options[q.answer_index]}"
            writer.writerow([term, definition])


def main() -> None:
    rng = random.Random(42)

    ct = build_connective_tissue_bank()
    ue = build_ue22_upper_limb_bank()
    chiro = build_chiropractic_ifec_bank()

    base = ct + ue + chiro

    # Mélange + shuffle options
    shuffled = [_shuffle_options(rng, q) for q in base]
    rng.shuffle(shuffled)

    # Expansion contrôlée jusqu'à 400 (stems rendus uniques dans le générateur)
    expanded = expand_with_templates(rng, shuffled, target_count=400)[:400]

    out_md = Path("QCM_Chiropraxie_P1_Complet_400.md")
    out_key = Path("QCM_Chiropraxie_P1_Complet_400_CORRIGE.md")
    out_tsv = Path("Quizlet_QCM_400.tsv")

    write_markdown(expanded, out_md)
    write_answer_key(expanded, out_key)
    write_quizlet_tsv(expanded, out_tsv)

    print("Wrote:", out_md.resolve())
    print("Wrote:", out_key.resolve())
    print("Wrote:", out_tsv.resolve())
    print("Questions:", len(expanded))


if __name__ == "__main__":
    main()
