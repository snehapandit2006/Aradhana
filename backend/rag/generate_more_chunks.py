import json
import os

new_entries = [
    # --- Moon Signs (astro_081 to astro_092) ---
    {
        "id": "astro_081",
        "category": "moon_signs",
        "topic": "Moon in Aries",
        "text": "Moon in Aries individuals process emotions through immediate action and assertiveness. They feel secure when they can lead, initiate, and tackle challenges directly. Their emotional responses are quick, passionate, and sometimes impulsive. The shadow side is a tendency toward impatience, quick-tempered outbursts, and emotional self-centeredness.",
        "tags": ["moon", "aries", "emotions", "temper"]
    },
    {
        "id": "astro_082",
        "category": "moon_signs",
        "topic": "Moon in Taurus",
        "text": "Moon in Taurus is in its exaltation, bringing emotional stability, patience, and a deep need for physical comfort and financial security. These individuals react calmly to stress and nurture themselves through sensory pleasures and nature. Their shadow trait is stubbornness, resisting emotional change, and over-eating or hoarding for comfort.",
        "tags": ["moon", "taurus", "exaltation", "stability"]
    },
    {
        "id": "astro_083",
        "category": "moon_signs",
        "topic": "Moon in Gemini",
        "text": "Moon in Gemini individuals intellectualize their feelings, needing to talk, write, or think through their emotions to feel secure. They are curious, adaptable, and enjoy socializing to process moods. The shadow side manifests as nervous restlessness, superficiality, and avoiding deep emotional truths through constant talking.",
        "tags": ["moon", "gemini", "mind", "intellect"]
    },
    {
        "id": "astro_084",
        "category": "moon_signs",
        "topic": "Moon in Cancer",
        "text": "Moon in Cancer is in its home sign, indicating intense emotional depth, strong intuition, and a maternal, nurturing instinct. These individuals are deeply attached to their home and family. The shadow manifests as defensiveness (retreating into their shell), moodiness, and holding onto emotional history and grudges.",
        "tags": ["moon", "cancer", "nurturing", "moody"]
    },
    {
        "id": "astro_085",
        "category": "moon_signs",
        "topic": "Moon in Leo",
        "text": "Moon in Leo individuals have a warm, generous, and theatrical emotional nature. They feel secure when they are appreciated, loved, and given creative attention. Their shadow manifests as dramatic reactions, pride, vulnerability to criticism, and a constant need for external praise and validation.",
        "tags": ["moon", "leo", "pride", "attention"]
    },
    {
        "id": "astro_086",
        "category": "moon_signs",
        "topic": "Moon in Virgo",
        "text": "Moon in Virgo individuals seek emotional safety through order, clean routines, service, and analysis. They show love by being useful and helping with practical details. The shadow side shows up as perfectionism, hyper-criticism of self and others, and excessive anxiety or worrying about health.",
        "tags": ["moon", "virgo", "service", "worry"]
    },
    {
        "id": "astro_087",
        "category": "moon_signs",
        "topic": "Moon in Libra",
        "text": "Moon in Libra individuals need relational harmony, peace, and aesthetic balance to feel emotionally secure. They are diplomatic and hate conflict, often acting as peacemakers. The shadow side manifests as people-pleasing, codependency, and indecisiveness when their personal needs clash with others.",
        "tags": ["moon", "libra", "harmony", "diplomacy"]
    },
    {
        "id": "astro_088",
        "category": "moon_signs",
        "topic": "Moon in Scorpio",
        "text": "Moon in Scorpio is in its fall, representing an intense, passionate, and highly private emotional nature. These individuals feel feelings deeply and possess powerful psychological intuition. The shadow side involves secrecy, jealousy, holding onto resentments, and a need to control emotional environments.",
        "tags": ["moon", "scorpio", "intensity", "privacy"]
    },
    {
        "id": "astro_089",
        "category": "moon_signs",
        "topic": "Moon in Sagittarius",
        "text": "Moon in Sagittarius individuals feel emotionally secure when they have freedom, space to explore, and a sense of optimism. They process feelings through travel, philosophy, and humor. Their shadow side is a tendency to escape emotional pain through excess, restlessness, and being blunt or insensitive.",
        "tags": ["moon", "sagittarius", "freedom", "optimism"]
    },
    {
        "id": "astro_090",
        "category": "moon_signs",
        "topic": "Moon in Capricorn",
        "text": "Moon in Capricorn is in its detriment, indicating a reserved, disciplined, and emotionally cautious nature. They feel secure when they are in control, achieving goals, and maintaining structure. The shadow manifests as emotional rigidity, depressing thoughts, workaholism, and difficulty showing vulnerability.",
        "tags": ["moon", "capricorn", "control", "detriment"]
    },
    {
        "id": "astro_091",
        "category": "moon_signs",
        "topic": "Moon in Aquarius",
        "text": "Moon in Aquarius individuals process feelings intellectually and value emotional independence. They feel secure when they can contribute to a group or humanitarian cause. Their shadow side involves emotional detachment, aloofness, and intellectualizing feelings rather than experiencing them.",
        "tags": ["moon", "aquarius", "independence", "detachment"]
    },
    {
        "id": "astro_092",
        "category": "moon_signs",
        "topic": "Moon in Pisces",
        "text": "Moon in Pisces individuals are highly compassionate, empathetic, and absorb the emotional energies of their surroundings. They have a rich dream life and express their moods through art or spirituality. Their shadow side shows up as lack of boundaries, escapism, and adopting a victim or martyr persona.",
        "tags": ["moon", "pisces", "empathy", "escapism"]
    },
    
    # --- Ascendant Signs (astro_093 to astro_104) ---
    {
        "id": "astro_093",
        "category": "ascendant",
        "topic": "Taurus Rising",
        "text": "Taurus Rising individuals project a calm, steady, and attractive presence. They approach the world with caution, valuing physical comfort, stability, and aesthetic beauty. They are seen as reliable, patient, and grounded. The ruling planet Venus indicates that relationships and resources play a key role in their life path.",
        "tags": ["ascendant", "taurus", "rising", "presence"]
    },
    {
        "id": "astro_094",
        "category": "ascendant",
        "topic": "Gemini Rising",
        "text": "Gemini Rising individuals appear quick-witted, sociable, and intellectually curious. They approach life as a learning experiment, engaging in conversations and gathering information. They look youthful and move quickly. The ruling planet Mercury indicates that writing, speaking, and learning are central to their path.",
        "tags": ["ascendant", "gemini", "rising", "mind"]
    },
    {
        "id": "astro_095",
        "category": "ascendant",
        "topic": "Cancer Rising",
        "text": "Cancer Rising individuals project a nurturing, gentle, and highly sensitive aura. They approach the world defensively at first, checking emotional safety before opening up. They value home and family. The ruling Moon indicates that emotional cycles and domestic foundations are central to their destiny.",
        "tags": ["ascendant", "cancer", "rising", "empathy"]
    },
    {
        "id": "astro_096",
        "category": "ascendant",
        "topic": "Leo Rising",
        "text": "Leo Rising individuals project a radiant, dramatic, and proud presence. They walk into rooms with confidence, showing warmth and creativity. They value self-expression and leadership. The ruling Sun indicates that developing a healthy ego and receiving public appreciation are central to their life journey.",
        "tags": ["ascendant", "leo", "rising", "radiance"]
    },
    {
        "id": "astro_097",
        "category": "ascendant",
        "topic": "Virgo Rising",
        "text": "Virgo Rising individuals project a clean, organized, helpful, and modest appearance. They approach life analytically, paying attention to details and scheduling. They are seen as reliable and health-conscious. The ruling Mercury indicates that daily service, writing, and practical tasks are central to their path.",
        "tags": ["ascendant", "virgo", "rising", "analytical"]
    },
    {
        "id": "astro_098",
        "category": "ascendant",
        "topic": "Libra Rising",
        "text": "Libra Rising individuals project a charming, diplomatic, and aesthetically pleasing presence. They approach the world seeking partnership, harmony, and balance, trying to make everyone comfortable. The ruling Venus indicates that relationships, art, and justice are central themes in their destiny.",
        "tags": ["ascendant", "libra", "rising", "charm"]
    },
    {
        "id": "astro_099",
        "category": "ascendant",
        "topic": "Scorpio Rising",
        "text": "Scorpio Rising individuals project an intense, magnetic, and highly private aura. They approach the world with caution, observing hidden dynamics and motivations. They are seen as powerful and mysterious. The ruling Pluto and Mars indicate that transformation, crisis, and power are central to their life.",
        "tags": ["ascendant", "scorpio", "rising", "power"]
    },
    {
        "id": "astro_100",
        "category": "ascendant",
        "topic": "Sagittarius Rising",
        "text": "Sagittarius Rising individuals project an optimistic, adventurous, and friendly presence. They approach life as a quest for truth and adventure, showing a love for travel and philosophy. They are generous and funny. The ruling Jupiter indicates that growth, faith, and higher learning are central to their destiny.",
        "tags": ["ascendant", "sagittarius", "rising", "adventure"]
    },
    {
        "id": "astro_101",
        "category": "ascendant",
        "topic": "Capricorn Rising",
        "text": "Capricorn Rising individuals project a mature, serious, and highly professional presence. They approach the world cautiously, valuing structure, time, and long-term goals. They are seen as authoritative and disciplined. The ruling Saturn indicates that career achievements and duty are central to their destiny.",
        "tags": ["ascendant", "capricorn", "rising", "authority"]
    },
    {
        "id": "astro_102",
        "category": "ascendant",
        "topic": "Aquarius Rising",
        "text": "Aquarius Rising individuals project an original, intellectual, and slightly detached presence. They approach life with progressive, humanitarian ideals, valuing community and independence. The ruling Saturn and Uranus indicate that social reform, technology, and eccentricity are central themes.",
        "tags": ["ascendant", "aquarius", "rising", "originality"]
    },
    {
        "id": "astro_103",
        "category": "ascendant",
        "topic": "Pisces Rising",
        "text": "Pisces Rising individuals project a soft, dreamy, and highly compassionate presence. They approach the world with sensitivity and imagination, appearing artistic or spiritually receptive. The ruling Neptune and Jupiter indicate that spiritual surrender, dreams, and creative arts are central to their path.",
        "tags": ["ascendant", "pisces", "rising", "dreamy"]
    },
    
    # --- Planet-in-House Additions (astro_104 to astro_120) ---
    {
        "id": "astro_104",
        "category": "placements",
        "topic": "Jupiter in the 9th House",
        "text": "Jupiter in the 9th House is in its natural home, representing an abundance of luck and growth in higher education, travel, publishing, and philosophical pursuits. These individuals have strong faith, an open mind, and enjoy exploring foreign lands and belief systems. The shadow side can manifest as self-righteousness.",
        "tags": ["jupiter", "9th_house", "travel", "philosophy", "growth"]
    },
    {
        "id": "astro_105",
        "category": "placements",
        "topic": "Venus in the 5th House",
        "text": "Venus in the 5th House brings love, harmony, and joy to creative hobbies, romance, play, and children. These individuals are charming, expressive, and attract romantic partners easily. They appreciate art, theater, and luxury games. The shadow side involves romantic drama and seeking constant attention.",
        "tags": ["venus", "5th_house", "romance", "creativity", "play"]
    },
    {
        "id": "astro_106",
        "category": "placements",
        "topic": "Saturn in the 10th House",
        "text": "Saturn in the 10th House indicates that career, public reputation, and status are areas of deep responsibility, hard work, and ultimate mastery. Success is built slowly through discipline, organization, and patience. The shadow side shows up as fear of public failure, career delays, and over-identifying with status.",
        "tags": ["saturn", "10th_house", "career", "reputation", "mastery"]
    },
    {
        "id": "astro_107",
        "category": "placements",
        "topic": "Uranus in the 11th House",
        "text": "Uranus in the 11th House indicates a unique, original, and independent approach to friendships, communities, and group activities. These individuals are attracted to eccentric, progressive, or activist circles and value intellectual freedom. The shadow side involves sudden friend breakups and rebellion against community rules.",
        "tags": ["uranus", "11th_house", "friends", "groups", "freedom"]
    },
    {
        "id": "astro_108",
        "category": "placements",
        "topic": "Mercury in the 1st House",
        "text": "Mercury in the 1st House indicates an active, talkative, and highly communicative personality. These individuals express their thoughts quickly, project a youthful aura, and analyze everything around them. The shadow side can lead to nervous tension, talking too much, and difficulty listening to other perspectives.",
        "tags": ["mercury", "1st_house", "communication", "youthful", "mind"]
    },
    {
        "id": "astro_109",
        "category": "placements",
        "topic": "Pluto in the 8th House",
        "text": "Pluto in the 8th House is in its home environment, bringing intense psychological power, rebirth, and transformation to shared resources, inheritance, and intimacy. These individuals seek deep, tabooless emotional bonds and possess powerful psychic intuition. The shadow side involves intense power struggles, control, and secrets.",
        "tags": ["pluto", "8th_house", "intimacy", "power", "transformation"]
    },
    
    # --- Astrological Advice / Themes (astro_110 to astro_120) ---
    {
        "id": "astro_110",
        "category": "career",
        "topic": "Saturn and Vocational Path",
        "text": "Saturn indicates where you must face fear, establish structure, and build competence over time. In career context, the house Saturn occupies shows where you must apply discipline to succeed. For example, Saturn in the 3rd house requires disciplined writing or communication, while Saturn in the 6th house requires daily health and work routine structure.",
        "tags": ["career", "saturn", "discipline", "work"]
    },
    {
        "id": "astro_111",
        "category": "relationships",
        "topic": "7th House Ruler",
        "text": "The ruler of the 7th house (Descendant) indicates the qualities and environments through which partnerships manifest in your life. If the ruler of the 7th house is in the 10th house, partnerships may connect to your career. If in the 9th house, you may attract foreign or highly philosophical partners, seeking shared expansion.",
        "tags": ["relationships", "7th_house", "ruler", "partnership"]
    },
    {
        "id": "astro_112",
        "category": "transits",
        "topic": "Uranus Transits",
        "text": "Uranus transits bring sudden change, breakthroughs, and a strong urge for liberation. When transiting Uranus aspects a natal planet, it disrupts current patterns, demanding freedom and innovation. For example, Uranus transiting the 2nd house can bring sudden changes in finances, while Uranus transiting the 1st house triggers an identity revolution.",
        "tags": ["uranus", "transits", "change", "freedom"]
    },
    {
        "id": "astro_113",
        "category": "transits",
        "topic": "Neptune Transits",
        "text": "Neptune transits bring spiritualization, dissolving boundaries, and confusion. When transiting Neptune aspects a natal planet, it softens rigid habits, allowing dreams and artistic inspiration to flow, but also triggering confusion or escapism. It tests our capacity for trust, surrender, and spiritual clarity.",
        "tags": ["neptune", "transits", "dreams", "spirituality"]
    },
    {
        "id": "astro_114",
        "category": "transits",
        "topic": "Pluto Transits",
        "text": "Pluto transits bring deep psychological purification, power issues, and rebirth. Operating slowly over several years, transiting Pluto requires us to purge obsolete patterns and reclaim personal power. It destroys what is weak, leading to profound empowerment and inner renewal.",
        "tags": ["pluto", "transits", "transformation", "power"]
    }
]

# Path to the data file
data_file_path = os.path.join("backend", "data", "astrology_knowledge.jsonl")

# Read existing entries to avoid duplication
existing_ids = set()
if os.path.exists(data_file_path):
    with open(data_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line.strip())
                    existing_ids.add(entry["id"])
                except Exception:
                    pass

# Filter new entries
entries_to_append = [e for e in new_entries if e["id"] not in existing_ids]

if entries_to_append:
    print(f"Appending {len(entries_to_append)} new entries to {data_file_path}...")
    with open(data_file_path, "a", encoding="utf-8") as f:
        for entry in entries_to_append:
            f.write(json.dumps(entry) + "\n")
    print("Done!")
else:
    print("All entries already exist in the file.")
