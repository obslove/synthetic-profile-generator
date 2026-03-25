from __future__ import annotations


TARGET_POOL_SIZE = 900


def _build_massive_pool(base: tuple[str, ...], *, target: int = TARGET_POOL_SIZE) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        if value not in seen:
            seen.add(value)
            ordered.append(value)

    for value in base:
        add(value)
    for left in base:
        for right in base:
            if left == right:
                continue
            add(f"{left}-{right}")
            if len(ordered) >= target:
                return tuple(ordered[:target])
    if len(ordered) < target:
        raise ValueError("Base pool is too small to reach the target size")
    return tuple(ordered[:target])


BR_MALE_BASE = (
    "Lucas", "Mateus", "Thiago", "Rafael", "Caio", "Bruno", "Gustavo", "Enzo", "Joao", "Pedro",
    "Gabriel", "Felipe", "Vinicius", "Andre", "Leandro", "Murilo", "Diego", "Daniel", "Eduardo", "Otavio",
    "Henrique", "Leonardo", "Marcelo", "Samuel", "Vitor", "Rodrigo", "Arthur", "Nicolas", "Yuri", "Alexandre",
    "Renan", "Wesley", "Matheus", "Igor", "Luiz", "Wellington", "Alan", "Cristiano", "Alisson", "Jonathan",
    "Ruan", "Carlos", "Roberto", "Ariel", "Breno", "Davi", "Fabricio", "Jean", "Luan", "Marlon",
    "Nathan", "Paulo", "Ricardo", "Sergio", "Tiago", "Valter", "Wagner", "William", "Heitor", "Jorge",
    "Lucca", "Raul", "Tales", "Ulysses", "Vitorino", "Adriano", "Emerson", "Fernando", "Hugo", "Icaro",
    "Jose", "Kaique", "Marcos", "Noah", "Patrick", "Ramon", "Saulo", "Tadeu", "Wallace", "Yago",
)

BR_FEMALE_BASE = (
    "Marina", "Camila", "Bianca", "Larissa", "Aline", "Renata", "Beatriz", "Luana", "Ana", "Julia",
    "Leticia", "Isabela", "Natalia", "Patricia", "Fernanda", "Gabriela", "Amanda", "Carolina", "Raquel", "Cecilia",
    "Helena", "Sofia", "Bruna", "Milena", "Daniela", "Yasmin", "Clara", "Melissa", "Laura", "Alice",
    "Mariana", "Paula", "Priscila", "Tatiane", "Vanessa", "Rafaela", "Samara", "Ariane", "Evelyn", "Flavia",
    "Geovana", "Ingrid", "Janaina", "Karen", "Livia", "Mirela", "Nayara", "Olivia", "Pamela", "Quezia",
    "Rosana", "Sabrina", "Talita", "Valeria", "Wanessa", "Yohana", "Zelia", "Adriana", "Barbara", "Cristiane",
    "Debora", "Elisa", "Fabiana", "Giovana", "Heloisa", "Iara", "Jade", "Katia", "Lorena", "Monique",
    "Nicole", "Paloma", "Roberta", "Sara", "Taina", "Vitoria", "Agatha", "Betina", "Catarina", "Dandara",
)

BR_SURNAME_BASE = (
    "Silveira", "Moraes", "Nogueira", "Lacerda", "Pimenta", "Teixeira", "Freitas", "Barbosa", "Cardoso", "Araujo",
    "Ferreira", "Almeida", "Costa", "Ribeiro", "Macedo", "Farias", "Siqueira", "Monteiro", "Lopes", "Campos",
    "Mendes", "Rezende", "Xavier", "Batista", "Vieira", "Rocha", "Tavares", "Moreira", "Cavalcanti", "Machado",
    "Santana", "Guimaraes", "Peixoto", "Queiroz", "Assis", "Borges", "Coelho", "Duarte", "Esteves", "Fonseca",
    "Gomes", "Haddad", "Ibrahim", "Junqueira", "Klein", "Lima", "Maia", "Neves", "Oliveira", "Prado",
    "Quintana", "Rangel", "Sales", "Toledo", "Uchoa", "Valenca", "Werneck", "Ximenes", "Yamamoto", "Zanetti",
    "Amorim", "Bernardes", "Cunha", "Domingues", "Evangelista", "Franco", "Garcia", "Henriques", "Izidio", "Jardim",
    "Kuster", "Leite", "Marques", "Nascimento", "Ornelas", "Portela", "Quevedo", "Ramos", "Soares", "Trindade",
)

US_MALE_BASE = (
    "Evan", "Miles", "Noah", "Caleb", "Owen", "Julian", "Nathan", "Levi", "Logan", "Connor",
    "Wyatt", "Asher", "Dylan", "Parker", "Ian", "Colin", "Adam", "Cole", "Micah", "Grant",
    "Roman", "Blake", "Hudson", "Elliot", "Theo", "Gavin", "Rowan", "Simon", "Landon", "Brody",
    "Chase", "Dean", "Emmett", "Finn", "Graham", "Hunter", "Jace", "Kai", "Maddox", "Nolan",
    "Orion", "Preston", "Quentin", "Reid", "Spencer", "Tanner", "Uriah", "Vincent", "Wesley", "Xavier",
    "Yates", "Zane", "Aiden", "Beckett", "Carson", "Damian", "Easton", "Felix", "Greyson", "Holden",
    "Isaac", "Jonah", "Knox", "Luca", "Milo", "Nash", "Oliver", "Porter", "Quincy", "Rhett",
    "Sawyer", "Trevor", "Vaughn", "Walker", "Zachary", "Avery", "Bennett", "Cameron", "Declan", "Everett",
)

US_FEMALE_BASE = (
    "Avery", "Maya", "Claire", "Sophie", "Nora", "Zoe", "Elise", "Naomi", "Hazel", "Lila",
    "Sadie", "Ruby", "Anna", "Lena", "Chloe", "Julia", "Mila", "Ivy", "Audrey", "Lucy",
    "Paige", "Molly", "Violet", "Ellie", "Brooke", "Quinn", "Kira", "Cora", "Addison", "Brielle",
    "Caroline", "Delaney", "Emery", "Finley", "Georgia", "Hadley", "Isla", "Jocelyn", "Kennedy", "Lainey",
    "Madeline", "Noelle", "Oakley", "Piper", "Reese", "Stella", "Tessa", "Valerie", "Willa", "Xena",
    "Yvette", "Zara", "Abigail", "Bella", "Callie", "Daphne", "Eva", "Fiona", "Gemma", "Harper",
    "Indie", "Josephine", "Kendall", "Lorelei", "Margot", "Nina", "Olive", "Phoebe", "Rosalie", "Sienna",
    "Teagan", "Veronica", "Whitney", "Yara", "Adeline", "Brynn", "Celeste", "Daisy", "Elsie", "Frankie",
)

US_SURNAME_BASE = (
    "Walker", "Bennett", "Parker", "Hayes", "Morgan", "Cooper", "Foster", "Reed", "Harper", "Miller",
    "Sullivan", "Baker", "Porter", "Jensen", "Howard", "Bailey", "Murphy", "Ross", "Price", "Coleman",
    "Powell", "Carter", "Bryant", "Ward", "Sanders", "Myers", "Perry", "Fisher", "Griffin", "Brooks",
    "Adams", "Barnes", "Chapman", "Donovan", "Ellis", "Franklin", "Garrett", "Hawkins", "Irving", "Jacobs",
    "Keller", "Lawson", "Mason", "Norris", "Owens", "Palmer", "Quincy", "Russell", "Shaw", "Turner",
    "Underwood", "Vance", "Warren", "Young", "Zimmerman", "Aldridge", "Bradley", "Crawford", "Dalton", "Edwards",
    "Farrell", "Gibson", "Holland", "Ingram", "Jefferson", "Kendrick", "Lambert", "Monroe", "Nichols", "Osborne",
    "Prescott", "Ramsey", "Shelton", "Townsend", "Valentine", "Winters", "York", "Abbott", "Bishop", "Cross",
)

FR_MALE_BASE = (
    "Lucas", "Theo", "Jules", "Maxime", "Leo", "Noe", "Adrien", "Arthur", "Bastien", "Nathan",
    "Hugo", "Enzo", "Louis", "Tom", "Victor", "Alexis", "Romain", "Mathis", "Paul", "Gabriel",
    "Antoine", "Clement", "Tristan", "Eliott", "Quentin", "Robin", "Amaury", "Benoit", "Cedric", "Damien",
    "Etienne", "Fabien", "Gaspard", "Henri", "Ismael", "Jean", "Kevin", "Laurent", "Martin", "Nicolas",
    "Octave", "Pierre", "Raphael", "Sebastien", "Thierry", "Ulysse", "Valentin", "William", "Yanis", "Zacharie",
    "Alban", "Brice", "Corentin", "Dorian", "Edouard", "Florian", "Guillaume", "Helios", "Ilan", "Jerome",
    "Killian", "Loic", "Mael", "Nolan", "Oscar", "Pascal", "Remi", "Sylvain", "Titouan", "Vivien",
    "Walid", "Yohann", "Achille", "Baptiste", "Charles", "Denis", "Emilien", "Felix", "Gregoire", "Joris",
)

FR_FEMALE_BASE = (
    "Emma", "Chloe", "Ines", "Camille", "Louise", "Manon", "Jade", "Nina", "Sarah", "Lea",
    "Zoe", "Lucie", "Jeanne", "Alice", "Eva", "Clara", "Lina", "Elsa", "Anais", "Juliette",
    "Margot", "Amelie", "Noemie", "Marine", "Celia", "Mila", "Adele", "Berenice", "Capucine", "Delphine",
    "Elodie", "Fanny", "Garance", "Helene", "Iris", "Josephine", "Karine", "Laure", "Maeva", "Nadege",
    "Oceane", "Pauline", "Quitterie", "Romane", "Salome", "Tiphaine", "Victoire", "Wendy", "Yasmine", "Aurore",
    "Brune", "Coralie", "Diane", "Estelle", "Flavie", "Gaelle", "Hortense", "Ingrid", "Justine", "Laurine",
    "Melanie", "Nora", "Ophelie", "Penelope", "Raphaelle", "Solene", "Thea", "Valentine", "Ysee", "Aline",
    "Bianca", "Caroline", "Domitille", "Emilie", "Fleur", "Gaia", "Honorine", "Leonie", "Maud", "Ninon",
)

FR_SURNAME_BASE = (
    "Mercier", "Roux", "Blanchard", "Chevalier", "Garnier", "Colin", "Perrin", "Marchand", "Lambert", "Fabre",
    "Moreau", "Andre", "Fontaine", "Leroy", "Boyer", "Gautier", "Barbier", "Renard", "Dupont", "Caron",
    "Lopez", "Meyer", "Renaud", "Julien", "Aubry", "Masson", "Bertrand", "Charrier", "Delorme", "Etienne",
    "Fournier", "Girard", "Hubert", "Imbert", "Joly", "Klein", "Lemoine", "Morin", "Navarro", "Olivier",
    "Pichon", "Quentin", "Riviere", "Savary", "Tessier", "Vidal", "Wagner", "Yvard", "Zeller", "Arnaud",
    "Bourgeois", "Chauvin", "Deschamps", "Esnault", "Fleury", "Gaudin", "Hebert", "Isnard", "Jourdan", "Lacroix",
    "Monnier", "Nicolas", "Perrot", "Richard", "Schmitt", "Texier", "Vaillant", "Weber", "Briand", "Cousin",
    "Deniau", "Forest", "Giraud", "Hamon", "Lefort", "Pons", "Rey", "Simon", "Teillard", "Vasseur",
)


NAME_POOLS: dict[str, dict[str, tuple[str, ...]]] = {
    "BR": {
        "male": _build_massive_pool(BR_MALE_BASE),
        "female": _build_massive_pool(BR_FEMALE_BASE),
        "surnames": _build_massive_pool(BR_SURNAME_BASE),
    },
    "US": {
        "male": _build_massive_pool(US_MALE_BASE),
        "female": _build_massive_pool(US_FEMALE_BASE),
        "surnames": _build_massive_pool(US_SURNAME_BASE),
    },
    "FR": {
        "male": _build_massive_pool(FR_MALE_BASE),
        "female": _build_massive_pool(FR_FEMALE_BASE),
        "surnames": _build_massive_pool(FR_SURNAME_BASE),
    },
}


def names_for(country_code: str, kind: str) -> tuple[str, ...]:
    return NAME_POOLS[country_code][kind]
