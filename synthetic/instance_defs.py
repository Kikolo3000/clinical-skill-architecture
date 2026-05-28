#!/usr/bin/env python3
"""
Synthetic test suite instance definitions.

150 instances total:
  - 54 Pure single-subscale (HOP=8, SAC=10, PMR=6, SOM=6, DAM=8, SEP=6, HOS=10)
  - 25 Multi-subscale
  - 15 Multi-code
  - 15 Distractor-heavy
  - 10 Denial-focused
  - 31 True-negative

Each instance dict:
  id: str              - SYN_{NNN}_{TYPE}_{DIFF}_{SUBSCALE}
  type: str            - PURE|MULTI|MCODE|DIST|DENY|NEG
  difficulty: str      - EASY|MOD|HARD|ADV
  primary_subscale: str
  n_distractors: int   - count of distractor (non-codable) clauses
  turns: list[dict]    - {speaker: "I"|"S", text: str}
  ground_truth: list   - [{fragment: int, codings: [...], rationale: str}]
                         fragment is 1-based index into S: turns

Coding dict:
  clause, subscale, sub_item, perspective, weight, rationale
"""


def _c(clause, subscale, sub_item, perspective, weight, rationale=""):
    """Shorthand for coding dict."""
    return {
        "clause": clause,
        "subscale": subscale,
        "sub_item": sub_item,
        "perspective": perspective,
        "weight": weight,
        "rationale": rationale,
    }


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — HOP (8 instances)
# ===================================================================

PURE_HOP = [
    # SYN_001: Easy — prototypical hopelessness, self
    {
        "id": "SYN_001_PURE_EASY_HOP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how have you been feeling about the future"},
            {"speaker": "S", "text": "i just don't see the point anymore honestly nothing is going to change no matter what i do i've been going to work every day though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Two clear HOP.3b clauses (hopelessness attributed to self), one neutral distractor.",
            "codings": [
                _c("i just don't see the point anymore", "HOP", "HOP.3b", "self", 1,
                   "Direct expression of futility/hopelessness attributed to self"),
                _c("nothing is going to change no matter what i do", "HOP", "HOP.3b", "self", 1,
                   "Pessimism about future despite effort — classic hopelessness"),
            ],
        }],
    },
    # SYN_002: Easy — hopelessness about support from others
    {
        "id": "SYN_002_PURE_EASY_HOP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you feel like you have people you can rely on"},
            {"speaker": "S", "text": "no not really i feel like nobody cares about me nobody ever helps when i need it i still talk to my sister sometimes though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Two HOP.2a clauses — not receiving support/esteem from others. Distractor: neutral mention of sister.",
            "codings": [
                _c("i feel like nobody cares about me", "HOP", "HOP.2a", "self", 1,
                   "Not receiving esteem/care from others"),
                _c("nobody ever helps when i need it", "HOP", "HOP.2a", "self", 1,
                   "Not receiving help/support from others"),
            ],
        }],
    },
    # SYN_003: Easy — lack of motivation/interest
    {
        "id": "SYN_003_PURE_EASY_HOP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what kinds of things do you enjoy doing"},
            {"speaker": "S", "text": "i used to like painting but i've completely lost all motivation i just don't care about anything anymore the weather has been nice lately i guess"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.3b (loss of motivation/interest). Distractors: past hobby mention, weather.",
            "codings": [
                _c("i've completely lost all motivation", "HOP", "HOP.3b", "self", 1,
                   "Lack of ambition/interest attributed to self"),
                _c("i just don't care about anything anymore", "HOP", "HOP.3b", "self", 1,
                   "Loss of interest — hopelessness"),
            ],
        }],
    },
    # SYN_004: Easy — bad luck, inanimate perspective
    {
        "id": "SYN_004_PURE_EASY_HOP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how would you describe your luck in life"},
            {"speaker": "S", "text": "i guess i'm just unlucky nothing good ever happens to me like things just never go my way i do have a decent apartment at least"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.1 (not recipient of good fortune) + HOP.3b (pessimism). Distractor: apartment.",
            "codings": [
                _c("i guess i'm just unlucky", "HOP", "HOP.1", "inanimate", 1,
                   "Not being recipient of good fortune/luck"),
                _c("nothing good ever happens to me", "HOP", "HOP.1", "inanimate", 1,
                   "Not receiving good fortune"),
                _c("things just never go my way", "HOP", "HOP.3b", "self", 1,
                   "Pessimism/discouragement attributed to self"),
            ],
        }],
    },
    # SYN_005: Moderate — hopelessness about others + self
    {
        "id": "SYN_005_PURE_MOD_HOP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "tell me about your family"},
            {"speaker": "S", "text": "well my sister she um she says she has nothing to look forward to and honestly i kind of feel the same way like why bother trying it never works out we used to go fishing together when we were kids that was okay"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.3a (others' hopelessness) + HOP.3b (self hopelessness). Distractors: fishing memory.",
            "codings": [
                _c("she says she has nothing to look forward to", "HOP", "HOP.3a", "others", 1,
                   "Hopelessness/despair attributed to another person"),
                _c("why bother trying", "HOP", "HOP.3b", "self", 1,
                   "Discouragement/pessimism attributed to self"),
                _c("it never works out", "HOP", "HOP.3b", "self", 1,
                   "Pessimism about outcomes"),
            ],
        }],
    },
    # SYN_006: Moderate — can't help self + SEP-like distractor
    {
        "id": "SYN_006_PURE_MOD_HOP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "when things get difficult how do you cope"},
            {"speaker": "S", "text": "um i can't even help myself at this point you know i just feel like there's no way out my friend moved to another state last year but that's just life i suppose"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.2b (can't help self) + HOP.3b (no way out). Distractors: friend moving (SEP-adjacent but factual).",
            "codings": [
                _c("i can't even help myself at this point", "HOP", "HOP.2b", "self", 1,
                   "Not getting support/confidence from self"),
                _c("i just feel like there's no way out", "HOP", "HOP.3b", "self", 1,
                   "Hopelessness/despair — feeling trapped"),
            ],
        }],
    },
    # SYN_007: Moderate — others not getting help
    {
        "id": "SYN_007_PURE_MOD_HOP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "is there anything that's been on your mind lately"},
            {"speaker": "S", "text": "yeah um my brother he's been struggling and nobody is helping him out at all his friends just don't care i try to check in on him though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.2a (others not getting help from others). Distractor: speaker checking in.",
            "codings": [
                _c("nobody is helping him out at all", "HOP", "HOP.2a", "others", 1,
                   "Others not receiving help/support"),
                _c("his friends just don't care", "HOP", "HOP.2a", "others", 1,
                   "Others not receiving esteem/care from others"),
            ],
        }],
    },
    # SYN_008: Hard — hedged hopelessness with PMR-like distractor
    {
        "id": "SYN_008_PURE_HARD_HOP",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how do you see things going for you in the next year"},
            {"speaker": "S", "text": "i mean i don't know it's like maybe things could change but deep down i really doubt it i guess i've sort of given up expecting anything good i've been kind of slow getting stuff done but that's just because of the commute"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Hedged HOP.3b clauses. Distractors: slowness (PMR-adjacent but attributed to commute), commute.",
            "codings": [
                _c("deep down i really doubt it", "HOP", "HOP.3b", "self", 1,
                   "Pessimism despite hedging — core hopelessness"),
                _c("i've sort of given up expecting anything good", "HOP", "HOP.1", "inanimate", 1,
                   "Not seeking/expecting good fortune"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — SAC (10 instances)
# ===================================================================

PURE_SAC = [
    # SYN_009: Easy — guilt, self
    {
        "id": "SYN_009_PURE_EASY_SAC",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "is there anything you feel bad about"},
            {"speaker": "S", "text": "yeah it's all my fault that the marriage fell apart i feel so guilty about it we had a nice house though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.a (guilt/self-condemnation, self). Distractor: house.",
            "codings": [
                _c("it's all my fault that the marriage fell apart", "SAC", "SAC.A.a", "self", 3,
                   "Self-condemnation, guilt attributed to self"),
                _c("i feel so guilty about it", "SAC", "SAC.A.a", "self", 3,
                   "Direct expression of guilt attributed to self"),
            ],
        }],
    },
    # SYN_010: Easy — shame, self
    {
        "id": "SYN_010_PURE_EASY_SAC",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "can you tell me about a time you felt embarrassed"},
            {"speaker": "S", "text": "oh god i feel so ashamed of how i acted at that party i made a complete fool of myself the food was pretty good at least"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.B.a (shame/embarrassment, self). Distractor: food.",
            "codings": [
                _c("i feel so ashamed of how i acted at that party", "SAC", "SAC.B.a", "self", 3,
                   "Shame/embarrassment attributed to self"),
                _c("i made a complete fool of myself", "SAC", "SAC.B.a", "self", 3,
                   "Overexposure of deficiencies, humiliation — self"),
            ],
        }],
    },
    # SYN_011: Easy — self-blame, worthlessness (SAC.C.b2)
    {
        "id": "SYN_011_PURE_EASY_SAC",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you feel about yourself these days"},
            {"speaker": "S", "text": "i'm such an idiot i can never do anything right i'm completely worthless i still go to the gym on tuesdays"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b2 (self-blame, worthlessness). Distractor: gym.",
            "codings": [
                _c("i'm such an idiot", "SAC", "SAC.C.b2", "self", 3,
                   "Self-blame, considering self worthless"),
                _c("i can never do anything right", "SAC", "SAC.C.b2", "self", 3,
                   "Expressing anger/hatred toward self"),
                _c("i'm completely worthless", "SAC", "SAC.C.b2", "self", 3,
                   "Considering self of no value"),
            ],
        }],
    },
    # SYN_012: Easy — guilt about others (SAC.A.b)
    {
        "id": "SYN_012_PURE_EASY_SAC",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you noticed other people going through difficult times"},
            {"speaker": "S", "text": "yeah my coworker got in big trouble for something he didn't even do they were condemning him for no reason everyone else just watched the office is downtown"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.b (adverse criticism/condemnation of others). Distractor: office location.",
            "codings": [
                _c("my coworker got in big trouble for something he didn't even do", "SAC", "SAC.A.b", "others", 2,
                   "Adverse criticism experienced by another person"),
                _c("they were condemning him for no reason", "SAC", "SAC.A.b", "others", 2,
                   "Condemnation/moral disapproval experienced by others"),
            ],
        }],
    },
    # SYN_013: Moderate — self-criticism, regret (SAC.C.b3)
    {
        "id": "SYN_013_PURE_MOD_SAC",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SAC",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "is there anything you wish you had done differently"},
            {"speaker": "S", "text": "oh yeah i keep making the same stupid mistakes you know i really regret not finishing school i'm so sorry for how i treated people back then um i drive a honda civic"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b3 (self-criticism, regret). Distractors: car, school mention as factual.",
            "codings": [
                _c("i keep making the same stupid mistakes", "SAC", "SAC.C.b3", "self", 2,
                   "Self-criticism, references to self as in error"),
                _c("i really regret not finishing school", "SAC", "SAC.C.b3", "self", 2,
                   "Regretting past actions"),
                _c("i'm so sorry for how i treated people back then", "SAC", "SAC.C.b3", "self", 2,
                   "Being sorry/ashamed for what one did"),
            ],
        }],
    },
    # SYN_014: Moderate — shame about others (SAC.B.b)
    {
        "id": "SYN_014_PURE_MOD_SAC",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you seen anyone close to you struggling"},
            {"speaker": "S", "text": "my friend was really humiliated at work in front of everyone she said she felt so inadequate like she couldn't measure up she takes the bus home usually"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.B.b (shame/humiliation experienced by others). Distractor: bus.",
            "codings": [
                _c("my friend was really humiliated at work in front of everyone", "SAC", "SAC.B.b", "others", 2,
                   "Humiliation/shame experienced by another person"),
                _c("she felt so inadequate", "SAC", "SAC.B.b", "others", 2,
                   "Inadequacy experienced by another person"),
            ],
        }],
    },
    # SYN_015: Moderate — deserving punishment (SAC.C.a3)
    {
        "id": "SYN_015_PURE_MOD_SAC",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you ever feel like things are unfair"},
            {"speaker": "S", "text": "no actually i deserve everything bad that happens to me i should be punished for what i've done i need to pay for my mistakes we live in a two bedroom place"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.a3 (needing/deserving punishment). Distractor: apartment.",
            "codings": [
                _c("i deserve everything bad that happens to me", "SAC", "SAC.C.a3", "self", 2,
                   "Needing/deserving punishment"),
                _c("i should be punished for what i've done", "SAC", "SAC.C.a3", "self", 2,
                   "Needing to atone/do penance"),
                _c("i need to pay for my mistakes", "SAC", "SAC.C.a3", "self", 2,
                   "Paying for one's sins"),
            ],
        }],
    },
    # SYN_016: Hard — unable to meet expectations (SAC.C.a4) + driven by standards (SAC.C.c2)
    {
        "id": "SYN_016_PURE_HARD_SAC",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "SAC",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "tell me about the pressures in your life"},
            {"speaker": "S", "text": "i feel like i have to be perfect all the time or everything falls apart i can never live up to what they expect of me i'm always disappointed in myself um i work in accounting the hours aren't too bad"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.c2 + SAC.C.a4 + SAC.C.a4. Distractors: job, hours.",
            "codings": [
                _c("i feel like i have to be perfect all the time or everything falls apart", "SAC", "SAC.C.c2", "self", 1,
                   "Feeling painfully driven to meet own standards"),
                _c("i can never live up to what they expect of me", "SAC", "SAC.C.a4", "self", 1,
                   "Unable to meet expectations of others"),
                _c("i'm always disappointed in myself", "SAC", "SAC.C.a4", "self", 1,
                   "Feeling disappointed in self"),
            ],
        }],
    },
    # SYN_017: Hard — deprivation/lonesomeness (SAC.C.c) + guilt
    {
        "id": "SYN_017_PURE_HARD_SAC",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been the hardest part of this year for you"},
            {"speaker": "S", "text": "just this overwhelming sense of deprivation like i'm missing out on everything and it's so lonely and i know it's my own fault for pushing people away the apartment complex has a pool which is nice"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.c (deprivation/lonesomeness) + SAC.A.a (guilt/self-blame). Distractor: pool.",
            "codings": [
                _c("overwhelming sense of deprivation like i'm missing out on everything", "SAC", "SAC.C.c", "self", 2,
                   "Feelings of deprivation"),
                _c("it's so lonely", "SAC", "SAC.C.c", "self", 2,
                   "Feelings of lonesomeness"),
                _c("it's my own fault for pushing people away", "SAC", "SAC.A.a", "self", 3,
                   "Self-condemnation, guilt attributed to self"),
            ],
        }],
    },
    # SYN_018: Adversarial — suicidal content (SAC.C.a + SAC.C.b) with HOS-like distractor
    {
        "id": "SYN_018_PURE_ADV_SAC",
        "type": "PURE", "difficulty": "ADV", "primary_subscale": "SAC",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "have you ever had thoughts of harming yourself"},
            {"speaker": "S", "text": "yeah sometimes i think everyone would be better off without me i've thought about ending it all i even um i cut myself once last year people at work really annoy me but that's not the same thing i mean i don't want to hurt them"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b (wanting to die, w4) + SAC.C.a (self-harm, w4) + SAC.C.a2 (cutting, w3). Distractors: work annoyance (HOS-adjacent but vague), not wanting to hurt them.",
            "codings": [
                _c("sometimes i think everyone would be better off without me", "SAC", "SAC.C.b", "self", 4,
                   "Wanting/needing to die — implicit suicidal ideation"),
                _c("i've thought about ending it all", "SAC", "SAC.C.a", "self", 4,
                   "Self threatening to kill self"),
                _c("i cut myself once last year", "SAC", "SAC.C.a2", "self", 3,
                   "Self injuring/mutilating self"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — PMR (6 instances)
# ===================================================================

PURE_PMR = [
    {
        "id": "SYN_019_PURE_EASY_PMR",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how has your energy been lately"},
            {"speaker": "S", "text": "everything just feels slow like i'm moving through mud my mind is so sluggish i had cereal for breakfast"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 (general slowing in action + thinking). Distractor: cereal.",
            "codings": [
                _c("everything just feels slow like i'm moving through mud", "PMR", "PMR.1", "self", 1,
                   "General retardation in action — psychomotor slowing"),
                _c("my mind is so sluggish", "PMR", "PMR.1", "self", 1,
                   "Slowing in thinking"),
            ],
        }],
    },
    {
        "id": "SYN_020_PURE_EASY_PMR",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's a typical morning like for you"},
            {"speaker": "S", "text": "i can barely think straight my thoughts are just stuck i can't process anything i usually wake up around seven"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 (cognitive slowing). Distractor: wake time.",
            "codings": [
                _c("i can barely think straight", "PMR", "PMR.1", "self", 1,
                   "Slowing in thinking — cognitive sluggishness"),
                _c("my thoughts are just stuck i can't process anything", "PMR", "PMR.1", "self", 1,
                   "Retardation in thinking — thoughts stuck"),
            ],
        }],
    },
    {
        "id": "SYN_021_PURE_MOD_PMR",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "PMR",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "has anything changed about how you function day to day"},
            {"speaker": "S", "text": "it takes me forever to do the simplest things now i feel like i'm in slow motion i just feel numb like i can't feel anything anymore my neighbor has a dog that barks a lot the bus runs every fifteen minutes"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 (slowing in action + feeling). Distractors: dog, bus.",
            "codings": [
                _c("it takes me forever to do the simplest things now", "PMR", "PMR.1", "self", 1,
                   "General slowing in action"),
                _c("i feel like i'm in slow motion", "PMR", "PMR.1", "self", 1,
                   "Direct metaphor for psychomotor retardation"),
                _c("i just feel numb like i can't feel anything anymore", "PMR", "PMR.1", "self", 1,
                   "Retardation in feeling — emotional numbness"),
            ],
        }],
    },
    {
        "id": "SYN_022_PURE_MOD_PMR",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have other people noticed any changes in you"},
            {"speaker": "S", "text": "my wife says i seem like i'm wading through molasses all day she says i can't seem to get myself going and it's true i just can't i work from home three days a week"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 (others describing slowing + self confirming). Distractor: work schedule.",
            "codings": [
                _c("i seem like i'm wading through molasses all day", "PMR", "PMR.1", "self", 1,
                   "General retardation — wading through molasses metaphor"),
                _c("i can't seem to get myself going", "PMR", "PMR.1", "self", 1,
                   "Difficulty initiating action — psychomotor slowing"),
            ],
        }],
    },
    {
        "id": "SYN_023_PURE_HARD_PMR",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "PMR",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how would you describe your mental state right now"},
            {"speaker": "S", "text": "it's um it's like everything has slowed way down my brain just won't cooperate even talking feels like effort right now i had a headache yesterday but it went away and i'm not really tired just slow"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 with SOM-adjacent distractors. Hard: distinguish general slowing from specific somatic.",
            "codings": [
                _c("everything has slowed way down", "PMR", "PMR.1", "self", 1,
                   "General retardation — global slowing"),
                _c("my brain just won't cooperate", "PMR", "PMR.1", "self", 1,
                   "Cognitive retardation"),
                _c("even talking feels like effort right now", "PMR", "PMR.1", "self", 1,
                   "Slowing in action — effort to communicate"),
            ],
        }],
    },
    {
        "id": "SYN_024_PURE_ADV_PMR",
        "type": "PURE", "difficulty": "ADV", "primary_subscale": "PMR",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "can you describe what it feels like inside your head"},
            {"speaker": "S", "text": "it's like my whole system has powered down you know not like i'm tired or anything my body is fine it's just this general shutdown where thinking feeling moving it's all in slow motion i'm not sick or hurting anywhere it's more like the whole machine is running at half speed"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 with explicit denial of SOM. Adversarial: speaker distinguishes PMR from SOM.",
            "codings": [
                _c("my whole system has powered down", "PMR", "PMR.1", "self", 1,
                   "General retardation — global shutdown metaphor"),
                _c("thinking feeling moving it's all in slow motion", "PMR", "PMR.1", "self", 1,
                   "Slowing in thinking, feeling, and action"),
                _c("the whole machine is running at half speed", "PMR", "PMR.1", "self", 1,
                   "General retardation metaphor"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — SOM (6 instances)
# ===================================================================

PURE_SOM = [
    {
        "id": "SYN_025_PURE_EASY_SOM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SOM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how has your health been"},
            {"speaker": "S", "text": "not great i haven't been sleeping well for weeks and i get these terrible headaches almost every day i watch tv in the evenings"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.B (sleep) + SOM.E (headaches). Distractor: TV.",
            "codings": [
                _c("i haven't been sleeping well for weeks", "SOM", "SOM.B", "self", 1,
                   "Sleep disturbance"),
                _c("i get these terrible headaches almost every day", "SOM", "SOM.E", "self", 1,
                   "General somatic — headaches"),
            ],
        }],
    },
    {
        "id": "SYN_026_PURE_EASY_SOM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SOM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you noticed any changes in your appetite or weight"},
            {"speaker": "S", "text": "yeah i've completely lost my appetite and i've lost about fifteen pounds without trying i cook for my kids though they eat fine"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.D (appetite) + SOM.E (weight loss). Distractor: kids eating.",
            "codings": [
                _c("i've completely lost my appetite", "SOM", "SOM.D", "self", 1,
                   "Appetite disturbance"),
                _c("i've lost about fifteen pounds without trying", "SOM", "SOM.E", "self", 1,
                   "Weight loss"),
            ],
        }],
    },
    {
        "id": "SYN_027_PURE_EASY_SOM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SOM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how is your body feeling physically"},
            {"speaker": "S", "text": "i have no energy i feel exhausted all the time my back has been killing me lately i take the stairs at work when i can"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (fatigue + backache). Distractor: stairs.",
            "codings": [
                _c("i have no energy i feel exhausted all the time", "SOM", "SOM.E", "self", 1,
                   "Loss of energy, fatigability"),
                _c("my back has been killing me lately", "SOM", "SOM.E", "self", 1,
                   "General somatic — backache"),
            ],
        }],
    },
    {
        "id": "SYN_028_PURE_MOD_SOM",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SOM",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "are there any physical symptoms that have been bothering you"},
            {"speaker": "S", "text": "well my stomach has been bothering me constantly and i feel so heavy like my limbs weigh a thousand pounds my heart races sometimes too i go for walks in the park on weekends the weather's been okay"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.D (stomach) + SOM.E (heaviness) + SOM.A (heart racing). Distractors: walks, weather.",
            "codings": [
                _c("my stomach has been bothering me constantly", "SOM", "SOM.D", "self", 1,
                   "Gastrointestinal disturbance"),
                _c("i feel so heavy like my limbs weigh a thousand pounds", "SOM", "SOM.E", "self", 1,
                   "Heaviness in limbs"),
                _c("my heart races sometimes", "SOM", "SOM.A", "self", 1,
                   "Bodily malfunctioning — cardiovascular"),
            ],
        }],
    },
    {
        "id": "SYN_029_PURE_MOD_SOM",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SOM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "has anyone else in your family had health issues"},
            {"speaker": "S", "text": "my mom she told me she can't sleep and has no appetite either she gets dizzy spells too my dad is doing fine though he plays golf"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.B + SOM.D + SOM.A (all others perspective). Distractor: dad/golf.",
            "codings": [
                _c("she can't sleep", "SOM", "SOM.B", "others", 1,
                   "Sleep disturbance — others"),
                _c("has no appetite", "SOM", "SOM.D", "others", 1,
                   "Appetite disturbance — others"),
                _c("she gets dizzy spells", "SOM", "SOM.A", "others", 1,
                   "Bodily malfunctioning — others"),
            ],
        }],
    },
    {
        "id": "SYN_030_PURE_HARD_SOM",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "SOM",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how do you feel when you wake up in the morning"},
            {"speaker": "S", "text": "um my whole body aches i can barely function but it's not like a mental thing you know it's physical my muscles hurt and i have zero energy and um there are problems in the bedroom too if you know what i mean that's been an issue for a while um i just don't want to deal with traffic so i leave early i've been eating less too not on purpose"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (aches, energy) + SOM.C (sexual) + SOM.D (eating less). Hard: includes sensitive SOM.C. Distractors: traffic, leaving early.",
            "codings": [
                _c("my whole body aches", "SOM", "SOM.E", "self", 1,
                   "General somatic — muscle aches"),
                _c("my muscles hurt and i have zero energy", "SOM", "SOM.E", "self", 1,
                   "Muscle aches + loss of energy"),
                _c("there are problems in the bedroom too", "SOM", "SOM.C", "self", 1,
                   "Sexual disturbance/malfunction"),
                _c("i've been eating less too not on purpose", "SOM", "SOM.D", "self", 1,
                   "Appetite disturbance — decreased eating"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — DAM (8 instances)
# ===================================================================

PURE_DAM = [
    {
        "id": "SYN_031_PURE_EASY_DAM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you lost anyone close to you"},
            {"speaker": "S", "text": "yeah my father died of cancer last year and my dog was hit by a car and killed we still live in the same house"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b (death of others). Distractor: house.",
            "codings": [
                _c("my father died of cancer last year", "DAM", "DAM.A.b", "others", 2,
                   "Death of animate other"),
                _c("my dog was hit by a car and killed", "DAM", "DAM.A.b", "others", 2,
                   "Death of animate other — pet"),
            ],
        }],
    },
    {
        "id": "SYN_032_PURE_EASY_DAM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you had any health scares"},
            {"speaker": "S", "text": "yes i'm afraid i'm going to die from this illness i keep thinking about death all the time the hospital is about twenty minutes away"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.a (death anxiety, self). Distractor: hospital distance.",
            "codings": [
                _c("i'm afraid i'm going to die from this illness", "DAM", "DAM.A.a", "self", 3,
                   "Anxiety about own death"),
                _c("i keep thinking about death all the time", "DAM", "DAM.A.a", "self", 3,
                   "Preoccupation with death — self-referenced anxiety"),
            ],
        }],
    },
    {
        "id": "SYN_033_PURE_EASY_DAM",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you ever been in an accident"},
            {"speaker": "S", "text": "yeah i broke my arm in the accident and my friend she got badly hurt in the fire the car was completely totaled in the crash too"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.B.a (self injury) + DAM.B.b (others injury) + DAM.B.c (inanimate damage).",
            "codings": [
                _c("i broke my arm in the accident", "DAM", "DAM.B.a", "self", 3,
                   "Injury/physical damage to self"),
                _c("my friend she got badly hurt in the fire", "DAM", "DAM.B.b", "others", 2,
                   "Injury to another person"),
                _c("the car was completely totaled in the crash", "DAM", "DAM.B.c", "inanimate", 1,
                   "Physical damage to inanimate object"),
            ],
        }],
    },
    {
        "id": "SYN_034_PURE_MOD_DAM",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been on your mind recently"},
            {"speaker": "S", "text": "um a lot of people have been dying around me you know my neighbor had a terrible wound that wouldn't heal and then the building on our street was destroyed in that earthquake and the old oak tree in the park it just died too you know it was like a hundred years old i take the train to work"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b + DAM.B.b + DAM.B.c + DAM.A.c. Distractor: train.",
            "codings": [
                _c("a lot of people have been dying around me", "DAM", "DAM.A.b", "others", 2,
                   "Death of animate others"),
                _c("my neighbor had a terrible wound that wouldn't heal", "DAM", "DAM.B.b", "others", 2,
                   "Tissue damage in another person"),
                _c("the building on our street was destroyed in that earthquake", "DAM", "DAM.B.c", "inanimate", 1,
                   "Physical destruction of inanimate object"),
                _c("the old oak tree in the park it just died", "DAM", "DAM.A.c", "inanimate", 1,
                   "Death of inanimate/plant — destruction of living but non-animate entity"),
            ],
        }],
    },
    {
        "id": "SYN_035_PURE_MOD_DAM",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "DAM",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "tell me about something that's been difficult"},
            {"speaker": "S", "text": "well my grandmother she died in the hospital and before that she was in so much pain her body was just falling apart um i like watching cooking shows that helps and i've been reading more"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b (death) + DAM.B.b (pain/deterioration). Distractors: cooking shows, reading.",
            "codings": [
                _c("my grandmother she died in the hospital", "DAM", "DAM.A.b", "others", 2,
                   "Death of animate other"),
                _c("she was in so much pain", "DAM", "DAM.B.b", "others", 2,
                   "Injury/suffering in another person"),
                _c("her body was just falling apart", "DAM", "DAM.B.b", "others", 2,
                   "Physical deterioration/tissue damage — others"),
            ],
        }],
    },
    {
        "id": "SYN_036_PURE_MOD_DAM",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you worry about your own health"},
            {"speaker": "S", "text": "i sometimes worry that this pain in my chest could kill me and i got injured pretty badly playing basketball last month tore my knee up i usually play on saturdays"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.a (death anxiety) + DAM.B.a (self injury). Distractor: saturday schedule.",
            "codings": [
                _c("i sometimes worry that this pain in my chest could kill me", "DAM", "DAM.A.a", "self", 3,
                   "Anxiety about own death — threat of death"),
                _c("i got injured pretty badly playing basketball", "DAM", "DAM.B.a", "self", 3,
                   "Injury/physical damage to self"),
                _c("tore my knee up", "DAM", "DAM.B.a", "self", 3,
                   "Tissue damage to self"),
            ],
        }],
    },
    {
        "id": "SYN_037_PURE_HARD_DAM",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "DAM",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "is there anything that frightens you"},
            {"speaker": "S", "text": "i mean i feel like i'm dying sometimes you know this illness is destroying me from the inside and i've seen what it did to my uncle he wasted away it's scary um that kills me just thinking about it but anyway the traffic is terrible around here"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.a + DAM.B.a + DAM.A.b. 'that kills me' is idiomatic NOT coded. Distractors: idiom, traffic.",
            "codings": [
                _c("i feel like i'm dying sometimes", "DAM", "DAM.A.a", "self", 3,
                   "Anxiety about own death — in illness context, coded despite seeming figurative"),
                _c("this illness is destroying me from the inside", "DAM", "DAM.B.a", "self", 3,
                   "Physical damage/destruction to self"),
                _c("he wasted away", "DAM", "DAM.B.b", "others", 2,
                   "Physical deterioration — tissue damage in others"),
            ],
        }],
    },
    {
        "id": "SYN_038_PURE_ADV_DAM",
        "type": "PURE", "difficulty": "ADV", "primary_subscale": "DAM",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "can you tell me more about what scares you"},
            {"speaker": "S", "text": "well i'm dying of boredom at work ha no but seriously i am scared of actually dying from this thing i'm not afraid of death itself that doesn't bother me but the pain of it the physical breakdown that terrifies me i'm killing it on my projects though so at least there's that"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Adversarial: idioms 'dying of boredom' and 'killing it' NOT coded. DAM.A.d (denial) + DAM.A.a + DAM.B.a. Distractors: boredom idiom, killing-it idiom.",
            "codings": [
                _c("i am scared of actually dying from this thing", "DAM", "DAM.A.a", "self", 3,
                   "Genuine death anxiety — distinguished from preceding idiom"),
                _c("i'm not afraid of death itself that doesn't bother me", "DAM", "DAM.A.d", "denial", 1,
                   "Denial of death anxiety"),
                _c("the pain of it the physical breakdown that terrifies me", "DAM", "DAM.B.a", "self", 3,
                   "Anxiety about physical destruction/injury to self"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — SEP (6 instances)
# ===================================================================

PURE_SEP = [
    {
        "id": "SYN_039_PURE_EASY_SEP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about your relationships"},
            {"speaker": "S", "text": "she left me and i don't think she's coming back i feel so alone like nobody wants me around we used to go to the movies together"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (abandonment + ostracism, self). Distractor: movies.",
            "codings": [
                _c("she left me and i don't think she's coming back", "SEP", "SEP.a", "self", 3,
                   "Abandonment/desertion experienced by self"),
                _c("i feel so alone like nobody wants me around", "SEP", "SEP.a", "self", 3,
                   "Ostracism/rejection experienced by self"),
            ],
        }],
    },
    {
        "id": "SYN_040_PURE_EASY_SEP",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you experienced any losses recently"},
            {"speaker": "S", "text": "i miss my mother so much since she passed ever since my best friend moved away there's this emptiness i still go to church on sundays"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (loss of love object). Distractor: church.",
            "codings": [
                _c("i miss my mother so much since she passed", "SEP", "SEP.a", "self", 3,
                   "Loss of love object experienced by self"),
                _c("ever since my best friend moved away there's this emptiness", "SEP", "SEP.a", "self", 3,
                   "Loss of support/love object"),
            ],
        }],
    },
    {
        "id": "SYN_041_PURE_MOD_SEP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what has been the hardest thing you've gone through"},
            {"speaker": "S", "text": "my whole family turned their backs on me and the kids were taken away from their parents i mean my neighbors' kids not mine um i drive to work it's about thirty minutes the weather has been cold"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (ostracism, self) + SEP.b (separation, others). Distractors: commute, weather.",
            "codings": [
                _c("my whole family turned their backs on me", "SEP", "SEP.a", "self", 3,
                   "Ostracism/abandonment by family — self"),
                _c("the kids were taken away from their parents", "SEP", "SEP.b", "others", 2,
                   "Separation/loss experienced by others"),
            ],
        }],
    },
    {
        "id": "SYN_042_PURE_MOD_SEP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about what's been weighing on you"},
            {"speaker": "S", "text": "after the divorce the children lost contact with their father and he lost his wife and never recovered from it i like to garden in my spare time it helps"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.b (others' loss). Distractor: gardening.",
            "codings": [
                _c("the children lost contact with their father", "SEP", "SEP.b", "others", 2,
                   "Loss of parental relationship — others"),
                _c("he lost his wife and never recovered from it", "SEP", "SEP.b", "others", 2,
                   "Loss of love object experienced by another person"),
            ],
        }],
    },
    {
        "id": "SYN_043_PURE_MOD_SEP",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "is there anything you miss about the past"},
            {"speaker": "S", "text": "yeah the old house was torn down it meant so much to us and i got fired from my job so that support system is gone too um i've been watching a lot of netflix"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.c (inanimate loss) + SEP.a (loss of support). Distractor: netflix.",
            "codings": [
                _c("the old house was torn down it meant so much to us", "SEP", "SEP.c", "inanimate", 1,
                   "Loss of inanimate object with emotional significance"),
                _c("i got fired from my job so that support system is gone", "SEP", "SEP.a", "self", 3,
                   "Loss of support experienced by self"),
            ],
        }],
    },
    {
        "id": "SYN_044_PURE_HARD_SEP",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how have things been at home"},
            {"speaker": "S", "text": "um it's hard my parents left me at my grandma's when i was little and i never really got over that and now my daughter she's pulling away from me too like i can feel her slipping away but the house is nice we just painted it and the yard looks good"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (childhood abandonment + current loss). Hard: 'slipping away' is metaphorical separation. Distractors: house, yard.",
            "codings": [
                _c("my parents left me at my grandma's when i was little", "SEP", "SEP.a", "self", 3,
                   "Abandonment/desertion experienced by self"),
                _c("i never really got over that", "SEP", "SEP.a", "self", 3,
                   "Ongoing impact of separation/loss"),
                _c("my daughter she's pulling away from me", "SEP", "SEP.a", "self", 3,
                   "Loss of love object — emotional withdrawal"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 1: PURE SINGLE-SUBSCALE — HOS (10 instances)
# ===================================================================

PURE_HOS = [
    {
        "id": "SYN_045_PURE_EASY_HOS",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you get along with people at work"},
            {"speaker": "S", "text": "i just want to punch my boss in the face my neighbor is such an idiot too we carpool sometimes"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.a1 (threat to injure) + HOS.A.c1 (criticizing others). Distractor: carpool.",
            "codings": [
                _c("i just want to punch my boss in the face", "HOS", "HOS.A.a1", "self", 3,
                   "Self threatening to injure another individual"),
                _c("my neighbor is such an idiot", "HOS", "HOS.A.c1", "self", 3,
                   "Self adversely criticizing another human being"),
            ],
        }],
    },
    {
        "id": "SYN_046_PURE_EASY_HOS",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about a conflict you've had recently"},
            {"speaker": "S", "text": "my mother always criticized everything i did she would say the most hurtful things he killed a man in a bar fight that's what she told me about my uncle i like playing guitar"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.c1 (others criticizing) + HOS.B.a1 (others killing). Distractor: guitar.",
            "codings": [
                _c("my mother always criticized everything i did", "HOS", "HOS.B.c1", "others", 3,
                   "Others adversely criticizing other human beings"),
                _c("she would say the most hurtful things", "HOS", "HOS.B.b1", "others", 3,
                   "Others causing suffering/anguish to others"),
                _c("he killed a man in a bar fight", "HOS", "HOS.B.a1", "others", 3,
                   "Others killing/fighting other individuals"),
            ],
        }],
    },
    {
        "id": "SYN_047_PURE_EASY_HOS",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what makes you angry"},
            {"speaker": "S", "text": "i was so mad i kicked the wall this stupid computer never works right i eat lunch at noon usually"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.a3 (self destroying inanimate) + HOS.A.b3 (criticizing inanimate). Distractor: lunch.",
            "codings": [
                _c("i was so mad i kicked the wall", "HOS", "HOS.A.a3", "self", 1,
                   "Self injuring/destroying inanimate object"),
                _c("this stupid computer never works right", "HOS", "HOS.A.b3", "self", 1,
                   "Self adversely criticizing inanimate object"),
            ],
        }],
    },
    {
        "id": "SYN_048_PURE_EASY_HOS",
        "type": "PURE", "difficulty": "EASY", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "has anyone ever treated you unfairly"},
            {"speaker": "S", "text": "yeah the teachers were so unfair to the students and she let the dog starve that's how cruel she was i have a cat now he's sweet"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.d (depriving others) + HOS.B.a2 (harming animals). Distractor: cat.",
            "codings": [
                _c("the teachers were so unfair to the students", "HOS", "HOS.B.d", "others", 2,
                   "Others depriving/disappointing other human beings"),
                _c("she let the dog starve", "HOS", "HOS.B.a2", "others", 2,
                   "Others harming domestic animals"),
            ],
        }],
    },
    {
        "id": "SYN_049_PURE_MOD_HOS",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOS",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how do you handle frustration"},
            {"speaker": "S", "text": "i shouldn't have left them when they needed me and i told her off for being so rude and i feel terrible because i left my dog at the shelter when i moved i just abandoned him the storm destroyed the entire village where my uncle lived um i like hiking when the weather is good we go to the mountains"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.b1 + HOS.A.c1 + HOS.A.b2 + HOS.B.d3. Distractors: hiking, mountains.",
            "codings": [
                _c("i shouldn't have left them when they needed me", "HOS", "HOS.A.b1", "self", 3,
                   "Self abandoning others, causing suffering"),
                _c("i told her off for being so rude", "HOS", "HOS.A.c1", "self", 3,
                   "Self adversely criticizing another human being"),
                _c("i left my dog at the shelter when i moved i just abandoned him", "HOS", "HOS.A.b2", "self", 2,
                   "Self abandoning domestic animals/pets"),
                _c("the storm destroyed the entire village", "HOS", "HOS.B.d3", "others", 1,
                   "Others harmed by inanimate forces — storm"),
            ],
        }],
    },
    {
        "id": "SYN_050_PURE_MOD_HOS",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you ever lose your temper"},
            {"speaker": "S", "text": "yeah i just get so angry sometimes like cursing and yelling for no reason and my coworker she's always vaguely putting people down in this passive way i read before bed usually"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.c3 (hostile words without referent) + HOS.B.c2 (vague criticism). Distractor: reading.",
            "codings": [
                _c("i just get so angry sometimes like cursing and yelling for no reason", "HOS", "HOS.A.c3", "self", 1,
                   "Self using hostile words, cursing — anger without referent"),
                _c("she's always vaguely putting people down in this passive way", "HOS", "HOS.B.c2", "others", 2,
                   "Others criticizing individuals in a vague or mild manner"),
            ],
        }],
    },
    {
        "id": "SYN_051_PURE_MOD_HOS",
        "type": "PURE", "difficulty": "MOD", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about a time when something really upset you"},
            {"speaker": "S", "text": "this guy was so angry just raging for no reason and there were these stray dogs fighting each other in the alley it was awful the park nearby is actually really nice"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.c3 (others angry without referent) + HOS.B.e3 (subhumans fighting). Distractor: park.",
            "codings": [
                _c("this guy was so angry just raging for no reason", "HOS", "HOS.B.c3", "others", 1,
                   "Others angry/cursing without reference to cause"),
                _c("there were these stray dogs fighting each other", "HOS", "HOS.B.e3", "others", 1,
                   "Subhumans fighting each other"),
            ],
        }],
    },
    {
        "id": "SYN_052_PURE_HARD_HOS",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "HOS",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "has anyone in your life been violent"},
            {"speaker": "S", "text": "yeah my ex he was violent he used to hit people and his friend's body was found mutilated it was horrible they found all these broken windows and damaged property around the house too but i'm not really angry about it anymore i've moved on i like cooking pasta"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.a1 + HOS.B.f + HOS.B.a3 + HOS.B.f3 (denial). Distractors: moved on (genuine), pasta.",
            "codings": [
                _c("he used to hit people", "HOS", "HOS.B.a1", "others", 3,
                   "Others fighting/injuring other individuals"),
                _c("his friend's body was found mutilated", "HOS", "HOS.B.f", "others", 2,
                   "Bodies mutilated/depreciated"),
                _c("broken windows and damaged property around the house", "HOS", "HOS.B.a3", "others", 1,
                   "Inanimate objects broken/destroyed"),
                _c("i'm not really angry about it anymore", "HOS", "HOS.B.f3", "denial", 1,
                   "Denial of anger"),
            ],
        }],
    },
    {
        "id": "SYN_053_PURE_HARD_HOS",
        "type": "PURE", "difficulty": "HARD", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what makes you most frustrated"},
            {"speaker": "S", "text": "i deprived my kids of a normal childhood by working too much and i disappointed my wife over and over i even kicked the neighbor's cat once when i was angry and she said i was being sort of passive-aggressive and dismissive toward her friends she also said some guy robbed her pet store and abandoned the animals the store is on maple street and his buddy was talking trash about the whole neighborhood"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.d + HOS.A.a2 + HOS.A.c2 + HOS.B.b2 + HOS.B.b3. Distractor: address.",
            "codings": [
                _c("i deprived my kids of a normal childhood", "HOS", "HOS.A.d", "self", 2,
                   "Self depriving other human beings"),
                _c("i disappointed my wife over and over", "HOS", "HOS.A.d", "self", 2,
                   "Self disappointing other human beings"),
                _c("i even kicked the neighbor's cat once when i was angry", "HOS", "HOS.A.a2", "self", 2,
                   "Self injuring domestic animals"),
                _c("i was being sort of passive-aggressive and dismissive toward her friends", "HOS", "HOS.A.c2", "self", 2,
                   "Self criticizing others in a vague or mild manner"),
                _c("some guy robbed her pet store and abandoned the animals", "HOS", "HOS.B.b2", "others", 2,
                   "Others abandoning/robbing domestic animals"),
                _c("his buddy was talking trash about the whole neighborhood", "HOS", "HOS.B.b3", "others", 1,
                   "Others criticizing/depreciating inanimate objects/places/situations"),
            ],
        }],
    },
    {
        "id": "SYN_054_PURE_ADV_HOS",
        "type": "PURE", "difficulty": "ADV", "primary_subscale": "HOS",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "tell me about your feelings toward other people"},
            {"speaker": "S", "text": "i could have killed her when she said that but you know i didn't obviously i'm not a violent person but she was dying in that hospital from what they did to her they basically murdered her with their negligence and i don't hate anyone not really i'm at peace with it all we have a lovely garden out back"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Adversarial: 'could have killed her' is frustration idiom NOT coded as HOS.A.a1. But 'murdered her with negligence' IS coded. HOS.B.f3 denial. Distractors: idiom, garden.",
            "codings": [
                _c("they basically murdered her with their negligence", "HOS", "HOS.B.a1", "others", 3,
                   "Others killing other individuals — negligent death"),
                _c("i don't hate anyone not really", "HOS", "HOS.B.f3", "denial", 1,
                   "Denial of hatred/hostility"),
                _c("she was dying in that hospital from what they did to her", "HOS", "HOS.B.e", "others", 2,
                   "Others dying in death-dealing situations"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 2: MULTI-SUBSCALE (25 instances) — Part 1 (13)
# ===================================================================

MULTI_SUBSCALE = [
    # HOP + SEP (5 instances — highest confusion pair)
    {
        "id": "SYN_055_MULTI_EASY_HOP-SEP",
        "type": "MULTI", "difficulty": "EASY", "primary_subscale": "HOP-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how are things going for you"},
            {"speaker": "S", "text": "she left me and now there's nothing to look forward to i feel so empty since she's gone and nothing will ever get better i like watching sports though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (she left, emptiness) + HOP.3b (nothing to look forward to, won't get better).",
            "codings": [
                _c("she left me", "SEP", "SEP.a", "self", 3, "Abandonment experienced by self"),
                _c("there's nothing to look forward to", "HOP", "HOP.3b", "self", 1, "Hopelessness/despair"),
                _c("i feel so empty since she's gone", "SEP", "SEP.a", "self", 3, "Loss of love object"),
                _c("nothing will ever get better", "HOP", "HOP.3b", "self", 1, "Pessimism about future"),
            ],
        }],
    },
    {
        "id": "SYN_056_MULTI_EASY_HOP-SEP",
        "type": "MULTI", "difficulty": "EASY", "primary_subscale": "HOP-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about your family situation"},
            {"speaker": "S", "text": "my kids don't talk to me anymore i miss them so much and i don't think things will ever be the same nobody is going to help me fix this i play cards on fridays"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (loss of children) + HOP.3b (won't be the same) + HOP.2a (nobody helps).",
            "codings": [
                _c("my kids don't talk to me anymore", "SEP", "SEP.a", "self", 3, "Loss of love objects"),
                _c("i miss them so much", "SEP", "SEP.a", "self", 3, "Missing loved ones"),
                _c("i don't think things will ever be the same", "HOP", "HOP.3b", "self", 1, "Pessimism"),
                _c("nobody is going to help me fix this", "HOP", "HOP.2a", "self", 1, "Not receiving help from others"),
            ],
        }],
    },
    {
        "id": "SYN_057_MULTI_MOD_HOP-SEP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "HOP-SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what keeps you up at night"},
            {"speaker": "S", "text": "i just keep thinking about how alone i am since everyone left and there's no point in trying to make new friends it won't work out i can't help myself anymore the apartment is quiet now we live on the third floor"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a (alone, everyone left) + HOP.3b (no point) + HOP.2b (can't help self).",
            "codings": [
                _c("how alone i am since everyone left", "SEP", "SEP.a", "self", 3, "Abandonment/ostracism"),
                _c("there's no point in trying to make new friends", "HOP", "HOP.3b", "self", 1, "Hopelessness/futility"),
                _c("it won't work out", "HOP", "HOP.3b", "self", 1, "Pessimism"),
                _c("i can't help myself anymore", "HOP", "HOP.2b", "self", 1, "Not getting support from self"),
            ],
        }],
    },
    {
        "id": "SYN_058_MULTI_HARD_HOP-SEP",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "HOP-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you see your future"},
            {"speaker": "S", "text": "i mean what future right everyone who mattered is gone and i'm just sort of drifting i don't expect good things to happen to people like me i guess maybe i'll get a dog"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a + HOP.3b + HOP.1. Hard: hedged, implicit.",
            "codings": [
                _c("everyone who mattered is gone", "SEP", "SEP.a", "self", 3, "Loss of love objects"),
                _c("i'm just sort of drifting", "HOP", "HOP.3b", "self", 1, "Lack of interest/ambition"),
                _c("i don't expect good things to happen to people like me", "HOP", "HOP.1", "inanimate", 1, "Not expecting good fortune"),
            ],
        }],
    },
    {
        "id": "SYN_059_MULTI_ADV_HOP-SEP",
        "type": "MULTI", "difficulty": "ADV", "primary_subscale": "HOP-SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what's on your mind today"},
            {"speaker": "S", "text": "my heart is broken you know not literally ha but since the divorce i just feel abandoned and there's this hopelessness like i've hit rock bottom things were looking up for a bit but that's over now we live in a nice neighborhood the schools are good"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Adversarial: 'heart is broken' NOT SOM (emotional). 'hit rock bottom' IS HOP. SEP.a + HOP.3b.",
            "codings": [
                _c("since the divorce i just feel abandoned", "SEP", "SEP.a", "self", 3, "Abandonment from divorce"),
                _c("there's this hopelessness", "HOP", "HOP.3b", "self", 1, "Direct hopelessness reference"),
                _c("i've hit rock bottom", "HOP", "HOP.3b", "self", 1, "Hopelessness/despair metaphor"),
                _c("things were looking up for a bit but that's over now", "HOP", "HOP.3b", "self", 1, "Pessimism about reversal"),
            ],
        }],
    },
    # SAC + SEP (3 instances)
    {
        "id": "SYN_060_MULTI_MOD_SAC-SEP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SAC-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about your breakup"},
            {"speaker": "S", "text": "she left because i wasn't good enough i feel so alone now and it's all my fault i drove her away i watch the news before bed"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.a (guilt/self-blame) + SEP.a (abandonment/loneliness).",
            "codings": [
                _c("she left because i wasn't good enough", "SAC", "SAC.B.a", "self", 3, "Shame/inadequacy — self"),
                _c("i feel so alone now", "SEP", "SEP.a", "self", 3, "Loneliness from loss"),
                _c("it's all my fault i drove her away", "SAC", "SAC.A.a", "self", 3, "Self-condemnation/guilt"),
            ],
        }],
    },
    {
        "id": "SYN_061_MULTI_MOD_SAC-SEP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SAC-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been the hardest part of this experience"},
            {"speaker": "S", "text": "i keep blaming myself for losing them i'm such a terrible parent and now my children are gone i can barely stand the emptiness we used to have game nights"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b2 (self-blame) + SAC.A.a (terrible parent) + SEP.a (children gone, emptiness).",
            "codings": [
                _c("i keep blaming myself for losing them", "SAC", "SAC.C.b2", "self", 3, "Self-blame"),
                _c("i'm such a terrible parent", "SAC", "SAC.C.b2", "self", 3, "Considering self worthless"),
                _c("my children are gone", "SEP", "SEP.a", "self", 3, "Loss of love objects"),
                _c("i can barely stand the emptiness", "SEP", "SEP.a", "self", 3, "Emptiness from loss"),
            ],
        }],
    },
    {
        "id": "SYN_062_MULTI_HARD_SAC-SEP",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "SAC-SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how are you coping with everything"},
            {"speaker": "S", "text": "i'm ashamed that i couldn't keep the family together everyone scattered and i'm the one left behind i should have tried harder i feel like i deserve this loneliness um the commute is about forty minutes i listen to podcasts"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.B.a (shame) + SEP.a (scattered/left behind) + SAC.C.a3 (deserve punishment) + SEP.a (loneliness).",
            "codings": [
                _c("i'm ashamed that i couldn't keep the family together", "SAC", "SAC.B.a", "self", 3, "Shame — self"),
                _c("everyone scattered and i'm the one left behind", "SEP", "SEP.a", "self", 3, "Abandonment/desertion"),
                _c("i should have tried harder", "SAC", "SAC.C.b3", "self", 2, "Self-criticism/regret"),
                _c("i deserve this loneliness", "SAC", "SAC.C.a3", "self", 2, "Deserving punishment"),
            ],
        }],
    },
    # DAM + SEP (3 instances)
    {
        "id": "SYN_063_MULTI_MOD_DAM-SEP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you dealt with any losses"},
            {"speaker": "S", "text": "my father died last spring and i miss him terribly there's this void that nothing can fill he was sixty two the funeral was nice though people came from everywhere"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b (death) + SEP.a (missing/void).",
            "codings": [
                _c("my father died last spring", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i miss him terribly", "SEP", "SEP.a", "self", 3, "Loss of love object"),
                _c("there's this void that nothing can fill", "SEP", "SEP.a", "self", 3, "Emptiness from loss"),
            ],
        }],
    },
    {
        "id": "SYN_064_MULTI_MOD_DAM-SEP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been the most painful experience"},
            {"speaker": "S", "text": "losing my sister to that car accident was devastating she died instantly and i'm just left here without her i feel completely abandoned i have a goldfish now"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b (death in accident) + SEP.a (loss/abandonment).",
            "codings": [
                _c("my sister died instantly in that car accident", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i'm just left here without her", "SEP", "SEP.a", "self", 3, "Loss of love object/desertion"),
                _c("i feel completely abandoned", "SEP", "SEP.a", "self", 3, "Abandonment/loss"),
            ],
        }],
    },
    {
        "id": "SYN_065_MULTI_HARD_DAM-SEP",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me more about that time in your life"},
            {"speaker": "S", "text": "well his body was badly injured in the explosion and then he passed two days later and i lost my whole world there was nothing left of our old life together even the house was destroyed i go to therapy on wednesdays"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.B.b (injury) + DAM.A.b (death) + SEP.a (lost world) + SEP.c + DAM.B.c (house destroyed).",
            "codings": [
                _c("his body was badly injured in the explosion", "DAM", "DAM.B.b", "others", 2, "Injury to others"),
                _c("he passed two days later", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i lost my whole world", "SEP", "SEP.a", "self", 3, "Loss of love/support"),
                _c("the house was destroyed", "DAM", "DAM.B.c", "inanimate", 1, "Physical destruction of inanimate"),
            ],
        }],
    },
    # SOM + PMR (3 instances — key boundary)
    {
        "id": "SYN_066_MULTI_MOD_SOM-PMR",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SOM-PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how have you been physically and mentally"},
            {"speaker": "S", "text": "i have these terrible headaches and my back hurts and on top of that everything feels like it's in slow motion like my brain won't work i eat dinner at six usually"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (headaches, back) + PMR.1 (slow motion, brain). Key boundary test.",
            "codings": [
                _c("i have these terrible headaches", "SOM", "SOM.E", "self", 1, "General somatic — headache"),
                _c("my back hurts", "SOM", "SOM.E", "self", 1, "General somatic — backache"),
                _c("everything feels like it's in slow motion", "PMR", "PMR.1", "self", 1, "General retardation"),
                _c("my brain won't work", "PMR", "PMR.1", "self", 1, "Cognitive slowing"),
            ],
        }],
    },
    {
        "id": "SYN_067_MULTI_MOD_SOM-PMR",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SOM-PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "describe how you feel on a typical day"},
            {"speaker": "S", "text": "exhausted like no energy at all and my whole body just aches plus this general slowness where i can't think or move properly i've been losing weight too i work nine to five"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (exhaustion, aches, weight) + PMR.1 (general slowness). Boundary: exhaustion=SOM, slowness=PMR.",
            "codings": [
                _c("exhausted like no energy at all", "SOM", "SOM.E", "self", 1, "Loss of energy/fatigability"),
                _c("my whole body just aches", "SOM", "SOM.E", "self", 1, "General somatic — body aches"),
                _c("this general slowness where i can't think or move properly", "PMR", "PMR.1", "self", 1, "General retardation in thinking and action"),
                _c("i've been losing weight", "SOM", "SOM.E", "self", 1, "Weight loss"),
            ],
        }],
    },
    # SOM + PMR continued
    {
        "id": "SYN_068_MULTI_HARD_SOM-PMR",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "SOM-PMR",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what's the worst part of your day"},
            {"speaker": "S", "text": "mornings are bad um my stomach is upset and i can't sleep and then on top of the physical stuff there's this fog where my mind just won't engage at all everything moves in slow motion i drink coffee though and the commute is okay"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.D (stomach) + SOM.B (sleep) + PMR.1 (fog, slow motion). Hard boundary.",
            "codings": [
                _c("my stomach is upset", "SOM", "SOM.D", "self", 1, "GI disturbance"),
                _c("i can't sleep", "SOM", "SOM.B", "self", 1, "Sleep disturbance"),
                _c("this fog where my mind just won't engage at all", "PMR", "PMR.1", "self", 1, "Cognitive retardation"),
                _c("everything moves in slow motion", "PMR", "PMR.1", "self", 1, "General retardation"),
            ],
        }],
    },
    # HOS + DAM (3 instances)
    {
        "id": "SYN_069_MULTI_MOD_HOS-DAM",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you witnessed any violence"},
            {"speaker": "S", "text": "yeah this guy attacked someone on the street badly injured him and the victim he nearly died from the beating it was on the news we live in a quiet area usually"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.a1 (others attacking) + DAM.B.b (injury) + DAM.A.b (nearly died).",
            "codings": [
                _c("this guy attacked someone on the street", "HOS", "HOS.B.a1", "others", 3, "Others fighting/injuring individuals"),
                _c("badly injured him", "DAM", "DAM.B.b", "others", 2, "Injury to another person"),
                _c("the victim he nearly died from the beating", "DAM", "DAM.A.b", "others", 2, "Threat of death — others"),
            ],
        }],
    },
    {
        "id": "SYN_070_MULTI_MOD_HOS-DAM",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about something that upset you"},
            {"speaker": "S", "text": "my neighbor's ex broke into her house and trashed everything smashed all the windows and she got cut really badly on the glass i have three cats"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.a1 (breaking in) + HOS.B.a3 (property destruction) + DAM.B.b (cut/injury).",
            "codings": [
                _c("her ex broke into her house and trashed everything", "HOS", "HOS.B.a1", "others", 3, "Others robbing/causing suffering"),
                _c("smashed all the windows", "HOS", "HOS.B.a3", "others", 1, "Inanimate objects broken/destroyed"),
                _c("she got cut really badly on the glass", "DAM", "DAM.B.b", "others", 2, "Injury — tissue damage to others"),
            ],
        }],
    },
    {
        "id": "SYN_071_MULTI_HARD_HOS-DAM",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "is there anything from your past that still affects you"},
            {"speaker": "S", "text": "my uncle was shot and killed in a robbery and the person who did it just got away with it and i want to hurt that person for what they did his body was left there for hours we go to the cemetery every year"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.a1 (shooting) + DAM.A.b (killed) + HOS.A.a1 (want to hurt) + HOS.B.f (body left).",
            "codings": [
                _c("my uncle was shot and killed in a robbery", "HOS", "HOS.B.a1", "others", 3, "Others killing individuals"),
                _c("my uncle was shot and killed", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i want to hurt that person", "HOS", "HOS.A.a1", "self", 3, "Self threatening to injure others"),
                _c("his body was left there for hours", "HOS", "HOS.B.f", "others", 2, "Bodies depreciated/defiled"),
            ],
        }],
    },
    # SAC + HOP (3 instances)
    {
        "id": "SYN_072_MULTI_MOD_SAC-HOP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SAC-HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been weighing on you lately"},
            {"speaker": "S", "text": "i'm such a screw-up and nothing's going to get better because of it everything i touch falls apart and there's no point trying anymore i have a meeting tomorrow"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b2 (screw-up) + HOP.3b (nothing better, no point) + SAC.C.b3 (everything falls apart).",
            "codings": [
                _c("i'm such a screw-up", "SAC", "SAC.C.b2", "self", 3, "Self-blame/worthlessness"),
                _c("nothing's going to get better because of it", "HOP", "HOP.3b", "self", 1, "Pessimism"),
                _c("everything i touch falls apart", "SAC", "SAC.C.b3", "self", 2, "Self-criticism — self as in error"),
                _c("there's no point trying anymore", "HOP", "HOP.3b", "self", 1, "Hopelessness/futility"),
            ],
        }],
    },
    {
        "id": "SYN_073_MULTI_MOD_SAC-HOP",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SAC-HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you see yourself"},
            {"speaker": "S", "text": "i'm a failure plain and simple i can't do anything right and the future looks completely hopeless because i keep ruining everything i go to the gym sometimes"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b2 (failure) + SAC.C.b3 (ruining) + HOP.3b (hopeless future).",
            "codings": [
                _c("i'm a failure plain and simple", "SAC", "SAC.C.b2", "self", 3, "Considering self worthless"),
                _c("i can't do anything right", "SAC", "SAC.C.b2", "self", 3, "Self-blame"),
                _c("the future looks completely hopeless", "HOP", "HOP.3b", "self", 1, "Hopelessness about future"),
                _c("i keep ruining everything", "SAC", "SAC.C.b3", "self", 2, "Self-criticism"),
            ],
        }],
    },
    {
        "id": "SYN_074_MULTI_HARD_SAC-HOP",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "SAC-HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "what do you think about when you're alone"},
            {"speaker": "S", "text": "just how badly i've messed up my life and how there's no coming back from it i deserve to suffer for the choices i've made and nothing good is ever going to happen to someone like me um i've been watching that new show it's pretty good actually the weather has been nice"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b3 (messed up) + HOP.3b (no coming back) + SAC.C.a3 (deserve suffering) + HOP.1 (nothing good).",
            "codings": [
                _c("how badly i've messed up my life", "SAC", "SAC.C.b3", "self", 2, "Self-criticism — self as in error"),
                _c("there's no coming back from it", "HOP", "HOP.3b", "self", 1, "Despair/hopelessness"),
                _c("i deserve to suffer for the choices i've made", "SAC", "SAC.C.a3", "self", 2, "Deserving punishment"),
                _c("nothing good is ever going to happen to someone like me", "HOP", "HOP.1", "inanimate", 1, "Not receiving good fortune"),
            ],
        }],
    },
    # SOM + HOS (2 instances)
    {
        "id": "SYN_075_MULTI_MOD_SOM-HOS",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "SOM-HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how are you feeling today"},
            {"speaker": "S", "text": "i have this horrible headache and my stomach is killing me and i'm so angry at my doctor for not listening to me he's completely useless i take ibuprofen sometimes"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (headache) + SOM.D (stomach) + HOS.A.c1 (criticizing doctor).",
            "codings": [
                _c("i have this horrible headache", "SOM", "SOM.E", "self", 1, "General somatic — headache"),
                _c("my stomach is killing me", "SOM", "SOM.D", "self", 1, "GI disturbance"),
                _c("i'm so angry at my doctor for not listening to me", "HOS", "HOS.A.c1", "self", 3, "Self criticizing another human"),
                _c("he's completely useless", "HOS", "HOS.A.c1", "self", 3, "Self depreciating another human"),
            ],
        }],
    },
    {
        "id": "SYN_076_MULTI_HARD_SOM-HOS",
        "type": "MULTI", "difficulty": "HARD", "primary_subscale": "SOM-HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been going on with your health"},
            {"speaker": "S", "text": "i can't sleep because of the pain and the healthcare system they don't care about people like me the nurses were dismissive and rude and i've been losing weight from the stress of it all i like reading though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.B (sleep) + SOM.E (pain, weight) + HOS.A.b3 (criticizing system) + HOS.B.d (dismissive nurses).",
            "codings": [
                _c("i can't sleep because of the pain", "SOM", "SOM.B", "self", 1, "Sleep disturbance"),
                _c("the healthcare system they don't care about people like me", "HOS", "HOS.A.b3", "self", 1, "Criticizing inanimate systems/situations"),
                _c("the nurses were dismissive and rude", "HOS", "HOS.B.d", "others", 2, "Others depriving/disappointing humans"),
                _c("i've been losing weight from the stress", "SOM", "SOM.E", "self", 1, "Weight loss"),
            ],
        }],
    },
    # Other pairings (3 instances)
    {
        "id": "SYN_077_MULTI_MOD_HOP-SOM",
        "type": "MULTI", "difficulty": "MOD", "primary_subscale": "HOP-SOM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how are you managing day to day"},
            {"speaker": "S", "text": "i have no energy to get through the day and honestly i have no reason to either like what's the point my body is falling apart and my spirit is too i drive to work"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.E (no energy) + HOP.3b (no reason/what's the point) + SOM.A (body falling apart).",
            "codings": [
                _c("i have no energy to get through the day", "SOM", "SOM.E", "self", 1, "Loss of energy"),
                _c("i have no reason to either like what's the point", "HOP", "HOP.3b", "self", 1, "Hopelessness/futility"),
                _c("my body is falling apart", "SOM", "SOM.A", "self", 1, "Bodily malfunctioning"),
            ],
        }],
    },
    {
        "id": "SYN_078_MULTI_ADV_DAM-HOS-SEP",
        "type": "MULTI", "difficulty": "ADV", "primary_subscale": "DAM-HOS-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about the most traumatic thing you've experienced"},
            {"speaker": "S", "text": "my brother was murdered in a gang shooting and i lost everything after that they just left his body in the street like garbage and now i'm all alone no family left i play basketball on weekends"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Triple: HOS.B.a1 (murder) + DAM.A.b (death) + HOS.B.f (body defiled) + SEP.a (alone).",
            "codings": [
                _c("my brother was murdered in a gang shooting", "HOS", "HOS.B.a1", "others", 3, "Others killing individuals"),
                _c("my brother was murdered", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("they just left his body in the street like garbage", "HOS", "HOS.B.f", "others", 2, "Bodies depreciated/defiled"),
                _c("now i'm all alone no family left", "SEP", "SEP.a", "self", 3, "Loss of family/support"),
            ],
        }],
    },
    {
        "id": "SYN_079_MULTI_ADV_HOS-SEP",
        "type": "MULTI", "difficulty": "ADV", "primary_subscale": "HOS-SEP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "can you tell me about a difficult relationship"},
            {"speaker": "S", "text": "my ex she was verbally abusive constantly tearing me down and criticizing me in front of everyone and then she just kicked me out abandoned me with nothing i could have killed her when she did that but obviously i'm joking um the apartment is downtown the rent is reasonable"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.c1 (ex criticizing) + HOS.B.b1 (causing suffering) + SEP.a (kicked out/abandoned). Adversarial: 'could have killed her' = idiom NOT coded.",
            "codings": [
                _c("she was verbally abusive constantly tearing me down", "HOS", "HOS.B.b1", "others", 3, "Others causing suffering/anguish"),
                _c("criticizing me in front of everyone", "HOS", "HOS.B.c1", "others", 3, "Others criticizing individuals"),
                _c("she just kicked me out", "SEP", "SEP.a", "self", 3, "Abandonment/desertion"),
                _c("abandoned me with nothing", "SEP", "SEP.a", "self", 3, "Abandonment experienced by self"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 3: MULTI-CODE (15 instances) — same clause codes 2+ subscales
# ===================================================================

MULTI_CODE = [
    # DAM + SEP dual-coded (4 clauses across instances)
    {
        "id": "SYN_080_MCODE_HARD_DAM-SEP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's been the hardest thing"},
            {"speaker": "S", "text": "my mother died and i miss her terribly she was everything to me and now she's gone forever i play tennis on weekends"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual-code: 'died and I miss her' = DAM.A.b + SEP.a on overlapping clauses.",
            "codings": [
                _c("my mother died", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i miss her terribly", "SEP", "SEP.a", "self", 3, "Loss of love object"),
                _c("she was everything to me and now she's gone forever", "SEP", "SEP.a", "self", 3, "Loss of love object — permanent"),
            ],
        }],
    },
    {
        "id": "SYN_081_MCODE_HARD_DAM-SEP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about your losses"},
            {"speaker": "S", "text": "my best friend was killed in an accident and losing him destroyed me inside i'm so lonely without him we used to fish together"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: DAM.A.b (killed) + SEP.a (losing/lonely).",
            "codings": [
                _c("my best friend was killed in an accident", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("losing him destroyed me inside", "SEP", "SEP.a", "self", 3, "Loss of love object"),
                _c("i'm so lonely without him", "SEP", "SEP.a", "self", 3, "Loneliness from loss"),
            ],
        }],
    },
    # HOS + DAM dual-coded (3 clauses)
    {
        "id": "SYN_082_MCODE_HARD_HOS-DAM",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "have you seen anything disturbing"},
            {"speaker": "S", "text": "he was murdered in the street shot three times and left to bleed out they never caught the guy i have a garden out back"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: HOS.B.a1 (murder) + DAM.A.b (death) + DAM.B.b (shot/bleeding).",
            "codings": [
                _c("he was murdered in the street", "HOS", "HOS.B.a1", "others", 3, "Others killing individuals"),
                _c("he was murdered in the street", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("shot three times and left to bleed out", "DAM", "DAM.B.b", "others", 2, "Injury/tissue damage — others"),
            ],
        }],
    },
    {
        "id": "SYN_083_MCODE_ADV_HOS-DAM",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what happened to your neighbor"},
            {"speaker": "S", "text": "some guys beat him so badly he ended up in a coma his skull was fractured and they thought he might die the police eventually arrested someone i have two kids"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: HOS.B.a1 (beating) + DAM.B.b (skull fracture) + DAM.A.b (might die).",
            "codings": [
                _c("some guys beat him so badly", "HOS", "HOS.B.a1", "others", 3, "Others fighting/injuring individuals"),
                _c("his skull was fractured", "DAM", "DAM.B.b", "others", 2, "Injury/tissue damage"),
                _c("they thought he might die", "DAM", "DAM.A.b", "others", 2, "Threat of death — others"),
            ],
        }],
    },
    # SAC + SEP dual-coded (3 clauses)
    {
        "id": "SYN_084_MCODE_HARD_SAC-SEP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "SAC-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "why do you think the relationship ended"},
            {"speaker": "S", "text": "she left because i'm worthless i pushed her away with my behavior and now i'm alone i eat lunch at my desk"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: SAC.C.b2 (worthless) + SEP.a (left/alone). Same event, dual coding.",
            "codings": [
                _c("she left because i'm worthless", "SAC", "SAC.C.b2", "self", 3, "Self as worthless — cause of loss"),
                _c("she left", "SEP", "SEP.a", "self", 3, "Abandonment experienced by self"),
                _c("i pushed her away with my behavior", "SAC", "SAC.C.b3", "self", 2, "Self-criticism"),
                _c("now i'm alone", "SEP", "SEP.a", "self", 3, "Loneliness from loss"),
            ],
        }],
    },
    {
        "id": "SYN_085_MCODE_HARD_SAC-SEP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "SAC-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you feel about what happened"},
            {"speaker": "S", "text": "it's my fault they all left i'm a terrible person who doesn't deserve to have people around i miss them all so much the house is really quiet now i have a cat though"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.a (fault) + SAC.C.b2 (terrible person) + SEP.a (they left/miss them).",
            "codings": [
                _c("it's my fault they all left", "SAC", "SAC.A.a", "self", 3, "Guilt/self-condemnation"),
                _c("they all left", "SEP", "SEP.a", "self", 3, "Abandonment"),
                _c("i'm a terrible person who doesn't deserve to have people around", "SAC", "SAC.C.b2", "self", 3, "Self-worthlessness"),
                _c("i miss them all so much", "SEP", "SEP.a", "self", 3, "Loss of love objects"),
            ],
        }],
    },
    # SAC + HOP dual-coded (3 clauses)
    {
        "id": "SYN_086_MCODE_HARD_SAC-HOP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "SAC-HOP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what goes through your mind"},
            {"speaker": "S", "text": "i'm a failure and nothing will ever change because of who i am i've ruined everything and there's no hope left for me i like dogs"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: SAC.C.b2 (failure) + HOP.3b (nothing will change/no hope).",
            "codings": [
                _c("i'm a failure", "SAC", "SAC.C.b2", "self", 3, "Self as worthless"),
                _c("nothing will ever change", "HOP", "HOP.3b", "self", 1, "Hopelessness/pessimism"),
                _c("i've ruined everything", "SAC", "SAC.C.b3", "self", 2, "Self-criticism"),
                _c("there's no hope left for me", "HOP", "HOP.3b", "self", 1, "Despair"),
            ],
        }],
    },
    {
        "id": "SYN_087_MCODE_ADV_SAC-HOP",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "SAC-HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "tell me about your outlook on life"},
            {"speaker": "S", "text": "i mean what's the use i'm the one who caused all this mess and it's only going to get worse i can't forgive myself and i don't see any way out of this darkness i ordered pizza last night it was pretty good the place is on third street"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.a (caused mess) + HOP.3b (what's the use/worse/no way out) + SAC.C.b2 (can't forgive).",
            "codings": [
                _c("what's the use", "HOP", "HOP.3b", "self", 1, "Futility/hopelessness"),
                _c("i'm the one who caused all this mess", "SAC", "SAC.A.a", "self", 3, "Guilt/self-condemnation"),
                _c("it's only going to get worse", "HOP", "HOP.3b", "self", 1, "Pessimism"),
                _c("i can't forgive myself", "SAC", "SAC.C.b2", "self", 3, "Self-blame/self-hatred"),
                _c("i don't see any way out of this darkness", "HOP", "HOP.3b", "self", 1, "Despair/hopelessness"),
            ],
        }],
    },
    # HOS + SEP dual-coded (3 clauses)
    {
        "id": "SYN_088_MCODE_HARD_HOS-SEP",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "HOS-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what happened with your family"},
            {"speaker": "S", "text": "they kicked me out of the house threw my stuff on the lawn and i'm left with nothing no family no support i take the bus now"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: HOS.B.b1 (kicked out/threw stuff) + SEP.a (left with nothing).",
            "codings": [
                _c("they kicked me out of the house", "HOS", "HOS.B.b1", "others", 3, "Others causing suffering/anguish"),
                _c("they kicked me out", "SEP", "SEP.a", "self", 3, "Abandonment/ostracism"),
                _c("threw my stuff on the lawn", "HOS", "HOS.B.a3", "others", 1, "Inanimate objects destroyed"),
                _c("i'm left with nothing no family no support", "SEP", "SEP.a", "self", 3, "Loss of support/family"),
            ],
        }],
    },
    {
        "id": "SYN_089_MCODE_ADV_HOS-SEP",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "HOS-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about that time"},
            {"speaker": "S", "text": "my own mother she rejected me completely told me i was dead to her her words were brutal and cruel and i lost everything that day the park across the street is where i go to think"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.b1 (rejection/cruelty) + SEP.a (rejected/lost everything). 'dead to her' = figurative SEP not DAM.",
            "codings": [
                _c("my own mother she rejected me completely", "SEP", "SEP.a", "self", 3, "Rejection/ostracism"),
                _c("told me i was dead to her", "SEP", "SEP.a", "self", 3, "Ostracism — figurative death-as-rejection"),
                _c("her words were brutal and cruel", "HOS", "HOS.B.b1", "others", 3, "Others causing suffering/anguish"),
                _c("i lost everything that day", "SEP", "SEP.a", "self", 3, "Loss of love/support"),
            ],
        }],
    },
    # SOM + PMR dual-coded (2 clauses)
    {
        "id": "SYN_090_MCODE_HARD_SOM-PMR",
        "type": "MCODE", "difficulty": "HARD", "primary_subscale": "SOM-PMR",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how does your body feel"},
            {"speaker": "S", "text": "no energy everything in slow motion my limbs are heavy and my mind won't work it's like the fatigue and the slowness are all mixed together i drink tea in the mornings"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Dual: SOM.E (no energy, heavy limbs) + PMR.1 (slow motion, mind won't work). Overlapping on 'fatigue+slowness'.",
            "codings": [
                _c("no energy", "SOM", "SOM.E", "self", 1, "Loss of energy"),
                _c("everything in slow motion", "PMR", "PMR.1", "self", 1, "General retardation"),
                _c("my limbs are heavy", "SOM", "SOM.E", "self", 1, "Heaviness in limbs"),
                _c("my mind won't work", "PMR", "PMR.1", "self", 1, "Cognitive retardation"),
            ],
        }],
    },
    # DAM + HOS + SEP triple-coded (2 instances)
    {
        "id": "SYN_091_MCODE_ADV_DAM-HOS-SEP",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "DAM-HOS-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "what's the worst thing that happened to you"},
            {"speaker": "S", "text": "my husband was beaten to death by those men and i watched him die right in front of me and now i'm completely alone with nothing they took everything from me i garden to keep busy"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Triple: HOS.B.a1 (beaten) + DAM.A.b (death) + DAM.B.b (beaten) + SEP.a (alone/nothing).",
            "codings": [
                _c("my husband was beaten to death by those men", "HOS", "HOS.B.a1", "others", 3, "Others killing individuals"),
                _c("my husband was beaten to death", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("i watched him die right in front of me", "DAM", "DAM.A.b", "others", 2, "Death witnessed"),
                _c("now i'm completely alone with nothing", "SEP", "SEP.a", "self", 3, "Total loss of support/love"),
                _c("they took everything from me", "HOS", "HOS.B.b1", "others", 3, "Others robbing/causing suffering"),
            ],
        }],
    },
    {
        "id": "SYN_092_MCODE_ADV_DAM-HOS-SEP",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "DAM-HOS-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "tell me about that experience"},
            {"speaker": "S", "text": "they stabbed my brother and he bled out and died right there on the corner and after that the whole family fell apart everyone went their separate ways and i was left behind with nobody i cook pasta mostly"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Triple: HOS.B.a1 (stabbing) + DAM.A.b (died) + DAM.B.b (bled out) + SEP.a (family fell apart/left behind).",
            "codings": [
                _c("they stabbed my brother", "HOS", "HOS.B.a1", "others", 3, "Others injuring individuals"),
                _c("he bled out and died", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
                _c("he bled out", "DAM", "DAM.B.b", "others", 2, "Tissue damage — bleeding"),
                _c("the whole family fell apart everyone went their separate ways", "SEP", "SEP.a", "self", 3, "Loss of family — dissolution"),
                _c("i was left behind with nobody", "SEP", "SEP.a", "self", 3, "Abandonment/desertion"),
            ],
        }],
    },
    {
        "id": "SYN_093_MCODE_ADV_SAC-HOP",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "SAC-HOP",
        "n_distractors": 2,
        "turns": [
            {"speaker": "I", "text": "how would you sum up where you are in life"},
            {"speaker": "S", "text": "i'm a complete waste of space who destroyed everything good in my life and i know deep down that nothing will ever get better because people like me don't deserve good things i'm not even worth the air i breathe ha but i still go to the coffee shop down the street the barista knows my order"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Adversarial: dense SAC.C.b2 + HOP.3b + SAC.C.a3. Multiple dual-coded themes in one utterance.",
            "codings": [
                _c("i'm a complete waste of space", "SAC", "SAC.C.b2", "self", 3, "Considering self worthless"),
                _c("who destroyed everything good in my life", "SAC", "SAC.C.b3", "self", 2, "Self-criticism — self as cause of destruction"),
                _c("nothing will ever get better", "HOP", "HOP.3b", "self", 1, "Pessimism/hopelessness"),
                _c("people like me don't deserve good things", "SAC", "SAC.C.a3", "self", 2, "Not deserving good — needing punishment"),
                _c("i'm not even worth the air i breathe", "SAC", "SAC.C.b2", "self", 3, "Self as worthless"),
            ],
        }],
    },
    {
        "id": "SYN_094_MCODE_ADV_HOS-DAM",
        "type": "MCODE", "difficulty": "ADV", "primary_subscale": "HOS-DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "was there ever a time you felt really scared"},
            {"speaker": "S", "text": "this man he pulled a knife on someone right in front of me and slashed him across the face the blood was everywhere and the guy collapsed and i thought he was going to die right there i take the subway"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.a1 (knife attack) + DAM.B.b (slashed/blood) + DAM.A.b (thought he'd die).",
            "codings": [
                _c("this man he pulled a knife on someone", "HOS", "HOS.B.a1", "others", 3, "Others threatening to injure"),
                _c("slashed him across the face", "DAM", "DAM.B.b", "others", 2, "Injury/tissue damage — others"),
                _c("the blood was everywhere", "DAM", "DAM.B.b", "others", 2, "Tissue damage — bleeding"),
                _c("i thought he was going to die right there", "DAM", "DAM.A.b", "others", 2, "Threat of death — others"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 4: DISTRACTOR-HEAVY (15 instances) — 1-2 codable, 3-5 distractors
# ===================================================================

DISTRACTOR_HEAVY = [
    {
        "id": "SYN_095_DIST_MOD_HOP",
        "type": "DIST", "difficulty": "MOD", "primary_subscale": "HOP",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "how's your week been"},
            {"speaker": "S", "text": "pretty normal i went to the store got some groceries the weather was nice i walked the dog and then at night i just thought nothing is ever going to work out for me but besides that fine really just had spaghetti for dinner"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "One HOP.3b buried in neutral content. 4 distractors.",
            "codings": [
                _c("nothing is ever going to work out for me", "HOP", "HOP.3b", "self", 1, "Pessimism/hopelessness"),
            ],
        }],
    },
    {
        "id": "SYN_096_DIST_MOD_SAC",
        "type": "DIST", "difficulty": "MOD", "primary_subscale": "SAC",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "tell me about your day"},
            {"speaker": "S", "text": "woke up had coffee drove to work sat through meetings came home made dinner watched tv and just before bed i thought i'm such a terrible person for what i did to them then i fell asleep the sheets are new they're nice"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "One SAC.C.b2 buried in routine. 4 distractors.",
            "codings": [
                _c("i'm such a terrible person for what i did to them", "SAC", "SAC.C.b2", "self", 3, "Self-worthlessness/blame"),
            ],
        }],
    },
    {
        "id": "SYN_097_DIST_MOD_SEP",
        "type": "DIST", "difficulty": "MOD", "primary_subscale": "SEP",
        "n_distractors": 3,
        "turns": [
            {"speaker": "I", "text": "how are things at home"},
            {"speaker": "S", "text": "the house is clean the kids are doing well in school my husband got a promotion and we're thinking about getting a pool but i still miss my mom who passed and i feel alone without her we had tacos last night"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.a buried in positive content. 3 distractors.",
            "codings": [
                _c("i still miss my mom who passed", "SEP", "SEP.a", "self", 3, "Loss of love object"),
                _c("i feel alone without her", "SEP", "SEP.a", "self", 3, "Loneliness from loss"),
            ],
        }],
    },
    {
        "id": "SYN_098_DIST_MOD_DAM",
        "type": "DIST", "difficulty": "MOD", "primary_subscale": "DAM",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "anything eventful happen recently"},
            {"speaker": "S", "text": "not really went to the grocery store saw a movie it was okay played some basketball and oh yeah my neighbor's dog got hit by a car died right there on the road that was sad but otherwise pretty normal week we had barbecue on sunday"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.b buried in mundane events. 4 distractors.",
            "codings": [
                _c("my neighbor's dog got hit by a car died right there", "DAM", "DAM.A.b", "others", 2, "Death of animate other"),
            ],
        }],
    },
    {
        "id": "SYN_099_DIST_MOD_HOS",
        "type": "DIST", "difficulty": "MOD", "primary_subscale": "HOS",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "how do you spend your evenings"},
            {"speaker": "S", "text": "usually just relax watch tv maybe cook something nice read a book and sometimes i'll call my sister but last tuesday i told my coworker he's a complete moron and i meant it then i went to bed we have a nice patio"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.c1 buried in pleasant routine. 4 distractors.",
            "codings": [
                _c("i told my coworker he's a complete moron", "HOS", "HOS.A.c1", "self", 3, "Self adversely criticizing another human"),
            ],
        }],
    },
    {
        "id": "SYN_100_DIST_HARD_HOP",
        "type": "DIST", "difficulty": "HARD", "primary_subscale": "HOP",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "what have you been up to"},
            {"speaker": "S", "text": "oh you know the usual stuff working out eating right seeing friends went to a concert last week that was great and my sister visited but deep down i've just given up on things ever getting better um i also started a new book it's a mystery"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOP.3b hedged amid heavily positive content. Hard: high positive-to-negative ratio.",
            "codings": [
                _c("deep down i've just given up on things ever getting better", "HOP", "HOP.3b", "self", 1, "Hopelessness despite hedging"),
            ],
        }],
    },
    {
        "id": "SYN_101_DIST_HARD_SAC",
        "type": "DIST", "difficulty": "HARD", "primary_subscale": "SAC",
        "n_distractors": 5,
        "turns": [
            {"speaker": "I", "text": "how would you describe yourself"},
            {"speaker": "S", "text": "i'm pretty outgoing i like meeting people i'm good at my job i volunteer on weekends i have great friends but underneath all of that i feel like a fraud i'm ashamed of who i really am inside the weather has been warm lately and i've been swimming"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.B.a (shame) amid self-positive statements. 5 distractors.",
            "codings": [
                _c("i feel like a fraud", "SAC", "SAC.B.a", "self", 3, "Shame/humiliation — imposter"),
                _c("i'm ashamed of who i really am inside", "SAC", "SAC.B.a", "self", 3, "Shame attributed to self"),
            ],
        }],
    },
    {
        "id": "SYN_102_DIST_HARD_SOM",
        "type": "DIST", "difficulty": "HARD", "primary_subscale": "SOM",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "how's life treating you"},
            {"speaker": "S", "text": "great actually my marriage is strong kids are happy i got a raise we're going to hawaii next month but my stomach has been really bad lately and i can't keep food down other than that life is wonderful really i play tennis twice a week"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SOM.D amid very positive content. Hard: mostly-positive interview.",
            "codings": [
                _c("my stomach has been really bad lately", "SOM", "SOM.D", "self", 1, "GI disturbance"),
                _c("i can't keep food down", "SOM", "SOM.D", "self", 1, "GI disturbance — vomiting"),
            ],
        }],
    },
    {
        "id": "SYN_103_DIST_HARD_HOS",
        "type": "DIST", "difficulty": "HARD", "primary_subscale": "HOS",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "tell me about the people in your life"},
            {"speaker": "S", "text": "my wife is amazing my kids are wonderful my parents are supportive my best friend is always there for me but i really despise my sister's husband he's a manipulative cruel person who mistreats her i went to the beach last weekend and we're remodeling the kitchen"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.A.c1 + HOS.B.b1 amid positive relationship statements. 4 distractors.",
            "codings": [
                _c("i really despise my sister's husband", "HOS", "HOS.A.c1", "self", 3, "Self expressing dislike of another human"),
                _c("he's a manipulative cruel person who mistreats her", "HOS", "HOS.B.b1", "others", 3, "Others causing suffering to others"),
            ],
        }],
    },
    {
        "id": "SYN_104_DIST_HARD_PMR",
        "type": "DIST", "difficulty": "HARD", "primary_subscale": "PMR",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "how's everything going"},
            {"speaker": "S", "text": "pretty well i went hiking last weekend saw some friends had a nice dinner the office is busy but manageable only thing is this weird feeling like my brain is running at quarter speed like everything in my head is in slow motion but physically i'm fine i had a checkup it's all good"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "PMR.1 amid active/positive content. 4 distractors. Hard: isolated PMR in healthy context.",
            "codings": [
                _c("my brain is running at quarter speed", "PMR", "PMR.1", "self", 1, "Cognitive retardation"),
                _c("everything in my head is in slow motion", "PMR", "PMR.1", "self", 1, "General retardation in thinking"),
            ],
        }],
    },
    {
        "id": "SYN_105_DIST_ADV_NULL",
        "type": "DIST", "difficulty": "ADV", "primary_subscale": "NULL",
        "n_distractors": 5,
        "turns": [
            {"speaker": "I", "text": "how are you doing"},
            {"speaker": "S", "text": "oh man that meeting killed me today i was dying of boredom in there my heart was broken when my team lost the game yesterday i'm killing it at work though and i hit rock bottom on that video game level the traffic was murder getting home"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "ALL idioms — none codable. 'killed me' 'dying of boredom' 'heart broken (sports)' 'killing it' 'rock bottom (game)' 'murder (traffic)'. Zero codings.",
            "codings": [],
        }],
    },
    {
        "id": "SYN_106_DIST_ADV_HOP",
        "type": "DIST", "difficulty": "ADV", "primary_subscale": "HOP",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "what's on your mind"},
            {"speaker": "S", "text": "i'm dead tired today the test results were murder to study for i could kill for a good pizza right now i was dying laughing at that show last night but honestly underneath it all i've lost hope that anything will improve for me we have a cat named whiskers"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "One real HOP.3b amid 4 idioms. Adversarial: must distinguish literal from figurative.",
            "codings": [
                _c("i've lost hope that anything will improve for me", "HOP", "HOP.3b", "self", 1, "Loss of hope — genuine hopelessness"),
            ],
        }],
    },
    {
        "id": "SYN_107_DIST_ADV_DAM",
        "type": "DIST", "difficulty": "ADV", "primary_subscale": "DAM",
        "n_distractors": 4,
        "turns": [
            {"speaker": "I", "text": "tell me about your week"},
            {"speaker": "S", "text": "oh that kills me when people say that ha no but um i almost died laughing at this comedy show and my friend said the exam was murder but actually my aunt she's really sick they think she might not make it she could really die from this the pizza place on fifth is great"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Genuine DAM.A.b (aunt might die) amid idioms. Adversarial: 3 death idioms + 1 real.",
            "codings": [
                _c("she's really sick they think she might not make it", "DAM", "DAM.A.b", "others", 2, "Threat of death — others"),
                _c("she could really die from this", "DAM", "DAM.A.b", "others", 2, "Death anxiety for others"),
            ],
        }],
    },
    {
        "id": "SYN_108_DIST_ADV_SAC",
        "type": "DIST", "difficulty": "ADV", "primary_subscale": "SAC",
        "n_distractors": 3,
        "turns": [
            {"speaker": "I", "text": "how do you feel about how things are going"},
            {"speaker": "S", "text": "i beat myself up over that game ha not literally obviously and i'm my own worst critic when it comes to cooking my soufflé collapsed but for real though i genuinely hate myself for how i treated my ex i'm a terrible person um i play chess online"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b2 (genuine self-hate) amid idiomatic self-criticism (cooking). Adversarial: distinguish casual from clinical self-blame.",
            "codings": [
                _c("i genuinely hate myself for how i treated my ex", "SAC", "SAC.C.b2", "self", 3, "Self-blame/self-hatred — genuine"),
                _c("i'm a terrible person", "SAC", "SAC.C.b2", "self", 3, "Considering self worthless"),
            ],
        }],
    },
    {
        "id": "SYN_109_DIST_ADV_HOS",
        "type": "DIST", "difficulty": "ADV", "primary_subscale": "HOS",
        "n_distractors": 3,
        "turns": [
            {"speaker": "I", "text": "how do you handle conflict"},
            {"speaker": "S", "text": "oh i could have killed him when he ate my leftovers ha and my friend she was killing it at karaoke the crowd was dying laughing but honestly i really do want to hurt my neighbor for what he did to my property he destroyed my fence on purpose i ride my bike to work"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Genuine HOS.A.a1 + HOS.B.a3 amid idioms. Adversarial: 'could have killed' = idiom but 'want to hurt' = genuine.",
            "codings": [
                _c("i really do want to hurt my neighbor", "HOS", "HOS.A.a1", "self", 3, "Self threatening to injure another"),
                _c("he destroyed my fence on purpose", "HOS", "HOS.B.a3", "others", 1, "Inanimate objects destroyed"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 5: DENIAL-FOCUSED (10 instances)
# ===================================================================

DENIAL_FOCUSED = [
    {
        "id": "SYN_110_DENY_MOD_SAC",
        "type": "DENY", "difficulty": "MOD", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you ever feel guilty about anything"},
            {"speaker": "S", "text": "i don't feel guilty about it at all and i'm not embarrassed by what happened i'm genuinely at peace with my decisions i enjoy cooking on weekends"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.c (denial of guilt) + SAC.B.c (denial of embarrassment). 'at peace' = genuine positive NOT coded. Distractor: cooking.",
            "codings": [
                _c("i don't feel guilty about it at all", "SAC", "SAC.A.c", "denial", 1, "Denial of guilt"),
                _c("i'm not embarrassed by what happened", "SAC", "SAC.B.c", "denial", 1, "Denial of shame/embarrassment"),
            ],
        }],
    },
    {
        "id": "SYN_111_DENY_MOD_DAM",
        "type": "DENY", "difficulty": "MOD", "primary_subscale": "DAM",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "are you afraid of dying"},
            {"speaker": "S", "text": "no i'm not afraid of dying it doesn't bother me at all and i'm not hurt by what happened physically i'm perfectly healthy i like going to the movies"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.d (denial of death anxiety) + DAM.B.d (denial of injury). 'perfectly healthy' = genuine positive NOT coded.",
            "codings": [
                _c("i'm not afraid of dying it doesn't bother me at all", "DAM", "DAM.A.d", "denial", 1, "Denial of death anxiety"),
                _c("i'm not hurt by what happened physically", "DAM", "DAM.B.d", "denial", 1, "Denial of injury"),
            ],
        }],
    },
    {
        "id": "SYN_112_DENY_MOD_SEP",
        "type": "DENY", "difficulty": "MOD", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you ever feel lonely"},
            {"speaker": "S", "text": "i'm not lonely at all and i don't miss her not one bit i'm perfectly happy on my own i have lots of hobbies i really enjoy my life as it is right now"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.d (denial of loneliness + denial of missing). 'happy on my own' + 'enjoy my life' = genuine positives NOT coded.",
            "codings": [
                _c("i'm not lonely at all", "SEP", "SEP.d", "denial", 1, "Denial of loneliness/separation"),
                _c("i don't miss her not one bit", "SEP", "SEP.d", "denial", 1, "Denial of missing loved one"),
            ],
        }],
    },
    {
        "id": "SYN_113_DENY_HARD_HOS",
        "type": "DENY", "difficulty": "HARD", "primary_subscale": "HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "do you ever get angry at people"},
            {"speaker": "S", "text": "i'm not angry at anyone not really and i don't hate anybody i don't have any hostile feelings toward anyone i genuinely care about the people in my life we play board games together"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "HOS.B.f3 × 3 (denial of anger/hate/hostility). 'genuinely care' = positive NOT coded. Hard: triple denial.",
            "codings": [
                _c("i'm not angry at anyone", "HOS", "HOS.B.f3", "denial", 1, "Denial of anger"),
                _c("i don't hate anybody", "HOS", "HOS.B.f3", "denial", 1, "Denial of hatred"),
                _c("i don't have any hostile feelings toward anyone", "HOS", "HOS.B.f3", "denial", 1, "Denial of hostility/intent to harm"),
            ],
        }],
    },
    {
        "id": "SYN_114_DENY_HARD_SAC",
        "type": "DENY", "difficulty": "HARD", "primary_subscale": "SAC",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how do you feel about yourself"},
            {"speaker": "S", "text": "i don't hate myself no not at all and i'm not disappointed in who i am i think i'm a good person actually i like who i've become i volunteer at the shelter"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.C.b4 (denial of self-hatred) + SAC.C.a4 (denial of disappointment). 'good person' + 'like who I've become' = genuine positives NOT coded.",
            "codings": [
                _c("i don't hate myself no not at all", "SAC", "SAC.C.b4", "denial", 1, "Denial of self-hatred"),
                _c("i'm not disappointed in who i am", "SAC", "SAC.C.a4", "denial", 1, "Denial of self-disappointment — still references the construct"),
            ],
        }],
    },
    {
        "id": "SYN_115_DENY_HARD_DAM",
        "type": "DENY", "difficulty": "HARD", "primary_subscale": "DAM",
        "n_distractors": 0,
        "turns": [
            {"speaker": "I", "text": "how do you feel about mortality"},
            {"speaker": "S", "text": "death doesn't scare me i'm not afraid of it at all and the injuries from the accident they don't bother me i'm not in pain i'm not worried about dying from anything"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.d × 2 (denial of death fear) + DAM.B.d (denial of injury concern). Hard: all denial, no positive foils.",
            "codings": [
                _c("death doesn't scare me i'm not afraid of it at all", "DAM", "DAM.A.d", "denial", 1, "Denial of death anxiety"),
                _c("the injuries from the accident they don't bother me i'm not in pain", "DAM", "DAM.B.d", "denial", 1, "Denial of injury/pain"),
                _c("i'm not worried about dying from anything", "DAM", "DAM.A.d", "denial", 1, "Denial of death anxiety"),
            ],
        }],
    },
    {
        "id": "SYN_116_DENY_HARD_SEP",
        "type": "DENY", "difficulty": "HARD", "primary_subscale": "SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how did you handle the breakup"},
            {"speaker": "S", "text": "honestly i'm not lonely without her and i don't miss the relationship at all the separation doesn't bother me one bit i'm thriving actually i started a new hobby painting"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SEP.d × 3 (denial of loneliness, missing, separation distress). 'thriving' = genuine positive NOT coded.",
            "codings": [
                _c("i'm not lonely without her", "SEP", "SEP.d", "denial", 1, "Denial of loneliness"),
                _c("i don't miss the relationship at all", "SEP", "SEP.d", "denial", 1, "Denial of missing loved one"),
                _c("the separation doesn't bother me one bit", "SEP", "SEP.d", "denial", 1, "Denial of separation distress"),
            ],
        }],
    },
    {
        "id": "SYN_117_DENY_ADV_MIXED",
        "type": "DENY", "difficulty": "ADV", "primary_subscale": "MIXED",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "how are you dealing with everything"},
            {"speaker": "S", "text": "i'm fine really i'm not guilty about any of it and i'm not afraid of dying and i'm not lonely and i'm not angry at anyone i feel great actually life is good i go jogging every morning"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "Adversarial: stacked denials across scales. SAC.A.c + DAM.A.d + SEP.d + HOS.B.f3. 'feel great/life is good' = positive NOT coded.",
            "codings": [
                _c("i'm not guilty about any of it", "SAC", "SAC.A.c", "denial", 1, "Denial of guilt"),
                _c("i'm not afraid of dying", "DAM", "DAM.A.d", "denial", 1, "Denial of death anxiety"),
                _c("i'm not lonely", "SEP", "SEP.d", "denial", 1, "Denial of loneliness"),
                _c("i'm not angry at anyone", "HOS", "HOS.B.f3", "denial", 1, "Denial of anger"),
            ],
        }],
    },
    {
        "id": "SYN_118_DENY_ADV_SAC-HOS",
        "type": "DENY", "difficulty": "ADV", "primary_subscale": "SAC-HOS",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "some people feel angry at themselves or others do you"},
            {"speaker": "S", "text": "no i don't blame myself for anything and i don't resent anyone either i'm not ashamed and i certainly don't want to hurt anyone including myself i'm at peace i truly am my garden is beautiful this time of year"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "SAC.A.c (no blame) + HOS.B.f3 (no resentment/no hurting) + SAC.B.c (not ashamed) + SAC.C.b4 (not hurt self). 'at peace' = genuine.",
            "codings": [
                _c("i don't blame myself for anything", "SAC", "SAC.A.c", "denial", 1, "Denial of guilt/self-blame"),
                _c("i don't resent anyone", "HOS", "HOS.B.f3", "denial", 1, "Denial of resentment/hostility"),
                _c("i'm not ashamed", "SAC", "SAC.B.c", "denial", 1, "Denial of shame"),
                _c("i certainly don't want to hurt anyone including myself", "SAC", "SAC.C.b4", "denial", 1, "Denial of self-directed destructive impulses"),
            ],
        }],
    },
    {
        "id": "SYN_119_DENY_ADV_DAM-SEP",
        "type": "DENY", "difficulty": "ADV", "primary_subscale": "DAM-SEP",
        "n_distractors": 1,
        "turns": [
            {"speaker": "I", "text": "after everything that happened how do you feel"},
            {"speaker": "S", "text": "i'm not scared of death not one bit and i'm not hurt from the accident anymore and i don't feel abandoned by my family i'm not missing anyone i've made my peace with all of it the sunset last night was gorgeous"},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": "DAM.A.d + DAM.B.d + SEP.d × 2. 'made peace' = genuine. Adversarial: all denial, cross-scale.",
            "codings": [
                _c("i'm not scared of death not one bit", "DAM", "DAM.A.d", "denial", 1, "Denial of death anxiety"),
                _c("i'm not hurt from the accident anymore", "DAM", "DAM.B.d", "denial", 1, "Denial of injury"),
                _c("i don't feel abandoned by my family", "SEP", "SEP.d", "denial", 1, "Denial of abandonment"),
                _c("i'm not missing anyone", "SEP", "SEP.d", "denial", 1, "Denial of missing loved ones"),
            ],
        }],
    },
]


# ===================================================================
# BATCH 6: TRUE-NEGATIVE (31 instances) — zero codings expected
# ===================================================================

def _neg(syn_id, difficulty, category, question, answer, n_distractors=3):
    """Shorthand for true-negative instance."""
    return {
        "id": syn_id,
        "type": "NEG", "difficulty": difficulty, "primary_subscale": "NULL",
        "n_distractors": n_distractors,
        "turns": [
            {"speaker": "I", "text": question},
            {"speaker": "S", "text": answer},
        ],
        "ground_truth": [{
            "fragment": 1,
            "rationale": f"True negative — {category}. No depressive content.",
            "codings": [],
        }],
    }

TRUE_NEGATIVE = [
    # Neutral factual (5)
    _neg("SYN_120_NEG_EASY_NULL", "EASY", "neutral factual — origins",
         "where are you from originally",
         "i'm from phoenix arizona born and raised there my parents still live there i went to arizona state"),
    _neg("SYN_121_NEG_EASY_NULL", "EASY", "neutral factual — job",
         "what do you do for work",
         "i'm an accountant at a mid-size firm i do tax preparation mostly some auditing been there about five years"),
    _neg("SYN_122_NEG_EASY_NULL", "EASY", "neutral factual — routine",
         "walk me through your typical day",
         "i wake up at six thirty shower have breakfast drive to work come home around five make dinner watch some tv go to bed around ten"),
    _neg("SYN_123_NEG_MOD_NULL", "MOD", "neutral factual — education",
         "tell me about your education",
         "i studied engineering at state college graduated in two thousand fifteen did an internship at a tech company then got hired full time"),
    _neg("SYN_124_NEG_MOD_NULL", "MOD", "neutral factual — travel",
         "do you travel much",
         "yeah we went to italy last summer saw rome and florence the food was incredible and the architecture is amazing we're planning japan next year"),
    # Positive affect (5)
    _neg("SYN_125_NEG_EASY_NULL", "EASY", "positive affect — hobbies",
         "what do you enjoy doing",
         "i love hiking and photography i go out every weekend to take pictures of nature it's really relaxing and fulfilling"),
    _neg("SYN_126_NEG_EASY_NULL", "EASY", "positive affect — accomplishments",
         "what are you most proud of",
         "finishing my degree while working full time that was hard but i did it and i'm really proud of myself my family was so supportive"),
    _neg("SYN_127_NEG_MOD_NULL", "MOD", "positive affect — gratitude",
         "what makes you happy",
         "my kids honestly watching them grow up and learn new things i feel so grateful for my family we have game nights every friday"),
    _neg("SYN_128_NEG_MOD_NULL", "MOD", "positive affect — achievement",
         "tell me about something good that happened recently",
         "i got promoted last month and my wife threw me a surprise party all our friends came it was the best night i've had in years"),
    _neg("SYN_129_NEG_MOD_NULL", "MOD", "positive affect — contentment",
         "how would you describe your life right now",
         "honestly pretty good i have a stable job great relationship my health is fine i've been exercising more and eating better things are going well"),
    # Everyday complaints (5)
    _neg("SYN_130_NEG_MOD_NULL", "MOD", "everyday complaints — traffic",
         "what annoys you about daily life",
         "the traffic is insane it takes me an hour to get to work when it should be twenty minutes and parking is impossible downtown"),
    _neg("SYN_131_NEG_MOD_NULL", "MOD", "everyday complaints — weather",
         "how do you feel about living here",
         "it's fine but the winters are brutal too much rain and the gray skies get old but summer makes up for it i like the beach"),
    _neg("SYN_132_NEG_HARD_NULL", "HARD", "everyday complaints — inconvenience",
         "what's been frustrating lately",
         "my car broke down last week and the mechanic took forever to fix it and it cost way more than i expected plus my internet has been spotty"),
    _neg("SYN_133_NEG_HARD_NULL", "HARD", "everyday complaints — work stress",
         "how's work been",
         "busy really busy we have this big deadline coming up and my boss keeps adding things to my plate but i'm managing it fine just need more hours in the day"),
    _neg("SYN_134_NEG_HARD_NULL", "HARD", "everyday complaints — neighbor noise",
         "is there anything that's been bothering you",
         "my neighbor plays loud music at night and the garbage truck comes at six am and wakes me up and the construction next door is noisy but it's temporary"),
    # Health discussion no complaint (4)
    _neg("SYN_135_NEG_MOD_NULL", "MOD", "health — exercise",
         "tell me about your health habits",
         "i run three times a week and do yoga on weekends i eat mostly vegetables and fish i had a checkup last month everything looked good"),
    _neg("SYN_136_NEG_HARD_NULL", "HARD", "health — recovery",
         "have you had any health issues",
         "i had a cold last month but it cleared up fine and i twisted my ankle jogging but it healed quickly i'm back to running now feeling strong"),
    _neg("SYN_137_NEG_HARD_NULL", "HARD", "health — diet",
         "how do you take care of yourself",
         "i've been focusing on nutrition eating more whole foods cutting back on sugar and processed stuff i meal prep on sundays it saves time during the week"),
    _neg("SYN_138_NEG_HARD_NULL", "HARD", "health — sleep positive",
         "how's your sleep been",
         "actually really good i started a bedtime routine and it's made a huge difference i'm getting seven to eight hours now and i wake up feeling refreshed"),
    # Relationship discussion no loss (4)
    _neg("SYN_139_NEG_MOD_NULL", "MOD", "relationships — family activities",
         "tell me about your family",
         "we're really close my wife and i take the kids to the park every weekend and we do family dinners on sundays my parents come over sometimes"),
    _neg("SYN_140_NEG_HARD_NULL", "HARD", "relationships — friendships",
         "do you have a good support system",
         "yeah my best friend and i have been close since college we talk every week and my sister lives nearby we help each other with the kids"),
    _neg("SYN_141_NEG_HARD_NULL", "HARD", "relationships — social events",
         "how's your social life",
         "pretty active we had a barbecue last weekend with the neighbors and i play in a softball league on thursdays my book club meets monthly"),
    _neg("SYN_142_NEG_HARD_NULL", "HARD", "relationships — partner positive",
         "how's your relationship",
         "really good actually we've been together eight years and we still make time for date nights communication has gotten better over time too"),
    # Near-miss emotional (4)
    _neg("SYN_143_NEG_HARD_NULL", "HARD", "near-miss — frustration resolved",
         "have you been stressed lately",
         "i was really frustrated with my project at work but i talked to my manager and we worked it out i was worried for a bit but it turned out fine"),
    _neg("SYN_144_NEG_HARD_NULL", "HARD", "near-miss — worry resolved",
         "what have you been worried about",
         "i was anxious about my daughter's test results but they came back normal and i was concerned about finances but we figured out a budget"),
    _neg("SYN_145_NEG_ADV_NULL", "ADV", "near-miss — sadness without depression",
         "have you felt sad recently",
         "yeah i was sad when my friend moved to another city but i'm happy for her it's a great opportunity and we video chat every week so it's fine"),
    _neg("SYN_146_NEG_ADV_NULL", "ADV", "near-miss — anger resolved",
         "do you ever get angry",
         "sure i was mad when my coworker took credit for my work but i addressed it directly and he apologized i don't hold grudges life's too short"),
    # Idiom-heavy (4)
    _neg("SYN_147_NEG_ADV_NULL", "ADV", "idiom-heavy — sports metaphors",
         "how's work going",
         "oh man i'm killing it at work right now knocked it out of the park on that presentation my boss was blown away i'm on fire lately"),
    _neg("SYN_148_NEG_ADV_NULL", "ADV", "idiom-heavy — food expressions",
         "what's been going on",
         "just the usual grind the morning commute is murder but i survived ha and this project is eating me alive but i'll get through it piece of cake"),
    _neg("SYN_149_NEG_ADV_NULL", "ADV", "idiom-heavy — mixed death metaphors",
         "tell me about your week",
         "oh that exam nearly killed me and i was dying to see that new movie it was to die for honestly i'm dead serious when i say it was amazing"),
    _neg("SYN_150_NEG_ADV_NULL", "ADV", "idiom-heavy — emotional vocabulary",
         "how are you feeling",
         "i'm dead tired from the gym but in a good way and i crushed my personal record my heart was pounding like crazy but that's just the workout high"),
]


# ===================================================================
# ASSEMBLY — ALL_INSTANCES
# ===================================================================

ALL_INSTANCES = (
    PURE_HOP
    + PURE_SAC
    + PURE_PMR
    + PURE_SOM
    + PURE_DAM
    + PURE_SEP
    + PURE_HOS
    + MULTI_SUBSCALE
    + MULTI_CODE
    + DISTRACTOR_HEAVY
    + DENIAL_FOCUSED
    + TRUE_NEGATIVE
)
