#!/usr/bin/env python3
"""
Script de réorganisation de la banque QCM Chiropraxie
- Reclassifie les questions existantes selon les nouveaux thèmes
- Supprime les doublons
- Ajoute les nouvelles questions extraites des PDFs
- Génère les nouveaux fichiers Deck_*.md avec multi-tags
"""

import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

# Configuration des nouveaux thèmes
NEW_THEMES = {
    "Angiologie_MS": "Angiologie - Membre Supérieur",
    "Angiologie_MI": "Angiologie - Membre Inférieur",
    "Histologie_Tissu_Conjonctif": "Histologie - Tissu Conjonctif",
    "Histologie_Cartilage": "Histologie - Tissu Cartilagineux",
    "Histologie_Tissu_Nerveux": "Histologie - Tissu Nerveux",
    "Histologie_Tissu_Musculaire": "Histologie - Tissu Musculaire",
    "Histologie_Epithelium": "Histologie - Épithélium",
    "Histologie_Jonctions": "Histologie - Jonctions Cellulaires",
    "Myologie_MS": "Myologie - Membre Supérieur",
    "Myologie_MI": "Myologie - Membre Inférieur",
    "Neurologie_MS": "Neurologie - Membre Supérieur",
    "Neurologie_MI": "Neurologie - Membre Inférieur",
    "Osteologie_MI": "Ostéologie - Membre Inférieur",
    "Biologie_Cellulaire": "Biologie Cellulaire",
    "Embryologie": "Embryologie",
    "Securite_IFEC": "Sécurité IFEC",
}

# Mots-clés pour classification automatique (tag principal)
CLASSIFICATION_KEYWORDS = {
    "Angiologie_MS": [
        "artère brachiale", "artère radiale", "artère ulnaire", "artère axillaire",
        "artère sous-clavière", "arcade palmaire", "veine céphalique", "veine basilique",
        "artère humérale", "tabatière anatomique", "pouls radial", "irrigation du membre supérieur",
        "défilé costo-claviculaire", "artère thoraco-acromiale", "terminales de l'artère brachiale",
        "radiale + ulnaire", "sous-clavière", "axillaire", "brachiale profonde"
    ],
    "Angiologie_MI": [
        "artère fémorale", "artère poplitée", "artère tibiale", "artère fibulaire",
        "artère iliaque", "veine fémorale", "veine saphène", "membre inférieur",
        "cuisse", "jambe", "pied", "fémorale profonde"
    ],
    "Histologie_Tissu_Conjonctif": [
        "collagène", "fibroblaste", "fibrocyte", "protéoglycane", "glycosaminoglycane",
        "gag", "acide hyaluronique", "hyaluronidase", "laminine", "fibronectine",
        "mastocyte", "histiocyte", "macrophage", "adipocyte", "plasmocyte",
        "tissu conjonctif", "matrice extracellulaire", "mec", "substance fondamentale",
        "réticuline", "élastine", "fibrilline", "myofibroblaste", "tc dense",
        "tc lâche", "endomysium", "dure-mère", "ligaments jaunes", "mucopolysaccharidose",
        "tc muqueux", "cordon ombilical", "stroma", "collagène type", "type i",
        "type ii", "type iii", "type iv", "orcéine", "intégrine", "hématie",
        "plasma", "plaquette", "tissu réticulé", "mésoblaste", "charges négatives"
    ],
    "Histologie_Cartilage": [
        "cartilage", "chondrocyte", "périchondre", "cartilage hyalin",
        "cartilage élastique", "cartilage fibreux", "chondroblaste"
    ],
    "Histologie_Jonctions": [
        "intégrine", "jonction serrée", "desmosome", "hémidesmosome",
        "jonction gap", "zonula", "adherens", "lame basale"
    ],
    "Neurologie_MS": [
        "plexus brachial", "nerf radial", "nerf médian", "nerf ulnaire",
        "nerf musculo-cutané", "nerf axillaire", "corde postérieure", "corde latérale",
        "corde médiale", "tronc supérieur", "tronc moyen", "tronc inférieur",
        "canal carpien", "canal de guyon", "défilé des scalènes",
        "espace quadrangulaire", "espace huméro-tricipital", "racine c5", "racine c6",
        "racine c7", "racine c8", "racine t1", "divisions postérieures",
        "c5–t1", "c5 à t1", "c5-t1", "racine antérieure", "racine postérieure",
        "ganglion spinal", "nerf supra-scapulaire", "nerf interosseux"
    ],
    "Neurologie_MI": [
        "plexus lombaire", "plexus sacré", "nerf sciatique", "nerf fémoral",
        "nerf obturateur", "nerf tibial", "nerf fibulaire", "nerf cutané"
    ],
    "Myologie_MS": [
        "coiffe des rotateurs", "supra-épineux", "infra-épineux", "subscapulaire",
        "petit rond", "deltoïde", "biceps brachial", "triceps brachial", "brachialis",
        "anconé", "coraco-brachial", "pronateur", "supinateur", "fléchisseur",
        "extenseur", "épitrochléen", "épicondylien", "grand rond"
    ],
    "Myologie_MI": [
        "grand fessier", "moyen fessier", "petit fessier", "piriforme",
        "quadriceps", "sartorius", "ilio-psoas", "adducteur", "gracile",
        "pectiné", "biceps fémoral", "semi-tendineux", "semi-membraneux",
        "ischio-jambier", "triceps sural", "gastrocnémien", "soléaire"
    ],
    "Osteologie_MI": [
        "acétabulum", "os coxal", "ilium", "ischium", "pubis", "fémur",
        "grand trochanter", "petit trochanter", "ligne âpre", "col fémoral",
        "tubérosité ischiatique", "épine iliaque", "crête iliaque", "risser",
        "sacro-tubéreux", "sacro-épineux"
    ],
    "Securite_IFEC": [
        "ifec", "soap", "pico", "consentement", "éthique", "déontologie",
        "qualité", "sécurité des soins", "reconnaître ses limites",
        "raisonnement clinique", "ebp", "evidence-based", "red flag",
        "queue de cheval", "orienter", "premier recours"
    ],
    "Biologie_Cellulaire": [
        "membrane plasmique", "mitochondrie", "réticulum endoplasmique", "reg", "rel",
        "appareil de golgi", "lysosome", "peroxysome", "noyau", "nucléole",
        "cytosquelette", "microfilament", "microtubule", "filament intermédiaire",
        "ribosome", "centriole", "centrosome", "mitose", "méiose", "apoptose",
        "atp", "phospholipide", "bicouche", "transport membranaire", "endocytose",
        "exocytose", "phagocytose", "pinocytose", "autophagie"
    ],
    "Embryologie": [
        "gastrulation", "neurulation", "blastocyste", "morula", "blastomère",
        "ectoblaste", "mésoblaste", "endoblaste", "somite", "notochorde",
        "ligne primitive", "trophoblaste", "embryoblaste", "crêtes neurales",
        "tube neural", "gouttière neurale", "dermatome", "myotome", "sclérotome",
        "somatopleure", "splanchnopleure", "cœlome", "implantation", "placenta",
        "feuillet embryonnaire", "segmentation"
    ]
}


def classify_question(prompt: str, choices: list = None) -> tuple:
    """
    Classifie une question selon son contenu.
    Retourne (tag_principal, [tags_secondaires])
    """
    text = prompt.lower()
    if choices:
        text += " " + " ".join([str(c).lower() for c in choices])
    
    scores = defaultdict(int)
    
    for theme, keywords in CLASSIFICATION_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                scores[theme] += 1
    
    if not scores:
        return "Histologie_Tissu_Conjonctif", []
    
    # Trier par score décroissant
    sorted_themes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    primary_tag = sorted_themes[0][0]
    secondary_tags = [t[0] for t in sorted_themes[1:3] if t[1] >= 1]  # Max 2 tags secondaires
    
    return primary_tag, secondary_tags


def similarity(a: str, b: str) -> float:
    """Calcule la similarité entre deux textes."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_duplicate(q1: dict, q2: dict, threshold: float = 0.85) -> bool:
    """Vérifie si deux questions sont des doublons."""
    return similarity(q1.get("prompt", ""), q2.get("prompt", "")) > threshold


def parse_deck_md(filepath: Path) -> list:
    """Parse un fichier Deck markdown et retourne les questions."""
    if not filepath.exists():
        return []
    
    content = filepath.read_text(encoding="utf-8")
    questions = []
    
    # Diviser le contenu par questions (numéro suivi de parenthèse)
    lines = content.split('\n')
    current_question = None
    current_choices = []
    
    for line in lines:
        # Détecter une nouvelle question
        q_match = re.match(r'^(\d+)\)\s*(?:\[V\d+\])?\s*(.+)$', line)
        if q_match:
            # Sauvegarder la question précédente
            if current_question and len(current_choices) >= 2:
                questions.append({
                    "num": current_question["num"],
                    "prompt": current_question["prompt"],
                    "choices": current_choices,
                    "source_file": filepath.name
                })
            # Nouvelle question
            current_question = {
                "num": int(q_match.group(1)),
                "prompt": q_match.group(2).strip()
            }
            current_choices = []
            continue
        
        # Détecter un choix
        choice_match = re.match(r'^- ([A-D])\.?\s*(.+)$', line)
        if choice_match and current_question:
            current_choices.append({
                "key": choice_match.group(1),
                "text": choice_match.group(2).strip()
            })
    
    # Sauvegarder la dernière question
    if current_question and len(current_choices) >= 2:
        questions.append({
            "num": current_question["num"],
            "prompt": current_question["prompt"],
            "choices": current_choices,
            "source_file": filepath.name
        })
    
    return questions


def generate_deck_md(questions: list, theme: str, theme_name: str) -> str:
    """Génère le contenu d'un fichier Deck markdown."""
    lines = [
        f"# Deck: {theme_name} — {len(questions)} questions",
        "",
        "**Consigne** : 1 seule bonne réponse (A–D).",
        ""
    ]
    
    for i, q in enumerate(questions, 1):
        # Ajouter les tags si présents
        tags_str = ""
        if q.get("tags"):
            tags_str = f" [Tags: {', '.join(q['tags'])}]"
        
        lines.append(f"{i}) {q['prompt']}{tags_str}")
        for choice in q.get("choices", []):
            if isinstance(choice, dict):
                lines.append(f"- {choice['key']}. {choice['text']}")
            else:
                lines.append(f"- {choice}")
        lines.append("")
    
    return "\n".join(lines)


def get_new_questions_from_pdfs():
    """Retourne les nouvelles questions extraites des PDFs."""
    return [
        # Histologie Tissu Conjonctif (depuis PDF Tissus Conjonctifs)
        {"prompt": "Quel est le feuillet embryonnaire à l'origine de tous les tissus conjonctifs ?", 
         "choices": [{"key": "A", "text": "Ectoblaste"}, {"key": "B", "text": "Mésoblaste"}, {"key": "C", "text": "Endoblaste"}, {"key": "D", "text": "Neuroblaste"}],
         "answer": "B", "tags": ["Histologie_Tissu_Conjonctif"]},
        {"prompt": "Quel type de collagène est spécifique des lames basales et ne forme pas de fibres ?",
         "choices": [{"key": "A", "text": "Type I"}, {"key": "B", "text": "Type II"}, {"key": "C", "text": "Type III"}, {"key": "D", "text": "Type IV"}],
         "answer": "D", "tags": ["Histologie_Tissu_Conjonctif", "Histologie_Jonctions"]},
        {"prompt": "Quel GAG n'est PAS sulfaté et ne forme pas de protéoglycanes ?",
         "choices": [{"key": "A", "text": "Chondroïtine sulfate"}, {"key": "B", "text": "Acide hyaluronique"}, {"key": "C", "text": "Kératane sulfate"}, {"key": "D", "text": "Héparane sulfate"}],
         "answer": "B", "tags": ["Histologie_Tissu_Conjonctif"]},
        {"prompt": "Les fibres élastiques sont composées d'une partie centrale amorphe et d'une partie périphérique fibrillaire. Quelles protéines correspondent ?",
         "choices": [{"key": "A", "text": "Collagène (centre) et réticuline (périphérie)"}, {"key": "B", "text": "Élastine (centre) et fibrilline (périphérie)"}, {"key": "C", "text": "Fibrilline (centre) et élastine (périphérie)"}, {"key": "D", "text": "Laminine (centre) et fibronectine (périphérie)"}],
         "answer": "B", "tags": ["Histologie_Tissu_Conjonctif"]},
        {"prompt": "Les adipocytes bruns sont caractérisés par :",
         "choices": [{"key": "A", "text": "Une seule grande vacuole lipidique"}, {"key": "B", "text": "Peu de mitochondries"}, {"key": "C", "text": "Multiples petites vacuoles et nombreuses mitochondries"}, {"key": "D", "text": "Absence de lame basale"}],
         "answer": "C", "tags": ["Histologie_Tissu_Conjonctif"]},
        {"prompt": "Quel filament intermédiaire caractérise les fibroblastes ?",
         "choices": [{"key": "A", "text": "Kératine"}, {"key": "B", "text": "Desmine"}, {"key": "C", "text": "Vimentine"}, {"key": "D", "text": "Neurofilament"}],
         "answer": "C", "tags": ["Histologie_Tissu_Conjonctif"]},
        {"prompt": "Les mucopolysaccharidoses sont des maladies de surcharge causées par :",
         "choices": [{"key": "A", "text": "Excès de synthèse de collagène"}, {"key": "B", "text": "Déficit enzymatique lysosomal empêchant la dégradation des GAG"}, {"key": "C", "text": "Carence en fibronectine"}, {"key": "D", "text": "Hyperactivité des fibroblastes"}],
         "answer": "B", "tags": ["Histologie_Tissu_Conjonctif"]},
        
        # Histologie Cartilage
        {"prompt": "Quel type de collagène est caractéristique du tissu cartilagineux ?",
         "choices": [{"key": "A", "text": "Type I"}, {"key": "B", "text": "Type II"}, {"key": "C", "text": "Type III"}, {"key": "D", "text": "Type IV"}],
         "answer": "B", "tags": ["Histologie_Cartilage", "Histologie_Tissu_Conjonctif"]},
        {"prompt": "Les protéoglycanes du cartilage confèrent une résistance aux :",
         "choices": [{"key": "A", "text": "Forces de traction"}, {"key": "B", "text": "Forces de compression"}, {"key": "C", "text": "Forces de cisaillement"}, {"key": "D", "text": "Forces de torsion"}],
         "answer": "B", "tags": ["Histologie_Cartilage"]},
        {"prompt": "Quels glycosaminoglycanes sont principalement présents dans le cartilage hyalin et élastique ?",
         "choices": [{"key": "A", "text": "Héparane sulfate et dermatane sulfate"}, {"key": "B", "text": "Chondroïtine sulfate et kératane sulfate"}, {"key": "C", "text": "Acide hyaluronique uniquement"}, {"key": "D", "text": "Dermatane sulfate et héparane sulfate"}],
         "answer": "B", "tags": ["Histologie_Cartilage"]},
        
        # Myologie MS
        {"prompt": "Quels muscles composent la coiffe des rotateurs ?",
         "choices": [{"key": "A", "text": "Deltoïde, trapèze, grand dorsal, grand pectoral"}, {"key": "B", "text": "Supra-épineux, infra-épineux, petit rond, subscapulaire"}, {"key": "C", "text": "Biceps, triceps, brachial, anconé"}, {"key": "D", "text": "Grand rond, petit rond, subscapulaire, deltoïde"}],
         "answer": "B", "tags": ["Myologie_MS"]},
        {"prompt": "Le muscle subscapulaire réalise principalement :",
         "choices": [{"key": "A", "text": "Rotation latérale de l'épaule"}, {"key": "B", "text": "Rotation médiale de l'épaule"}, {"key": "C", "text": "Abduction de l'épaule"}, {"key": "D", "text": "Extension de l'épaule"}],
         "answer": "B", "tags": ["Myologie_MS"]},
        {"prompt": "Le muscle biceps brachial s'insère distalement sur :",
         "choices": [{"key": "A", "text": "L'olécrane"}, {"key": "B", "text": "L'épicondyle latéral"}, {"key": "C", "text": "La tubérosité radiale"}, {"key": "D", "text": "La tubérosité ulnaire"}],
         "answer": "C", "tags": ["Myologie_MS"]},
        
        # Neurologie MS
        {"prompt": "Quel nerf innerve le muscle deltoïde ?",
         "choices": [{"key": "A", "text": "N. radial"}, {"key": "B", "text": "N. musculo-cutané"}, {"key": "C", "text": "N. axillaire"}, {"key": "D", "text": "N. médian"}],
         "answer": "C", "tags": ["Neurologie_MS", "Myologie_MS"]},
        {"prompt": "Quelle est l'innervation du muscle triceps brachial ?",
         "choices": [{"key": "A", "text": "N. musculo-cutané"}, {"key": "B", "text": "N. médian"}, {"key": "C", "text": "N. radial"}, {"key": "D", "text": "N. ulnaire"}],
         "answer": "C", "tags": ["Neurologie_MS", "Myologie_MS"]},
        {"prompt": "Le canal de Guyon livre passage au :",
         "choices": [{"key": "A", "text": "N. médian et a. radiale"}, {"key": "B", "text": "N. ulnaire et a. ulnaire"}, {"key": "C", "text": "N. radial et a. radiale"}, {"key": "D", "text": "N. médian et a. ulnaire"}],
         "answer": "B", "tags": ["Neurologie_MS", "Angiologie_MS"]},
        {"prompt": "Le muscle rond pronateur est innervé par :",
         "choices": [{"key": "A", "text": "N. radial"}, {"key": "B", "text": "N. médian"}, {"key": "C", "text": "N. ulnaire"}, {"key": "D", "text": "N. musculo-cutané"}],
         "answer": "B", "tags": ["Neurologie_MS", "Myologie_MS"]},
        
        # Myologie MI
        {"prompt": "Le muscle ilio-psoas s'insère sur :",
         "choices": [{"key": "A", "text": "Le grand trochanter"}, {"key": "B", "text": "Le petit trochanter"}, {"key": "C", "text": "La ligne âpre"}, {"key": "D", "text": "La tubérosité ischiatique"}],
         "answer": "B", "tags": ["Myologie_MI", "Osteologie_MI"]},
        {"prompt": "Le muscle grand fessier s'insère distalement sur :",
         "choices": [{"key": "A", "text": "Le petit trochanter"}, {"key": "B", "text": "La tubérosité glutéale et le tractus ilio-tibial"}, {"key": "C", "text": "L'épine iliaque antéro-supérieure"}, {"key": "D", "text": "La ligne pectinée"}],
         "answer": "B", "tags": ["Myologie_MI"]},
        {"prompt": "Les muscles ischio-jambiers s'insèrent proximalement sur :",
         "choices": [{"key": "A", "text": "L'épine iliaque antéro-inférieure"}, {"key": "B", "text": "La tubérosité ischiatique"}, {"key": "C", "text": "Le grand trochanter"}, {"key": "D", "text": "La crête iliaque"}],
         "answer": "B", "tags": ["Myologie_MI", "Osteologie_MI"]},
        
        # Neurologie MI
        {"prompt": "Le nerf sciatique est issu du plexus :",
         "choices": [{"key": "A", "text": "Lombaire"}, {"key": "B", "text": "Sacré"}, {"key": "C", "text": "Cervical"}, {"key": "D", "text": "Brachial"}],
         "answer": "B", "tags": ["Neurologie_MI"]},
        {"prompt": "Le nerf fémoral innerve principalement :",
         "choices": [{"key": "A", "text": "Les ischio-jambiers"}, {"key": "B", "text": "Les adducteurs"}, {"key": "C", "text": "Le quadriceps et le sartorius"}, {"key": "D", "text": "Les muscles fessiers"}],
         "answer": "C", "tags": ["Neurologie_MI", "Myologie_MI"]},
        
        # Ostéologie MI
        {"prompt": "L'acétabulum est formé par la fusion de :",
         "choices": [{"key": "A", "text": "Ilium et ischium uniquement"}, {"key": "B", "text": "Ilium, ischium et pubis"}, {"key": "C", "text": "Pubis et ischium uniquement"}, {"key": "D", "text": "Ilium et pubis uniquement"}],
         "answer": "B", "tags": ["Osteologie_MI"]},
        {"prompt": "L'angle d'inclinaison du col fémoral est d'environ :",
         "choices": [{"key": "A", "text": "90°"}, {"key": "B", "text": "115°"}, {"key": "C", "text": "130°"}, {"key": "D", "text": "150°"}],
         "answer": "C", "tags": ["Osteologie_MI"]},
        {"prompt": "Le ligament sacro-tubéreux s'insère entre le sacrum et :",
         "choices": [{"key": "A", "text": "L'épine ischiatique"}, {"key": "B", "text": "La tubérosité ischiatique"}, {"key": "C", "text": "Le grand trochanter"}, {"key": "D", "text": "La crête iliaque"}],
         "answer": "B", "tags": ["Osteologie_MI"]},
        {"prompt": "Le signe de Risser évalue :",
         "choices": [{"key": "A", "text": "La maturité de l'articulation du genou"}, {"key": "B", "text": "L'ossification de la crête iliaque et la croissance vertébrale"}, {"key": "C", "text": "La densité osseuse du fémur"}, {"key": "D", "text": "La solidité de l'articulation sacro-iliaque"}],
         "answer": "B", "tags": ["Osteologie_MI"]},
        
        # Angiologie MI
        {"prompt": "L'artère principale de la cuisse est :",
         "choices": [{"key": "A", "text": "L'artère iliaque externe"}, {"key": "B", "text": "L'artère fémorale"}, {"key": "C", "text": "L'artère poplitée"}, {"key": "D", "text": "L'artère tibiale antérieure"}],
         "answer": "B", "tags": ["Angiologie_MI"]},
        {"prompt": "L'artère fémorale profonde vascularise principalement :",
         "choices": [{"key": "A", "text": "La jambe et le pied"}, {"key": "B", "text": "Les muscles de la cuisse"}, {"key": "C", "text": "Les viscères pelviens"}, {"key": "D", "text": "La paroi abdominale"}],
         "answer": "B", "tags": ["Angiologie_MI"]},
    ]


def main():
    repo_root = Path(__file__).parent.parent
    decks_dir = repo_root / "web" / "decks"
    archive_dir = decks_dir / "archive"
    
    print("=" * 60)
    print("🔄 Réorganisation de la banque QCM Chiropraxie")
    print("=" * 60)
    
    # 1. Charger toutes les questions existantes depuis l'archive
    print("\n📂 Chargement des decks archivés...")
    all_questions = []
    
    for deck_file in archive_dir.glob("Deck_*.md"):
        questions = parse_deck_md(deck_file)
        print(f"  - {deck_file.name}: {len(questions)} questions")
        all_questions.extend(questions)
    
    print(f"\n📊 Total: {len(all_questions)} questions chargées")
    
    # 2. Classifier les questions avec multi-tags
    print("\n🏷️  Classification des questions avec multi-tags...")
    classified = defaultdict(list)
    
    for q in all_questions:
        choice_texts = [c.get("text", c) if isinstance(c, dict) else c for c in q.get("choices", [])]
        primary_tag, secondary_tags = classify_question(q["prompt"], choice_texts)
        
        q["primary_tag"] = primary_tag
        q["tags"] = [primary_tag] + secondary_tags
        classified[primary_tag].append(q)
    
    print("\n📊 Distribution par thème principal:")
    for theme in NEW_THEMES.keys():
        count = len(classified.get(theme, []))
        print(f"  - {theme}: {count} questions")
    
    # 3. Détecter et supprimer les doublons
    print("\n🔍 Détection des doublons...")
    duplicates_count = 0
    unique_questions = defaultdict(list)
    
    for theme, questions in classified.items():
        seen = []
        for q in questions:
            is_dup = False
            for existing in seen:
                if is_duplicate(q, existing):
                    duplicates_count += 1
                    is_dup = True
                    break
            if not is_dup:
                seen.append(q)
                unique_questions[theme].append(q)
    
    print(f"  - {duplicates_count} doublons détectés et supprimés")
    
    # 4. Ajouter nouvelles questions des PDFs
    print("\n➕ Ajout des nouvelles questions extraites des PDFs...")
    new_questions = get_new_questions_from_pdfs()
    
    added_count = 0
    for q in new_questions:
        primary_tag = q["tags"][0]
        # Vérifier que ce n'est pas un doublon
        is_dup = False
        for existing in unique_questions.get(primary_tag, []):
            if is_duplicate(q, existing):
                is_dup = True
                break
        if not is_dup:
            q["primary_tag"] = primary_tag
            unique_questions[primary_tag].append(q)
            added_count += 1
    
    print(f"  - {added_count} nouvelles questions ajoutées")
    
    # 5. Générer les nouveaux decks (y compris vides pour expansion future)
    print("\n📝 Génération des nouveaux fichiers Deck...")
    
    total_final = 0
    for theme, theme_name in NEW_THEMES.items():
        questions = unique_questions.get(theme, [])
        deck_content = generate_deck_md(questions, theme, theme_name)
        deck_path = decks_dir / f"Deck_{theme}.md"
        deck_path.write_text(deck_content, encoding="utf-8")
        
        status = "✅" if questions else "📭"
        expansion = " (à compléter)" if not questions else ""
        print(f"  {status} {deck_path.name}: {len(questions)} questions{expansion}")
        total_final += len(questions)
    
    # 6. Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA RÉORGANISATION")
    print("=" * 60)
    print(f"  - Questions initiales: {len(all_questions)}")
    print(f"  - Doublons supprimés: {duplicates_count}")
    print(f"  - Nouvelles questions ajoutées: {added_count}")
    print(f"  - Total final: {total_final}")
    print(f"  - Fichiers Deck générés: {len(NEW_THEMES)}")
    print(f"  - Thèmes vides (expansion future): {len([t for t in NEW_THEMES if not unique_questions.get(t)])}")
    print("\n✅ Réorganisation terminée!")
    print("\n💡 Prochaine étape: exécutez 'python3 bank/build_bank.py' pour régénérer bank.json")


if __name__ == "__main__":
    main()
