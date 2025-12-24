#!/usr/bin/env python3
"""
Script de génération de QCM à partir des tableaux de myologie
Extrait automatiquement les tableaux (Origine/Terminaison/Action/Innervation)
du PDF UE2.2 et génère des questions QCM structurées.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any


# Structure des tableaux de muscles détectés dans le PDF
MUSCLE_TABLES = {
    # Groupe superficiel du dos
    "Trapèze": {
        "origine": "External Occipital Protuberance (EOP), Ligament nucal, SP C7->T12 + lig. interépineux correspondants",
        "terminaison": "Faisceau sup: 1/3 externe de la face supérieure de la clavicule; Faisceau moy: bord médial de l'acromion; Faisceau inf: bord sup. et post. de l'épine de la scapula",
        "trajet": "Faisceau sup: vers le bas, en dehors et en avant; Faisceau moy: horizontalement en dehors; Faisceau inf: en haut et en dehors",
        "action": "Faisceau sup: élévation de la scapula; Faisceau moy: rétraction de la scapula; Faisceau inf: abaissement de la scapula",
        "innervation": "N. accessoire (CN XI)",
        "tags": ["Myologie_MS"]
    },
    "Grand dorsal": {
        "origine": "Par le fascia thoraco-lombaire: SP de T7-L5 + lig. inter-épineux, Crête sacrale médiane, 1/5 post. de la crête iliaque, K9-K12 + angle inf. de la scapula (inconstant)",
        "terminaison": "Latéralement sur la crête du tubercule mineur",
        "trajet": "Oblique en dehors et haut, contourne les flancs du tronc",
        "action": "Adduction du bras, Rotation interne de la gléno-humérale, Extension du bras",
        "innervation": "N. thoraco-dorsal (C6,C7,C8)",
        "tags": ["Myologie_MS"]
    },
    # Groupe profond du dos
    "Élévateur de la scapula": {
        "origine": "Face postérieure des TP de C1-C4",
        "terminaison": "Partie sup. du bord médial de la scapula, Angle sup. de la scapula",
        "trajet": "En bas et en dehors",
        "action": "Élévateur de la scapula, Abaissement de la cavité glénoïdale par sonnette interne, Inflexion homolatérale du rachis cervical",
        "innervation": "Dorsal scapular nerve (C3,C4,C5)",
        "tags": ["Myologie_MS"]
    },
    "Petit rhomboïde": {
        "origine": "Lig. nucal, SP de C7 et T1",
        "terminaison": "Bord médial de la scapula au niveau de l'épine",
        "trajet": "Oblique en bas et en dehors",
        "action": "Élévation de la scapula, Rétraction de la scapula, Fixe la scapula contre le thorax",
        "innervation": "Dorsal scapular nerve (C4,C5)",
        "tags": ["Myologie_MS"]
    },
    "Grand rhomboïde": {
        "origine": "SP T2-T5 + lig. inter-épineux",
        "terminaison": "Bord médial de la scapula en dessous de l'épine",
        "trajet": "Oblique en bas et en dehors",
        "action": "Élévation de la scapula, Rétraction de la scapula, Fixe la scapula contre le thorax, Rotation médiale de la scapula",
        "innervation": "Dorsal scapular nerve (C4,C5)",
        "tags": ["Myologie_MS"]
    },
    # Muscles du thorax et MS
    "Grand pectoral": {
        "origine": "Faisceau claviculaire: partie méd. de la face supérieure et du bord ant. de la clavicule; Faisceau sterno-costal: face ant. du manubrium sternal, du corps du sternum et cartilages costaux; Faisceau abdominal: gaine du m. droit de l'abdomen",
        "terminaison": "Latéralement sur la crête du tubercule majeur",
        "trajet": "Les 3 faisceaux se dirigent latéralement",
        "action": "Adduction du bras, Rotation médiale de la gléno-humérale",
        "innervation": "N. pectoral médial et latéral (C8,T1)",
        "tags": ["Myologie_MS"]
    },
    "Petit pectoral": {
        "origine": "Latéralement aux 3e, 4e, 5e articulations costo-chondrales",
        "terminaison": "Face médiale de l'apophyse coracoïde",
        "trajet": "Vers le haut et en dehors",
        "action": "Protraction de la scapula, Abaisseur de la scapula, Inspirateur accessoire",
        "innervation": "N. pectoral médial (C8,T1)",
        "tags": ["Myologie_MS"]
    },
    "Subclavier": {
        "origine": "1ère articulation costo-chondrale",
        "terminaison": "Sillon du m. sous-clavier (face inférieure de la clavicule)",
        "trajet": "En dehors sous la clavicule",
        "action": "Fixe et abaisse la clavicule, Inspirateur accessoire",
        "innervation": "N. subclavier (C5,C6)",
        "tags": ["Myologie_MS"]
    },
    "Dentelé antérieur": {
        "origine": "Antérieurement, sur les faces externes de K1-K9",
        "terminaison": "Bord médial de la scapula",
        "trajet": "Vers l'arrière en contournant le grill costal entre ce dernier et la scapula",
        "action": "Fixe la scapula contre le thorax, Protraction de la scapula, Participe à la sonnette latérale",
        "innervation": "N. long thoracique (C5,C6,C7)",
        "tags": ["Myologie_MS"]
    },
    # Muscles de l'épaule
    "Deltoïde": {
        "origine": "Faisceau ant. (claviculaire): 1/3 lat. du bord ant. de la clavicule; Faisceau moy. (acromial): bord lat. de l'acromion; Faisceau post. (épineux): bord post. de l'épine de la scapula",
        "terminaison": "Tubérosité deltoïdienne au niveau de l'humérus",
        "trajet": "Faisceau ant: vers le bas, en dehors et en arrière; Faisceau moy: vers le bas; Faisceau post: vers le bas, en dehors et en avant",
        "action": "Faisceau ant: flexion + rotation médiale; Faisceau moy: ABDuction; Faisceau post: extension + rotation latérale",
        "innervation": "N. Axillaire (C5,C6)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    "Grand rond": {
        "origine": "Moitié inf. du bord lat. de la scapula",
        "terminaison": "Médialement sur la crête du tubercule mineur",
        "trajet": "Oblique en haut en dehors et en avant",
        "action": "ADDuction du bras, Rotation interne de la gléno-humérale, Extension du bras",
        "innervation": "N. subscapulaire / lower subscapular n. (C5,C6,C7)",
        "tags": ["Myologie_MS"]
    },
    # Coiffe des rotateurs
    "Supra-épineux": {
        "origine": "Fosse supra-épineuse",
        "terminaison": "Trochiter partie sup.",
        "trajet": "Latéralement, au-dessus de l'épine, sous l'acromion, au-dessus de la gléno-humérale",
        "action": "ABDuction du bras, Rotation latérale accessoire de la gléno-humérale",
        "innervation": "N. supra-scapulaire (C5,C6)",
        "tags": ["Myologie_MS"]
    },
    "Infra-épineux": {
        "origine": "Fosse infra-épineuse",
        "terminaison": "Trochiter partie post. sous le supra-épineux",
        "trajet": "En dehors et en haut",
        "action": "Rotation latérale de la gléno-humérale, ABDuction accessoire de la gléno-humérale",
        "innervation": "N. supra-scapulaire (C5,C6)",
        "tags": ["Myologie_MS"]
    },
    "Petit rond": {
        "origine": "½ sup du bord latéral de la scapula",
        "terminaison": "Trochiter partie post. sous l'infra-épineux",
        "trajet": "En dehors et en haut",
        "action": "Rotation latérale de la gléno-humérale, ADDuction accessoire de la gléno-humérale",
        "innervation": "N. axillaire (C5,C6)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    "Subscapulaire": {
        "origine": "Fosse subscapulaire, face costale de la scapula",
        "terminaison": "Trochin",
        "trajet": "En haut et en dehors, entre la scapula et le grill costal",
        "action": "Rotation médiale de la gléno-humérale, ADDuction accessoire de la gléno-humérale",
        "innervation": "N. subscapulaire / upper & lower subscapular n. (C5,C6)",
        "tags": ["Myologie_MS"]
    },
    # Muscles du bras - loge antérieure
    "Biceps brachial": {
        "origine": "Long chef: tubercule supra-glénoïdale; Court chef: apex du processus coracoïde",
        "terminaison": "Tubérosité du radius, Aponévrose bicipitale se perdant dans le fascia de l'avant-bras",
        "trajet": "Le tendon du long chef passe au-dessus de la tête humérale puis descend dans la gouttière bicipitale; Court chef: en dehors et en bas",
        "action": "Flexion du coude, Supination du coude, Stabilisation de la gléno-humérale, Flexion accessoire de l'épaule",
        "innervation": "N. musculo-cutané (C5,C6)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    "Coraco-brachial": {
        "origine": "Apex du processus coracoïde",
        "terminaison": "Partie moyenne de la face médiale de l'humérus",
        "trajet": "En bas et légèrement en dehors",
        "action": "Flexion de la gléno-humérale, Adduction accessoire de la gléno-humérale",
        "innervation": "N. musculo-cutané (C5,C6,C7)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    "Brachialis": {
        "origine": "Partie inf. des faces médiale et latérale de l'humérus",
        "terminaison": "Tubérosité ulnaire",
        "trajet": "En bas",
        "action": "Flexion du coude",
        "innervation": "N. musculo-cutané (C5,C6)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    # Muscles du bras - loge postérieure
    "Triceps brachial": {
        "origine": "Long chef: tubercule infra-glénoïdale; Chef médial: face post. de la diaphyse humérale (en dessous du sillon du n. radial); Chef latéral: face post. de la diaphyse humérale (au-dessus du sillon du n. radial)",
        "terminaison": "Tendon commun sur la face sup. de l'olécrane",
        "trajet": "En bas",
        "action": "Extension du coude, Long chef: extension du bras",
        "innervation": "N. radial (C6,C7,C8), N. axillaire (long chef)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    "Anconé": {
        "origine": "Face post. de l'épicondyle lat. de l'humérus",
        "terminaison": "Face post.-lat. de l'olécrane, Face post.-sup. de la diaphyse de l'ulna",
        "trajet": "En bas et en dedans",
        "action": "Extension du coude",
        "innervation": "N. radial (C6,C7,C8)",
        "tags": ["Myologie_MS", "Neurologie_MS"]
    },
    # Muscles de la cuisse - Fessiers
    "Grand fessier": {
        "origine": "Face postérieure de l'ilium (ligne glutéale postérieure), Sacrum, Ligament sacro-tubéreux",
        "terminaison": "Tubérosité glutéale du fémur, Tractus ilio-tibial",
        "trajet": "En bas et en dehors",
        "action": "Extension de la hanche, Rotation latérale de la hanche, Stabilisation du bassin",
        "innervation": "N. glutéal inférieur (L5,S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Moyen fessier": {
        "origine": "Face latérale de l'ilium entre les lignes glutéales antérieure et postérieure",
        "terminaison": "Face latérale du grand trochanter",
        "trajet": "En bas et en dehors",
        "action": "Abduction de la hanche, Rotation médiale (fibres antérieures), Rotation latérale (fibres postérieures)",
        "innervation": "N. glutéal supérieur (L4,L5,S1)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Petit fessier": {
        "origine": "Face latérale de l'ilium entre les lignes glutéales antérieure et inférieure",
        "terminaison": "Face antérieure du grand trochanter",
        "trajet": "En bas et en dehors",
        "action": "Abduction de la hanche, Rotation médiale de la hanche",
        "innervation": "N. glutéal supérieur (L4,L5,S1)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Piriforme": {
        "origine": "Face antérieure du sacrum (S2-S4)",
        "terminaison": "Bord supérieur du grand trochanter",
        "trajet": "Latéralement à travers la grande incisure ischiatique",
        "action": "Rotation latérale de la hanche, Abduction de la hanche (hanche fléchie)",
        "innervation": "N. du piriforme (S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    # Muscles de la cuisse - loge antérieure
    "Quadriceps fémoral": {
        "origine": "Droit fémoral: épine iliaque antéro-inférieure; Vaste latéral: ligne âpre (lèvre latérale), grand trochanter; Vaste médial: ligne âpre (lèvre médiale); Vaste intermédiaire: face antérieure du fémur",
        "terminaison": "Base et bords de la patella, puis tubérosité tibiale via le ligament patellaire",
        "trajet": "En bas",
        "action": "Extension du genou, Droit fémoral: flexion de la hanche",
        "innervation": "N. fémoral (L2,L3,L4)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Sartorius": {
        "origine": "Épine iliaque antéro-supérieure (EIAS)",
        "terminaison": "Face médiale du tibia (patte d'oie)",
        "trajet": "Oblique en bas et en dedans, croise la cuisse en diagonal",
        "action": "Flexion de la hanche, Abduction et rotation latérale de la hanche, Flexion du genou, Rotation médiale du genou",
        "innervation": "N. fémoral (L2,L3)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    # Muscles de la cuisse - loge médiale
    "Gracile": {
        "origine": "Branche inférieure du pubis",
        "terminaison": "Face médiale du tibia (patte d'oie)",
        "trajet": "En bas",
        "action": "Adduction de la hanche, Flexion du genou, Rotation médiale du genou",
        "innervation": "N. obturateur (L2,L3)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Pectiné": {
        "origine": "Pecten du pubis",
        "terminaison": "Ligne pectinée du fémur",
        "trajet": "En bas et en dehors",
        "action": "Adduction de la hanche, Flexion de la hanche",
        "innervation": "N. fémoral et N. obturateur (L2,L3)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Grand adducteur": {
        "origine": "Branche ischio-pubienne, Tubérosité ischiatique",
        "terminaison": "Ligne âpre, Tubercule adducteur (condyle fémoral médial)",
        "trajet": "En bas et en dehors",
        "action": "Adduction de la hanche, Extension de la hanche (partie postérieure)",
        "innervation": "N. obturateur (L2,L3,L4), N. sciatique (partie postérieure)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    # Muscles de la cuisse - loge postérieure (ischio-jambiers)
    "Biceps fémoral": {
        "origine": "Long chef: tubérosité ischiatique; Court chef: ligne âpre (lèvre latérale)",
        "terminaison": "Tête de la fibula",
        "trajet": "En bas et en dehors",
        "action": "Flexion du genou, Rotation latérale du genou, Long chef: extension de la hanche",
        "innervation": "Long chef: N. tibial (L5,S1,S2); Court chef: N. fibulaire commun (L5,S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Semi-tendineux": {
        "origine": "Tubérosité ischiatique",
        "terminaison": "Face médiale du tibia (patte d'oie)",
        "trajet": "En bas",
        "action": "Flexion du genou, Rotation médiale du genou, Extension de la hanche",
        "innervation": "N. tibial (L5,S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Semi-membraneux": {
        "origine": "Tubérosité ischiatique",
        "terminaison": "Condyle tibial médial",
        "trajet": "En bas",
        "action": "Flexion du genou, Rotation médiale du genou, Extension de la hanche",
        "innervation": "N. tibial (L5,S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    # Muscles de la jambe
    "Gastrocnémien": {
        "origine": "Chef médial: condyle fémoral médial; Chef latéral: condyle fémoral latéral",
        "terminaison": "Calcanéus via le tendon calcanéen (Achille)",
        "trajet": "En bas",
        "action": "Flexion plantaire de la cheville, Flexion du genou",
        "innervation": "N. tibial (S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Soléaire": {
        "origine": "Tête et partie proximale de la fibula, Ligne du soléaire sur le tibia",
        "terminaison": "Calcanéus via le tendon calcanéen (Achille)",
        "trajet": "En bas",
        "action": "Flexion plantaire de la cheville",
        "innervation": "N. tibial (S1,S2)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
    "Tibial antérieur": {
        "origine": "Face latérale du tibia, Membrane interosseuse",
        "terminaison": "Cunéiforme médial, Base du 1er métatarsien",
        "trajet": "En bas et en dedans",
        "action": "Dorsiflexion de la cheville, Inversion du pied",
        "innervation": "N. fibulaire profond (L4,L5)",
        "tags": ["Myologie_MI", "Neurologie_MI"]
    },
}


def generate_questions_from_muscles() -> List[Dict[str, Any]]:
    """Génère des questions QCM à partir des données des muscles."""
    questions = []
    
    for muscle_name, data in MUSCLE_TABLES.items():
        tags = data.get("tags", ["Myologie_MS"])
        
        # Question sur l'origine
        if data.get("origine"):
            questions.append({
                "prompt": f"Quelle est l'origine du muscle {muscle_name} ?",
                "choices": generate_origin_choices(muscle_name, data["origine"]),
                "answer": "A",
                "tags": tags,
                "source": "PDF UE2.2 2023-2024 - Tableaux Myologie"
            })
        
        # Question sur la terminaison
        if data.get("terminaison"):
            questions.append({
                "prompt": f"Quelle est la terminaison du muscle {muscle_name} ?",
                "choices": generate_termination_choices(muscle_name, data["terminaison"]),
                "answer": "A",
                "tags": tags,
                "source": "PDF UE2.2 2023-2024 - Tableaux Myologie"
            })
        
        # Question sur l'action
        if data.get("action"):
            questions.append({
                "prompt": f"Quelle est l'action principale du muscle {muscle_name} ?",
                "choices": generate_action_choices(muscle_name, data["action"]),
                "answer": "A",
                "tags": tags,
                "source": "PDF UE2.2 2023-2024 - Tableaux Myologie"
            })
        
        # Question sur l'innervation
        if data.get("innervation"):
            questions.append({
                "prompt": f"Quel nerf innerve le muscle {muscle_name} ?",
                "choices": generate_innervation_choices(muscle_name, data["innervation"]),
                "answer": "A",
                "tags": tags + ["Neurologie_MS" if "Myologie_MS" in tags else "Neurologie_MI"],
                "source": "PDF UE2.2 2023-2024 - Tableaux Myologie"
            })
    
    # Ajouter des questions de synthèse
    questions.extend(generate_synthesis_questions())
    
    return questions


def generate_origin_choices(muscle: str, correct: str) -> List[Dict[str, str]]:
    """Génère les choix pour une question sur l'origine."""
    # Simplifier la bonne réponse
    correct_short = correct.split(";")[0].split(",")[0].strip()[:100]
    
    # Mauvaises réponses plausibles
    wrong_origins = [
        "Processus épineux de C1-C7",
        "Face latérale de l'humérus",
        "Bord médial de la scapula",
        "Tubérosité du radius",
        "Épicondyle latéral de l'humérus",
        "Face antérieure du fémur",
        "Crête iliaque antérieure",
        "Tubercule supraglénoïdal",
        "Face postérieure du tibia",
        "Grande incisure ischiatique"
    ]
    
    choices = [
        {"key": "A", "text": correct_short},
    ]
    
    # Ajouter 3 mauvaises réponses
    import random
    random.seed(hash(muscle))
    wrong = random.sample(wrong_origins, 3)
    for i, w in enumerate(wrong):
        choices.append({"key": chr(66+i), "text": w})
    
    return choices


def generate_termination_choices(muscle: str, correct: str) -> List[Dict[str, str]]:
    """Génère les choix pour une question sur la terminaison."""
    correct_short = correct.split(";")[0].split(",")[0].strip()[:100]
    
    wrong_terminations = [
        "Tubérosité du radius",
        "Olécrane",
        "Épicondyle médial",
        "Processus coracoïde",
        "Trochiter",
        "Grand trochanter",
        "Tubérosité tibiale",
        "Tête de la fibula",
        "Calcanéus",
        "Bord médial de la scapula"
    ]
    
    import random
    random.seed(hash(muscle) + 1)
    
    choices = [{"key": "A", "text": correct_short}]
    wrong = random.sample(wrong_terminations, 3)
    for i, w in enumerate(wrong):
        choices.append({"key": chr(66+i), "text": w})
    
    return choices


def generate_action_choices(muscle: str, correct: str) -> List[Dict[str, str]]:
    """Génère les choix pour une question sur l'action."""
    correct_short = correct.split(";")[0].split(",")[0].strip()[:100]
    
    wrong_actions = [
        "Flexion du coude",
        "Extension du coude",
        "Abduction de l'épaule",
        "Rotation médiale de la hanche",
        "Extension du genou",
        "Flexion plantaire",
        "Pronation de l'avant-bras",
        "Supination de l'avant-bras",
        "Adduction du bras",
        "Rotation latérale de l'épaule"
    ]
    
    import random
    random.seed(hash(muscle) + 2)
    
    choices = [{"key": "A", "text": correct_short}]
    wrong = random.sample(wrong_actions, 3)
    for i, w in enumerate(wrong):
        choices.append({"key": chr(66+i), "text": w})
    
    return choices


def generate_innervation_choices(muscle: str, correct: str) -> List[Dict[str, str]]:
    """Génère les choix pour une question sur l'innervation."""
    correct_short = correct.split(",")[0].split("(")[0].strip()
    
    wrong_nerves = [
        "N. radial",
        "N. médian",
        "N. ulnaire",
        "N. musculo-cutané",
        "N. axillaire",
        "N. fémoral",
        "N. sciatique",
        "N. tibial",
        "N. fibulaire commun",
        "N. obturateur",
        "N. thoraco-dorsal",
        "N. supra-scapulaire"
    ]
    
    # Retirer le nerf correct de la liste des mauvaises réponses
    wrong_nerves = [n for n in wrong_nerves if n.lower() not in correct.lower()]
    
    import random
    random.seed(hash(muscle) + 3)
    
    choices = [{"key": "A", "text": correct_short}]
    wrong = random.sample(wrong_nerves, min(3, len(wrong_nerves)))
    for i, w in enumerate(wrong):
        choices.append({"key": chr(66+i), "text": w})
    
    return choices


def generate_synthesis_questions() -> List[Dict[str, Any]]:
    """Génère des questions de synthèse sur les muscles."""
    return [
        {
            "prompt": "Quels muscles composent la coiffe des rotateurs ?",
            "choices": [
                {"key": "A", "text": "Supra-épineux, Infra-épineux, Petit rond, Subscapulaire"},
                {"key": "B", "text": "Deltoïde, Trapèze, Grand dorsal, Grand pectoral"},
                {"key": "C", "text": "Biceps, Triceps, Brachialis, Anconé"},
                {"key": "D", "text": "Grand rond, Petit rond, Subscapulaire, Deltoïde"}
            ],
            "answer": "A",
            "tags": ["Myologie_MS"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quels muscles forment la patte d'oie au niveau du genou ?",
            "choices": [
                {"key": "A", "text": "Sartorius, Gracile, Semi-tendineux"},
                {"key": "B", "text": "Quadriceps, Biceps fémoral, Gastrocnémien"},
                {"key": "C", "text": "Pectiné, Grand adducteur, Gracile"},
                {"key": "D", "text": "Semi-membraneux, Semi-tendineux, Biceps fémoral"}
            ],
            "answer": "A",
            "tags": ["Myologie_MI"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quels muscles composent le triceps sural ?",
            "choices": [
                {"key": "A", "text": "Gastrocnémien (2 chefs) et Soléaire"},
                {"key": "B", "text": "Tibial antérieur et Tibial postérieur"},
                {"key": "C", "text": "Long et court fibulaires"},
                {"key": "D", "text": "Extenseurs des orteils"}
            ],
            "answer": "A",
            "tags": ["Myologie_MI"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quels muscles constituent les ischio-jambiers ?",
            "choices": [
                {"key": "A", "text": "Biceps fémoral, Semi-tendineux, Semi-membraneux"},
                {"key": "B", "text": "Quadriceps fémoral (4 chefs)"},
                {"key": "C", "text": "Grand, Moyen et Petit fessiers"},
                {"key": "D", "text": "Sartorius, Gracile, Pectiné"}
            ],
            "answer": "A",
            "tags": ["Myologie_MI"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quel nerf innerve tous les muscles de la coiffe des rotateurs sauf le petit rond ?",
            "choices": [
                {"key": "A", "text": "N. supra-scapulaire et N. subscapulaire"},
                {"key": "B", "text": "N. axillaire uniquement"},
                {"key": "C", "text": "N. radial"},
                {"key": "D", "text": "N. musculo-cutané"}
            ],
            "answer": "A",
            "tags": ["Myologie_MS", "Neurologie_MS"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quel nerf innerve les muscles de la loge antérieure du bras ?",
            "choices": [
                {"key": "A", "text": "N. musculo-cutané"},
                {"key": "B", "text": "N. radial"},
                {"key": "C", "text": "N. médian"},
                {"key": "D", "text": "N. ulnaire"}
            ],
            "answer": "A",
            "tags": ["Myologie_MS", "Neurologie_MS"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
        {
            "prompt": "Quel nerf innerve les muscles de la loge postérieure du bras ?",
            "choices": [
                {"key": "A", "text": "N. radial"},
                {"key": "B", "text": "N. musculo-cutané"},
                {"key": "C", "text": "N. médian"},
                {"key": "D", "text": "N. ulnaire"}
            ],
            "answer": "A",
            "tags": ["Myologie_MS", "Neurologie_MS"],
            "source": "PDF UE2.2 2023-2024 - Synthèse"
        },
    ]


def write_questions_to_deck(questions: List[Dict[str, Any]], output_path: Path):
    """Écrit les questions générées dans un fichier Deck markdown."""
    lines = [
        "# Deck: Questions générées depuis tableaux myologie",
        "",
        f"**Générées automatiquement** : {len(questions)} questions",
        "**Source** : PDF UE2.2 2023-2024 - Tableaux Myologie",
        "",
        "---",
        ""
    ]
    
    for i, q in enumerate(questions, 1):
        tags_str = f" [Tags: {', '.join(q.get('tags', []))}]"
        lines.append(f"{i}) {q['prompt']}{tags_str}")
        for choice in q.get("choices", []):
            lines.append(f"- {choice['key']}. {choice['text']}")
        lines.append(f"**Réponse** : {q.get('answer', 'A')}")
        lines.append("")
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Écrit {len(questions)} questions dans {output_path.name}")


def main():
    print("=" * 60)
    print("🏋️ Génération de QCM depuis tableaux de myologie")
    print("=" * 60)
    
    # Générer les questions
    questions = generate_questions_from_muscles()
    print(f"\n📊 {len(questions)} questions générées")
    
    # Compter par tag
    tag_counts = {}
    for q in questions:
        for tag in q.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\n📈 Distribution par thème:")
    for tag, count in sorted(tag_counts.items()):
        print(f"  - {tag}: {count}")
    
    # Écrire dans un fichier Deck
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / "web" / "decks" / "Deck_Generated_Myologie.md"
    write_questions_to_deck(questions, output_path)
    
    # Écrire aussi en JSON pour intégration directe
    json_output = repo_root / "sources" / "generated_myologie.json"
    json_output.parent.mkdir(exist_ok=True)
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=2)
    print(f"✅ Écrit JSON dans {json_output.name}")
    
    print("\n✅ Génération terminée!")
    print("💡 Exécutez 'python3 bank/build_bank.py' pour intégrer ces questions")


if __name__ == "__main__":
    main()
