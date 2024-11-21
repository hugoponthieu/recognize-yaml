import re

# Classe de validation pour vérifier la structure d'un fichier YAML
class YAMLValidator:
    def __init__(self):
        # Liste (pile) pour gérer l'indentation des lignes
        self.stack = []
        # État initial, ici on est au début du fichier
        self.state = 'START'
        # Variable pour savoir si le fichier est valide
        self.is_valid = True
        # Message d'erreur qui s'affichera si le YAML est invalide
        self.error_message = ""

    # Fonction principale qui analyse chaque ligne du fichier YAML
    def process_line(self, line, line_number):
        # Calcul du niveau d'indentation de la ligne (combien d'espaces avant le contenu)
        indent_level = len(line) - len(line.lstrip())
        
        # Expression régulière pour identifier les paires clé-valeur
        key_value_pattern = re.compile(r'^(\s*\w+):\s*(.*)$') 
        # Expression régulière pour identifier les éléments de séquence (listes)
        sequence_item_pattern = re.compile(r'^\s*-\s+(.*)$')   

        try:
            # Si la ligne correspond à un élément de séquence, on la gère
            if sequence_item_pattern.match(line):
                self.handle_sequence(indent_level, line, line_number)
            # Si la ligne correspond à une paire clé-valeur, on la gère
            elif key_value_pattern.match(line):
                self.handle_key_value(indent_level, line, line_number)
            else:
                # Si la ligne ne correspond à rien de valide, on déclenche une erreur
                self.handle_invalid_structure(indent_level, line, line_number)
        except Exception as e:
            # En cas d'erreur (comme une structure invalide), on marque le YAML comme invalide
            self.is_valid = False
            # Et on enregistre l'erreur avec la ligne où elle est survenue
            self.error_message = f"Error at line {line_number}: {str(e)}"
    
    # Fonction pour traiter les éléments de séquence (listes) dans le YAML
    def handle_sequence(self, indent_level, line, line_number):
        # On enlève les espaces et le tiret, et on récupère le contenu de l'élément
        sequence_content = line.lstrip()[1:].strip()  # Tout après le "-"

        # Si la pile est vide ou le niveau d'indentation est plus profond, on ajoute un niveau
        if not self.stack or indent_level > self.stack[-1]:
            self.stack.append(indent_level)
        elif indent_level < self.stack[-1]:
            # Si on est moins indenté que précédemment, on réajuste la pile
            while self.stack and indent_level < self.stack[-1]:
                self.stack.pop()

        # Si l'élément de la séquence contient un ":", c'est un début de clé-valeur
        if ':' in sequence_content:
            # Vérification de la bonne structure de la clé-valeur imbriquée
            nested_kv_pattern = re.compile(r'^\s*\w+:\s*.*$')
            if not nested_kv_pattern.match(sequence_content):
                raise ValueError(f"Invalid sequence item at line {line_number}: Incorrect nested key-value format")
    
    # Fonction pour traiter les paires clé-valeur dans le YAML
    def handle_key_value(self, indent_level, line, line_number):
        # Extraction de la clé et de la valeur via l'expression régulière
        match = re.match(r'^(\s*\w+):\s*(.*)$', line)
        key = match.group(1).strip()  # La clé est ce qui se trouve avant ":"
        value = match.group(2).strip() if match.group(2) else None  # La valeur est ce qui suit ":"

        # Si la pile est vide ou si on est à un niveau d'indentation plus profond, on ajoute ce niveau à la pile
        if not self.stack or indent_level > self.stack[-1]:
            self.stack.append(indent_level)
        elif indent_level < self.stack[-1]:
            # Sinon, on réajuste la pile si nécessaire
            while self.stack and indent_level < self.stack[-1]:
                self.stack.pop()

        # Vérification que la clé est bien présente
        if not key:
            raise ValueError(f"Invalid key-value pair at line {line_number}: Missing key")
        
        # Vérification que la valeur n'est pas vide et ne commence pas par un tiret (ce qui signifie une séquence imbriquée)
        if value and value.startswith('-'):
            raise ValueError(f"Invalid key-value pair at line {line_number}: Inline sequences are not allowed")
    
    # Si la ligne a une structure incorrecte (ni clé-valeur, ni séquence), on génère une erreur
    def handle_invalid_structure(self, indent_level, line, line_number):
        raise ValueError(f"Invalid structure at line {line_number}: Unexpected line content")

    # Fonction qui valide tout le fichier YAML en le lisant ligne par ligne
    def validate_yaml(self, file_path):
        try:
            with open(file_path, 'r') as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.rstrip()
                    if line:
                        self.process_line(line, line_number)
            return self.is_valid, self.error_message
        except IOError:
            return False, "Error: File could not be read."

# Exemple d'utilisation du validateur YAML
file_path = 'deployment.yaml'  
validator = YAMLValidator()  
is_valid, error_message = validator.validate_yaml(file_path) 

if is_valid:
    print("Valid YAML format")
else:
    print(f"Invalid YAML format: {error_message}")
