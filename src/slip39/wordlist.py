"""
SLIP-39 Wordlist Management

This module contains the official SLIP-39 wordlist of 1024 words and provides
conversion functions between words, indices, and integers.

The wordlist has the following properties:
- Exactly 1024 words (2^10)
- Each word has a unique 4-letter prefix
- Words are sorted alphabetically
- Compatible with Trezor's python-shamir-mnemonic implementation
"""

from typing import List, Sequence, Optional


# Official SLIP-39 wordlist (1024 words)
# Source: https://github.com/satoshilabs/slips/blob/master/slip-0039/wordlist.txt
WORDLIST = [
    "academic", "acid", "acne", "acquire", "acrobat", "activity", "actress", "adapt",
    "adequate", "adjust", "admit", "adorn", "adult", "advance", "advocate", "afraid",
    "again", "agency", "agree", "aide", "aircraft", "airline", "airport", "ajar",
    "alarm", "album", "alcohol", "alien", "alive", "alpha", "already", "alto",
    "aluminum", "always", "amazing", "ambition", "amount", "amuse", "analysis", "anatomy",
    "ancestor", "ancient", "angel", "angry", "animal", "answer", "antenna", "anxiety",
    "apart", "aquatic", "arcade", "arena", "argue", "armed", "artist", "artwork",
    "aspect", "auction", "august", "aunt", "average", "aviation", "avoid", "award",
    "away", "axis", "axle", "beam", "beard", "beaver", "become", "bedroom",
    "behavior", "being", "believe", "belong", "benefit", "best", "beyond", "bike",
    "biology", "birthday", "bishop", "black", "blanket", "blessing", "blimp", "blind",
    "blue", "body", "bolt", "boring", "born", "both", "boundary", "bracelet",
    "branch", "brave", "breathe", "briefing", "broken", "brother", "browser", "bucket",
    "budget", "building", "bulb", "bulge", "bumpy", "bundle", "burden", "burning",
    "busy", "buyer", "cage", "calcium", "camera", "campus", "canyon", "capacity",
    "capital", "capture", "carbon", "cards", "careful", "cargo", "carpet", "carve",
    "category", "cause", "ceiling", "center", "ceramic", "champion", "change", "charity",
    "check", "chemical", "chest", "chew", "chubby", "cinema", "civil", "class",
    "clay", "cleanup", "client", "climate", "clinic", "clock", "clogs", "closet",
    "clothes", "club", "cluster", "coal", "coastal", "coding", "column", "company",
    "corner", "costume", "counter", "course", "cover", "cowboy", "cradle", "craft",
    "crazy", "credit", "cricket", "criminal", "crisis", "critical", "crowd", "crucial",
    "crunch", "crush", "crystal", "cubic", "cultural", "curious", "curly", "custody",
    "cylinder", "daisy", "damage", "dance", "darkness", "database", "daughter", "deadline",
    "deal", "debris", "debut", "decent", "decision", "declare", "decorate", "decrease",
    "deliver", "demand", "density", "deny", "depart", "depend", "depict", "deploy",
    "describe", "desert", "desire", "desktop", "destroy", "detailed", "detect", "device",
    "devote", "diagnose", "dictate", "diet", "dilemma", "diminish", "dining", "diploma",
    "disaster", "discuss", "disease", "dish", "dismiss", "display", "distance", "dive",
    "divorce", "document", "domain", "domestic", "dominant", "dough", "downtown", "dragon",
    "dramatic", "dream", "dress", "drift", "drink", "drove", "drug", "dryer",
    "duckling", "duke", "duration", "dwarf", "dynamic", "early", "earth", "easel",
    "easy", "echo", "eclipse", "ecology", "edge", "editor", "educate", "either",
    "elbow", "elder", "election", "elegant", "element", "elephant", "elevator", "elite",
    "else", "email", "emerald", "emission", "emperor", "emphasis", "employer", "empty",
    "ending", "endless", "endorse", "enemy", "energy", "enforce", "engage", "enjoy",
    "enlarge", "entrance", "envelope", "envy", "epidemic", "episode", "equation", "equip",
    "eraser", "erode", "escape", "estate", "estimate", "evaluate", "evening", "evidence",
    "evil", "evoke", "exact", "example", "exceed", "exchange", "exclude", "excuse",
    "execute", "exercise", "exhaust", "exotic", "expand", "expect", "explain", "express",
    "extend", "extra", "eyebrow", "facility", "fact", "failure", "faint", "fake",
    "false", "family", "famous", "fancy", "fangs", "fantasy", "fatal", "fatigue",
    "favorite", "fawn", "fiber", "fiction", "filter", "finance", "findings", "finger",
    "firefly", "firm", "fiscal", "fishing", "fitness", "flame", "flash", "flavor",
    "flea", "flexible", "flip", "float", "floral", "fluff", "focus", "forbid",
    "force", "forecast", "forget", "formal", "fortune", "forward", "founder", "fraction",
    "fragment", "frequent", "freshman", "friar", "fridge", "friendly", "frost", "froth",
    "frozen", "fumes", "funding", "furl", "fused", "galaxy", "game", "garbage",
    "garden", "garlic", "gasoline", "gather", "general", "genius", "genre", "genuine",
    "geology", "gesture", "glad", "glance", "glasses", "glen", "glimpse", "goat",
    "golden", "graduate", "grant", "grasp", "gravity", "gray", "greatest", "grief",
    "grill", "grin", "grocery", "gross", "group", "grownup", "grumpy", "guard",
    "guest", "guilt", "guitar", "gums", "hairy", "hamster", "hand", "hanger",
    "harvest", "have", "havoc", "hawk", "hazard", "headset", "health", "hearing",
    "heat", "helpful", "herald", "herd", "hesitate", "hobo", "holiday", "holy",
    "home", "hormone", "hospital", "hour", "huge", "human", "humidity", "hunting",
    "husband", "hush", "husky", "hybrid", "idea", "identify", "idle", "image",
    "impact", "imply", "improve", "impulse", "include", "income", "increase", "index",
    "indicate", "industry", "infant", "inform", "inherit", "injury", "inmate", "insect",
    "inside", "install", "intend", "intimate", "invasion", "involve", "iris", "island",
    "isolate", "item", "ivory", "jacket", "jerky", "jewelry", "join", "judicial",
    "juice", "jump", "junction", "junior", "junk", "jury", "justice", "kernel",
    "keyboard", "kidney", "kind", "kitchen", "knife", "knit", "laden", "ladle",
    "ladybug", "lair", "lamp", "language", "large", "laser", "laundry", "lawsuit",
    "leader", "leaf", "learn", "leaves", "lecture", "legal", "legend", "legs",
    "lend", "length", "level", "liberty", "library", "license", "lift", "likely",
    "lilac", "lily", "lips", "liquid", "listen", "literary", "living", "lizard",
    "loan", "lobe", "location", "losing", "loud", "loyalty", "luck", "lunar",
    "lunch", "lungs", "luxury", "lying", "lyrics", "machine", "magazine", "maiden",
    "mailman", "main", "makeup", "making", "mama", "manager", "mandate", "mansion",
    "manual", "marathon", "march", "market", "marvel", "mason", "material", "math",
    "maximum", "mayor", "meaning", "medal", "medical", "member", "memory", "mental",
    "merchant", "merit", "method", "metric", "midst", "mild", "military", "mineral",
    "minister", "miracle", "mixed", "mixture", "mobile", "modern", "modify", "moisture",
    "moment", "morning", "mortgage", "mother", "mountain", "mouse", "move", "much",
    "mule", "multiple", "muscle", "museum", "music", "mustang", "nail", "national",
    "necklace", "negative", "nervous", "network", "news", "nuclear", "numb", "numerous",
    "nylon", "oasis", "obesity", "object", "observe", "obtain", "ocean", "often",
    "olympic", "omit", "oral", "orange", "orbit", "order", "ordinary", "organize",
    "ounce", "oven", "overall", "owner", "paces", "pacific", "package", "paid",
    "painting", "pajamas", "pancake", "pants", "papa", "paper", "parcel", "parking",
    "party", "patent", "patrol", "payment", "payroll", "peaceful", "peanut", "peasant",
    "pecan", "penalty", "pencil", "percent", "perfect", "permit", "petition", "phantom",
    "pharmacy", "photo", "phrase", "physics", "pickup", "picture", "piece", "pile",
    "pink", "pipeline", "pistol", "pitch", "plains", "plan", "plastic", "platform",
    "playoff", "pleasure", "plot", "plunge", "practice", "prayer", "preach", "predator",
    "pregnant", "premium", "prepare", "presence", "prevent", "priest", "primary", "priority",
    "prisoner", "privacy", "prize", "problem", "process", "profile", "program", "promise",
    "prospect", "provide", "prune", "public", "pulse", "pumps", "punish", "puny",
    "pupal", "purchase", "purple", "python", "quantity", "quarter", "quick", "quiet",
    "race", "racism", "radar", "railroad", "rainbow", "raisin", "random", "ranked",
    "rapids", "raspy", "reaction", "realize", "rebound", "rebuild", "recall", "receiver",
    "recover", "regret", "regular", "reject", "relate", "remember", "remind", "remove",
    "render", "repair", "repeat", "replace", "require", "rescue", "research", "resident",
    "response", "result", "retailer", "retreat", "reunion", "revenue", "review", "reward",
    "rhyme", "rhythm", "rich", "rival", "river", "robin", "rocky", "romantic",
    "romp", "roster", "round", "royal", "ruin", "ruler", "rumor", "sack",
    "safari", "salary", "salon", "salt", "satisfy", "satoshi", "saver", "says",
    "scandal", "scared", "scatter", "scene", "scholar", "science", "scout", "scramble",
    "screw", "script", "scroll", "seafood", "season", "secret", "security", "segment",
    "senior", "shadow", "shaft", "shame", "shaped", "sharp", "shelter", "sheriff",
    "short", "should", "shrimp", "sidewalk", "silent", "silver", "similar", "simple",
    "single", "sister", "skin", "skunk", "slap", "slavery", "sled", "slice",
    "slim", "slow", "slush", "smart", "smear", "smell", "smirk", "smith",
    "smoking", "smug", "snake", "snapshot", "sniff", "society", "software", "soldier",
    "solution", "soul", "source", "space", "spark", "speak", "species", "spelling",
    "spend", "spew", "spider", "spill", "spine", "spirit", "spit", "spray",
    "sprinkle", "square", "squeeze", "stadium", "staff", "standard", "starting", "station",
    "stay", "steady", "step", "stick", "stilt", "story", "strategy", "strike",
    "style", "subject", "submit", "sugar", "suitable", "sunlight", "superior", "surface",
    "surprise", "survive", "sweater", "swimming", "swing", "switch", "symbolic", "sympathy",
    "syndrome", "system", "tackle", "tactics", "tadpole", "talent", "task", "taste",
    "taught", "taxi", "teacher", "teammate", "teaspoon", "temple", "tenant", "tendency",
    "tension", "terminal", "testify", "texture", "thank", "that", "theater", "theory",
    "therapy", "thorn", "threaten", "thumb", "thunder", "ticket", "tidy", "timber",
    "timely", "ting", "tofu", "together", "tolerate", "total", "toxic", "tracks",
    "traffic", "training", "transfer", "trash", "traveler", "treat", "trend", "trial",
    "tricycle", "trip", "triumph", "trouble", "true", "trust", "twice", "twin",
    "type", "typical", "ugly", "ultimate", "umbrella", "uncover", "undergo", "unfair",
    "unfold", "unhappy", "union", "universe", "unkind", "unknown", "unusual", "unwrap",
    "upgrade", "upstairs", "username", "usher", "usual", "valid", "valuable", "vampire",
    "vanish", "various", "vegan", "velvet", "venture", "verdict", "verify", "very",
    "veteran", "vexed", "victim", "video", "view", "vintage", "violence", "viral",
    "visitor", "visual", "vitamins", "vocal", "voice", "volume", "voter", "voting",
    "walnut", "warmth", "warn", "watch", "wavy", "wealthy", "weapon", "webcam",
    "welcome", "welfare", "western", "width", "wildlife", "window", "wine", "wireless",
    "wisdom", "withdraw", "wits", "wolf", "woman", "work", "worthy", "wrap",
    "wrist", "writing", "wrote", "year", "yelp", "yield", "yoga", "zero",
]

# Pre-compute word-to-index mapping for O(1) lookups
_WORD_TO_INDEX = {word: idx for idx, word in enumerate(WORDLIST)}

# Pre-compute 4-letter prefix mapping for partial word matching
_PREFIX_TO_INDEX = {word[:4]: idx for idx, word in enumerate(WORDLIST)}


def word_to_index(word: str) -> Optional[int]:
    """
    Convert a word to its index in the SLIP-39 wordlist.
    
    Supports both full words and 4-letter prefixes.
    
    Args:
        word: A word from the SLIP-39 wordlist (case-insensitive)
    
    Returns:
        Index (0-1023) or None if word not found
    
    Example:
        >>> word_to_index("academic")
        0
        >>> word_to_index("acad")  # 4-letter prefix
        0
        >>> word_to_index("zero")
        1023
    """
    word_lower = word.lower().strip()
    
    # Try exact match first
    if word_lower in _WORD_TO_INDEX:
        return _WORD_TO_INDEX[word_lower]
    
    # Try 4-letter prefix match
    if len(word_lower) >= 4 and word_lower[:4] in _PREFIX_TO_INDEX:
        return _PREFIX_TO_INDEX[word_lower[:4]]
    
    return None


def index_to_word(index: int) -> str:
    """
    Convert an index to its corresponding word in the SLIP-39 wordlist.
    
    Args:
        index: Index (0-1023)
    
    Returns:
        Word from SLIP-39 wordlist
    
    Raises:
        IndexError: If index is out of range
    
    Example:
        >>> index_to_word(0)
        'academic'
        >>> index_to_word(1023)
        'zero'
    """
    if not 0 <= index < 1024:
        raise IndexError(f"Index {index} out of range (0-1023)")
    
    return WORDLIST[index]


def words_to_indices(words: Sequence[str]) -> List[int]:
    """
    Convert a sequence of words to their indices.
    
    Args:
        words: Sequence of words from SLIP-39 wordlist
    
    Returns:
        List of indices (0-1023)
    
    Raises:
        ValueError: If any word is not in the wordlist
    
    Example:
        >>> words_to_indices(["academic", "acid", "acne"])
        [0, 1, 2]
    """
    indices = []
    for word in words:
        idx = word_to_index(word)
        if idx is None:
            raise ValueError(f"Word '{word}' not in SLIP-39 wordlist")
        indices.append(idx)
    
    return indices


def indices_to_words(indices: Sequence[int]) -> List[str]:
    """
    Convert a sequence of indices to their corresponding words.
    
    Args:
        indices: Sequence of indices (0-1023)
    
    Returns:
        List of words from SLIP-39 wordlist
    
    Raises:
        IndexError: If any index is out of range
    
    Example:
        >>> indices_to_words([0, 1, 2])
        ['academic', 'acid', 'acne']
    """
    return [index_to_word(idx) for idx in indices]


def mnemonic_to_indices(mnemonic: str) -> List[int]:
    """
    Convert a mnemonic phrase (space-separated words) to indices.
    
    Args:
        mnemonic: Space-separated words from SLIP-39 wordlist
    
    Returns:
        List of indices (0-1023)
    
    Raises:
        ValueError: If any word is not in the wordlist
    
    Example:
        >>> mnemonic_to_indices("academic acid acne")
        [0, 1, 2]
    """
    words = mnemonic.strip().split()
    return words_to_indices(words)


def indices_to_mnemonic(indices: Sequence[int]) -> str:
    """
    Convert a sequence of indices to a mnemonic phrase.
    
    Args:
        indices: Sequence of indices (0-1023)
    
    Returns:
        Space-separated words forming mnemonic phrase
    
    Raises:
        IndexError: If any index is out of range
    
    Example:
        >>> indices_to_mnemonic([0, 1, 2])
        'academic acid acne'
    """
    words = indices_to_words(indices)
    return " ".join(words)


def int_to_indices(value: int, word_count: int) -> List[int]:
    """
    Convert an integer to a list of word indices (base-1024 encoding).
    
    Args:
        value: Integer value to encode
        word_count: Number of words to generate (pads with zeros if needed)
    
    Returns:
        List of indices representing the integer in base-1024
    
    Example:
        >>> int_to_indices(1025, 2)  # 1025 = 1*1024 + 1
        [1, 1]
        >>> int_to_indices(5, 3)
        [0, 0, 5]
    """
    if value < 0:
        raise ValueError("Value must be non-negative")
    
    indices = []
    for _ in range(word_count):
        indices.append(value % 1024)
        value //= 1024
    
    # Reverse to have most significant word first
    return list(reversed(indices))


def indices_to_int(indices: Sequence[int]) -> int:
    """
    Convert a list of word indices to an integer (base-1024 decoding).
    
    Args:
        indices: Sequence of indices (0-1023)
    
    Returns:
        Integer value represented by the indices
    
    Example:
        >>> indices_to_int([1, 1])  # 1*1024 + 1
        1025
        >>> indices_to_int([0, 0, 5])
        5
    """
    value = 0
    for idx in indices:
        if not 0 <= idx < 1024:
            raise ValueError(f"Index {idx} out of range (0-1023)")
        value = value * 1024 + idx
    
    return value


def validate_wordlist() -> bool:
    """
    Validate that the wordlist meets SLIP-39 requirements.
    
    Checks:
    - Exactly 1024 words
    - All words are unique
    - All 4-letter prefixes are unique
    - Words are sorted alphabetically
    
    Returns:
        True if all validations pass
    
    Raises:
        AssertionError: If any validation fails
    """
    # Check count
    assert len(WORDLIST) == 1024, f"Expected 1024 words, got {len(WORDLIST)}"
    
    # Check uniqueness
    assert len(set(WORDLIST)) == 1024, "Words are not unique"
    
    # Check 4-letter prefix uniqueness
    prefixes = [word[:4] for word in WORDLIST]
    assert len(set(prefixes)) == 1024, "4-letter prefixes are not unique"
    
    # Check alphabetical sorting
    sorted_list = sorted(WORDLIST)
    assert WORDLIST == sorted_list, "Words are not sorted alphabetically"
    
    return True


# Export public API
__all__ = [
    'WORDLIST',
    'word_to_index',
    'index_to_word',
    'words_to_indices',
    'indices_to_words',
    'mnemonic_to_indices',
    'indices_to_mnemonic',
    'int_to_indices',
    'indices_to_int',
    'validate_wordlist',
]
