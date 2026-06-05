import json
import os

new_entries = [
    # --- Sun in Houses (astro_115 to astro_124) ---
    {
        "id": "astro_115",
        "category": "placements",
        "topic": "Sun in the 2nd House",
        "text": "The Sun in the 2nd House focuses the core identity and ego on material resources, financial security, and values. These individuals seek self-worth and recognition through building financial stability and physical comfort. The shadow side involves materialism, defining self-value by possessions, and possessiveness.",
        "tags": ["sun", "2nd_house", "values", "money"]
    },
    {
        "id": "astro_116",
        "category": "placements",
        "topic": "Sun in the 3rd House",
        "text": "The Sun in the 3rd House focuses vitality on daily communication, writing, local environments, and mental curiosity. These individuals are active thinkers, enjoy learning, and shine when sharing information with peers. The shadow side can involve mental restlessness, gossiping, and intellectual arrogance.",
        "tags": ["sun", "3rd_house", "communication", "mind"]
    },
    {
        "id": "astro_117",
        "category": "placements",
        "topic": "Sun in the 4th House",
        "text": "The Sun in the 4th House focuses the core ego on the private life, home sanctuary, family heritage, and emotional foundations. They shine within the family structure and value domestic privacy. The shadow side involves difficulty leaving the past, family drama, and neglecting public or career ambitions.",
        "tags": ["sun", "4th_house", "home", "family", "privacy"]
    },
    {
        "id": "astro_118",
        "category": "placements",
        "topic": "Sun in the 5th House",
        "text": "The Sun in the 5th House is in its natural joy, indicating a creative, playful, and expressive nature. These individuals shine in the arts, romance, hobbies, and playing with children. The shadow side involves attention-seeking behavior, dramatic reactions, arrogance, and risky speculative investments.",
        "tags": ["sun", "5th_house", "creativity", "romance", "joy"]
    },
    {
        "id": "astro_119",
        "category": "placements",
        "topic": "Sun in the 6th House",
        "text": "The Sun in the 6th House focuses vitality on daily routines, work service, physical health, and organizing details. These individuals shine by being useful and refining processes. The shadow side involves perfectionism, becoming a slave to routine, workaholism, and health anxiety.",
        "tags": ["sun", "6th_house", "health", "work", "service"]
    },
    {
        "id": "astro_120",
        "category": "placements",
        "topic": "Sun in the 7th House",
        "text": "The Sun in the 7th House focuses identity on partnerships, contracts, marriage, and cooperation. These individuals shine in one-on-one relationships and are highly diplomatic. The shadow side involves codependency, people-pleasing, and projecting their personal power onto others.",
        "tags": ["sun", "7th_house", "relationships", "marriage"]
    },
    {
        "id": "astro_121",
        "category": "placements",
        "topic": "Sun in the 8th House",
        "text": "The Sun in the 8th House focuses the core ego on transformation, deep psychology, intimacy, and shared assets. These individuals are attracted to life's mysteries and research. The shadow side involves power struggles, secrecy, difficulty with trust, and intense psychological crises.",
        "tags": ["sun", "8th_house", "transformation", "intimacy"]
    },
    {
        "id": "astro_122",
        "category": "placements",
        "topic": "Sun in the 9th House",
        "text": "The Sun in the 9th House focuses vitality on travel, philosophy, higher education, and global worldviews. They shine when expanding their horizons and teaching others. The shadow side involves dogmatic beliefs, self-righteous lecturing, and neglecting local, daily details.",
        "tags": ["sun", "9th_house", "philosophy", "travel", "wisdom"]
    },
    {
        "id": "astro_123",
        "category": "placements",
        "topic": "Sun in the 11th House",
        "text": "The Sun in the 11th House focuses the ego on friendships, social networks, groups, and humanitarian ideals. They shine when collaborating with others for collective reform. The shadow side involves neglecting personal relationships, needing group approval, and rebellion.",
        "tags": ["sun", "11th_house", "friends", "groups", "ideals"]
    },
    {
        "id": "astro_124",
        "category": "placements",
        "topic": "Sun in the 12th House",
        "text": "The Sun in the 12th House is a highly introverted placement, focusing identity on the subconscious, dreams, and spiritual retreat. They shine behind the scenes and have high empathy. The shadow side involves escapism, lack of ego boundaries, isolation, and feeling like a victim.",
        "tags": ["sun", "12th_house", "subconscious", "spirituality"]
    },
    
    # --- Moon in Houses (astro_125 to astro_134) ---
    {
        "id": "astro_125",
        "category": "placements",
        "topic": "Moon in the 1st House",
        "text": "Moon in the 1st House represents individuals who wear their hearts on their sleeves, projecting their emotional states directly. They are highly sensitive, intuitive, and react to environments immediately. The shadow side involves moodiness, taking things too personally, and emotional instability.",
        "tags": ["moon", "1st_house", "emotions", "sensitivity"]
    },
    {
        "id": "astro_126",
        "category": "placements",
        "topic": "Moon in the 2nd House",
        "text": "Moon in the 2nd House indicates that emotional security is closely linked to financial security and material comfort. Financial situations may fluctuate with emotional states. The shadow side involves overspending when upset, material hoarding, and fear of resource scarcity.",
        "tags": ["moon", "2nd_house", "money", "security", "values"]
    },
    {
        "id": "astro_127",
        "category": "placements",
        "topic": "Moon in the 3rd House",
        "text": "Moon in the 3rd House indicates an intuitive, receptive mind that processes daily communications through emotional filters. They communicate with empathy and are close to siblings. The shadow side involves changing minds frequently, gossiping, and nervous mental tension.",
        "tags": ["moon", "3rd_house", "communication", "mind"]
    },
    {
        "id": "astro_128",
        "category": "placements",
        "topic": "Moon in the 5th House",
        "text": "Moon in the 5th House brings emotional warmth, playfulness, and creativity to romantic pursuits, hobbies, and children. They express moods creatively and enjoy drama. The shadow side involves emotional attention-seeking, instability in romance, and dramatic tantrums.",
        "tags": ["moon", "5th_house", "romance", "creativity"]
    },
    {
        "id": "astro_129",
        "category": "placements",
        "topic": "Moon in the 6th House",
        "text": "Moon in the 6th House indicates that emotional security is found through daily routine organization, service, work, and physical wellness. Emotional states strongly affect their digestive health. The shadow side involves workaholism, criticism, and excessive worry about health.",
        "tags": ["moon", "6th_house", "health", "work", "routine"]
    },
    {
        "id": "astro_130",
        "category": "placements",
        "topic": "Moon in the 7th House",
        "text": "Moon in the 7th House indicates a strong emotional need for committed partnerships and marriage. They seek partners who nurture them and absorb their moods. The shadow side involves codependency, people-pleasing, and attracting emotionally unstable or clingy partners.",
        "tags": ["moon", "7th_house", "relationships", "marriage"]
    },
    {
        "id": "astro_131",
        "category": "placements",
        "topic": "Moon in the 8th House",
        "text": "Moon in the 8th House indicates deep emotional intensity, powerful psychological intuition, and a need for intimate, transformative bonds. They absorb hidden family dynamics. The shadow side involves jealousy, emotional control issues, keeping secrets, and fear of betrayal.",
        "tags": ["moon", "8th_house", "intimacy", "transformation"]
    },
    {
        "id": "astro_132",
        "category": "placements",
        "topic": "Moon in the 9th House",
        "text": "Moon in the 9th House indicates that emotional security is found in travel, philosophy, higher studies, and seeking truth. They have a natural faith in the universe. The shadow side involves escaping emotional issues through travel, restlessness, and ignoring domestic needs.",
        "tags": ["moon", "9th_house", "travel", "philosophy"]
    },
    {
        "id": "astro_133",
        "category": "placements",
        "topic": "Moon in the 10th House",
        "text": "Moon in the 10th House indicates that emotional needs are tied to career status, public recognition, and authority. They are natural nurturers in their professional life. The shadow side involves fear of public rejection, workaholism, and bringing domestic moods into the workplace.",
        "tags": ["moon", "10th_house", "career", "status"]
    },
    {
        "id": "astro_134",
        "category": "placements",
        "topic": "Moon in the 11th House",
        "text": "Moon in the 11th House indicates that emotional security is found in friendships, social network collaborations, and humanitarian projects. They are supportive group members. The shadow side involves emotional detachment in friendships and a need for constant peer approval.",
        "tags": ["moon", "11th_house", "friends", "groups"]
    },

    # --- Mercury, Venus, Mars in Houses (astro_135 to astro_162) ---
    {
        "id": "astro_135",
        "category": "placements",
        "topic": "Mercury in the 2nd House",
        "text": "Mercury in the 2nd House indicates a practical mind focused on financial organization, budget planning, and resource development. They are clever in business matters. The shadow side involves worrying too much about money and analyzing every minor expense.",
        "tags": ["mercury", "2nd_house", "money", "mind"]
    },
    {
        "id": "astro_136",
        "category": "placements",
        "topic": "Mercury in the 4th House",
        "text": "Mercury in the 4th House indicates that intellectual activity and communication are focused on family affairs, home life, and childhood history. The home is a place of study. The shadow side involves family arguments, restlessness, and excessive worrying about domestic safety.",
        "tags": ["mercury", "4th_house", "home", "family"]
    },
    {
        "id": "astro_137",
        "category": "placements",
        "topic": "Mercury in the 5th House",
        "text": "Mercury in the 5th House brings mental creativity, cleverness, and wit to self-expression, hobbies, romance, and play. They speak with dramatic flair. The shadow side involves intellectual pride, bragging, and using communication to manipulate romantic partners.",
        "tags": ["mercury", "5th_house", "creativity", "wit"]
    },
    {
        "id": "astro_138",
        "category": "placements",
        "topic": "Mercury in the 6th House",
        "text": "Mercury in the 6th House is in its natural home, indicating an analytical mind focused on work scheduling, daily tasks, health, and services. They organize schedules efficiently. The shadow side involves nervous worry, perfectionism, and health hypochondria.",
        "tags": ["mercury", "6th_house", "work", "health"]
    },
    {
        "id": "astro_139",
        "category": "placements",
        "topic": "Mercury in the 7th House",
        "text": "Mercury in the 7th House indicates a mind focused on partnership communication, contracts, and negotiation. They seek intellectual compatibility in partnerships. The shadow side involves arguments in relationships, people-pleasing talk, and indecision.",
        "tags": ["mercury", "7th_house", "relationships", "negotiation"]
    },
    {
        "id": "astro_140",
        "category": "placements",
        "topic": "Mercury in the 8th House",
        "text": "Mercury in the 8th House represents a deep, penetrating intellect interested in research, psychology, mysteries, and shared finances. They are natural investigators. The shadow side involves paranoia, obsessive thoughts, keeping dark secrets, and cynicism.",
        "tags": ["mercury", "8th_house", "psychology", "research"]
    },
    {
        "id": "astro_141",
        "category": "placements",
        "topic": "Mercury in the 10th House",
        "text": "Mercury in the 10th House indicates that communication, writing, and teaching are central to career ambitions and public status. They present a professional, logical persona. The shadow side involves career anxiety, gossip, and using logic to manipulate public image.",
        "tags": ["mercury", "10th_house", "career", "public"]
    },
    {
        "id": "astro_142",
        "category": "placements",
        "topic": "Mercury in the 11th House",
        "text": "Mercury in the 11th House indicates a mind focused on social networking, group discussions, and humanitarian goals. They communicate with diverse friends. The shadow side involves scattered focus in groups and intellectual debate for its own sake.",
        "tags": ["mercury", "11th_house", "friends", "groups"]
    },
    {
        "id": "astro_143",
        "category": "placements",
        "topic": "Mercury in the 12th House",
        "text": "Mercury in the 12th House suggests a quiet, highly intuitive, and imaginative mind that processes thoughts through symbols, dreams, and art. They keep thoughts private. The shadow side involves mental confusion, difficulty speaking clearly, and self-deception.",
        "tags": ["mercury", "12th_house", "subconscious", "dreams"]
    },
    {
        "id": "astro_144",
        "category": "placements",
        "topic": "Venus in the 1st House",
        "text": "Venus in the 1st House projects a charming, attractive, and diplomatic physical persona. These individuals value aesthetics and seek peace and beauty in their environment. The shadow side involves vanity, people-pleasing, and superficial concern with physical appearance.",
        "tags": ["venus", "1st_house", "charm", "appearance"]
    },
    {
        "id": "astro_145",
        "category": "placements",
        "topic": "Venus in the 3rd House",
        "text": "Venus in the 3rd House indicates a love of writing, literature, and diplomatic daily communication. They speak with kindness and have happy ties with siblings. The shadow side involves superficial talk, using flattery to get their way, and mental laziness.",
        "tags": ["venus", "3rd_house", "communication", "diplomacy"]
    },
    {
        "id": "astro_146",
        "category": "placements",
        "topic": "Venus in the 4th House",
        "text": "Venus in the 4th House indicates a love of home aesthetics, family comfort, and domestic peace. They enjoy decorating their sanctuary and entertaining guests. The shadow side involves avoiding family confrontations and overspending on household luxury.",
        "tags": ["venus", "4th_house", "home", "family"]
    },
    {
        "id": "astro_147",
        "category": "placements",
        "topic": "Venus in the 6th House",
        "text": "Venus in the 6th House brings harmony and pleasure to daily work routines, service, health habits, and pet interactions. They value cooperative work settings. The shadow side involves over-indulgence in sweet foods and lazy physical routines.",
        "tags": ["venus", "6th_house", "work", "routine"]
    },
    {
        "id": "astro_148",
        "category": "placements",
        "topic": "Venus in the 8th House",
        "text": "Venus in the 8th House indicates a desire for deep emotional transformation, intense intimacy, and financial harmony in shared resources. They may gain from inheritances. The shadow side involves jealousy, manipulation in love, and financial codependency.",
        "tags": ["venus", "8th_house", "intimacy", "money"]
    },
    {
        "id": "astro_149",
        "category": "placements",
        "topic": "Venus in the 9th House",
        "text": "Venus in the 9th House represents a love for travel, foreign cultures, philosophy, and higher wisdom. They are attracted to partners from different backgrounds. The shadow side involves romantic restlessness and neglecting commitments for adventure.",
        "tags": ["venus", "9th_house", "travel", "philosophy"]
    },
    {
        "id": "astro_150",
        "category": "placements",
        "topic": "Venus in the 10th House",
        "text": "Venus in the 10th House indicates that charm, relationships, and aesthetics are central to career ambitions and public status. They have a popular public image. The shadow side involves using relationships for career advancement and vanity regarding public success.",
        "tags": ["venus", "10th_house", "career", "reputation"]
    },
    {
        "id": "astro_151",
        "category": "placements",
        "topic": "Venus in the 11th House",
        "text": "Venus in the 11th House indicates a love for friendships, social networks, and collaborative humanitarian group activities. They attract artistic, loving friends. The shadow side involves superficial group ties and difficulty separating friendship from romance.",
        "tags": ["venus", "11th_house", "friends", "groups"]
    },
    {
        "id": "astro_152",
        "category": "placements",
        "topic": "Venus in the 12th House",
        "text": "Venus in the 12th House suggests a private, deeply compassionate, and spiritual approach to love and relationships. They seek soul-level unions and keep romances hidden. The shadow side involves secret love affairs, codependency, and adopting a martyr role in love.",
        "tags": ["venus", "12th_house", "love", "spirituality"]
    },
    {
        "id": "astro_153",
        "category": "placements",
        "topic": "Mars in the 2nd House",
        "text": "Mars in the 2nd House indicates high physical energy and drive spent on making money and acquiring resources. They are ambitious in business. The shadow side involves financial impulsiveness, overspending, and arguments regarding personal property and values.",
        "tags": ["mars", "2nd_house", "money", "drive"]
    },
    {
        "id": "astro_154",
        "category": "placements",
        "topic": "Mars in the 3rd House",
        "text": "Mars in the 3rd House indicates an energetic, assertive communication style and a busy mental state. They write and speak with force, defending opinions. The shadow side involves verbal impatience, arguments with siblings/neighbors, and car accidents due to fast driving.",
        "tags": ["mars", "3rd_house", "communication", "mind"]
    },
    {
        "id": "astro_155",
        "category": "placements",
        "topic": "Mars in the 4th House",
        "text": "Mars in the 4th House indicates that physical energy and drive are directed into home renovations, family activities, or domestic leadership. The shadow side involves family arguments, domestic tension, and unresolved childhood anger.",
        "tags": ["mars", "4th_house", "home", "family"]
    },
    {
        "id": "astro_156",
        "category": "placements",
        "topic": "Mars in the 5th House",
        "text": "Mars in the 5th House indicates high passion, drive, and competition in romantic pursuits, creative hobbies, play, and athletics. They express desires playfully. The shadow side involves romantic conflicts, risk-taking, and impatience with children.",
        "tags": ["mars", "5th_house", "romance", "creativity"]
    },
    {
        "id": "astro_157",
        "category": "placements",
        "topic": "Mars in the 6th House",
        "text": "Mars in the 6th House indicates that physical energy is focused on daily work, service tasks, and physical health training. They work hard and fast. The shadow side involves conflicts with coworkers, physical stress, health inflammation, and over-working.",
        "tags": ["mars", "6th_house", "work", "health"]
    },
    {
        "id": "astro_158",
        "category": "placements",
        "topic": "Mars in the 7th House",
        "text": "Mars in the 7th House projects energy and assertiveness onto partnerships, seeking active, competitive, or independent partners. The shadow side involves intense relationship conflicts, competition with partners, and attracting aggressive people.",
        "tags": ["mars", "7th_house", "relationships", "conflict"]
    },
    {
        "id": "astro_159",
        "category": "placements",
        "topic": "Mars in the 8th House",
        "text": "Mars in the 8th House indicates intense desire and drive for intimacy, transformation, and shared financial resources. They handle financial negotiations with power. The shadow side involves power struggles over money, inheritance disputes, and intense emotional secrets.",
        "tags": ["mars", "8th_house", "intimacy", "power"]
    },
    {
        "id": "astro_160",
        "category": "placements",
        "topic": "Mars in the 9th House",
        "text": "Mars in the 9th House indicates high energy and passion directed into higher studies, philosophical exploration, travel, and defending worldviews. The shadow side involves self-righteous fanatical beliefs, arguing over philosophy, and travel dangers due to haste.",
        "tags": ["mars", "9th_house", "philosophy", "travel"]
    },
    {
        "id": "astro_161",
        "category": "placements",
        "topic": "Mars in the 11th House",
        "text": "Mars in the 11th House indicates that drive and leadership are directed into friendships, group networks, and humanitarian projects. They motivate group action. The shadow side involves arguments within groups, competition with friends, and scattered social circles.",
        "tags": ["mars", "11th_house", "friends", "groups"]
    },
    {
        "id": "astro_162",
        "category": "placements",
        "topic": "Mars in the 12th House",
        "text": "Mars in the 12th House indicates that energy and desires are processed in the subconscious, often working behind the scenes or in isolation. They have high spiritual energy. The shadow side involves hidden anger, self-sabotaging habits, and feeling powerless.",
        "tags": ["mars", "12th_house", "subconscious", "secrecy"]
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
