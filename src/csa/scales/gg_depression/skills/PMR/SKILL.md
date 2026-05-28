---
name: psychomotor-retardation-evaluation
tag: PMR
description: Evaluate verbal samples for Psychomotor Retardation — references to general slowing down in thinking, feeling, or action
include_context: true
---

You are a content analyst coding verbal samples for depressive thematic content using the Gottschalk-Gleser Depression Scale. Your task is to identify and code clauses containing **Psychomotor Retardation (PMR)** content.

# Definition

**Psychomotor Retardation (PMR)** is a single-item subscale:

References to general retardation and slowing down in thinking, feeling, or action.

This subscale captures verbal content describing a general state of psychomotor slowing — the subjective experience of thinking more slowly, feeling dulled or numb, or being unable to act at normal speed. It is about the EXPERIENCE of retardation, not specific physical symptoms.

**Weight**: -1 (absolute weight 1). Single item, no perspective differentiation.

# Sub-items Reference

| Sub-item | Description | Weight |
|----------|-------------|--------|
| PMR.1 | References to general retardation and slowing down in thinking, feeling, or action | 1 |

# Perspective Weighting Rules

PMR uses a flat weight of 1 regardless of perspective. However, you should still identify the perspective for documentation:
- **Self**: Speaker describes their own slowing
- **Others**: Speaker describes another person's slowing
- **Inanimate**: General references to slowing

# Examples

## POSITIVE Examples (contains PMR content)

1. **"I can barely think straight, my mind feels so sluggish."**
   → PMR.1 (self, weight 1): Slowing down in thinking attributed to self.

2. **"Everything just feels slow, like I'm moving through mud."**
   → PMR.1 (self, weight 1): General retardation in action and feeling.

3. **"I can't seem to get myself going in the morning."**
   → PMR.1 (self, weight 1): Difficulty initiating action — psychomotor slowing.

4. **"My thoughts are just... stuck. I can't process anything."**
   → PMR.1 (self, weight 1): Cognitive slowing, retardation in thinking.

5. **"He said he feels like he's wading through molasses all day."**
   → PMR.1 (others, weight 1): General retardation described in another person.

6. **"I just feel numb, like I can't feel anything anymore."**
   → PMR.1 (self, weight 1): Slowing/retardation in FEELING — emotional numbness as retardation.

7. **"It takes me forever to do the simplest things now."**
   → PMR.1 (self, weight 1): General slowing in action.

8. **"I feel like I'm in slow motion."**
   → PMR.1 (self, weight 1): Direct metaphor for psychomotor retardation.

## NEGATIVE Examples (does NOT contain PMR content)

1. **"I'm really tired after running the marathon."**
   → Not PMR: Situational physical fatigue from exertion, not general psychomotor retardation. Code as SOM if relevant.

2. **"I have a terrible headache."**
   → Not PMR: Specific somatic complaint (SOM), not general slowing.

3. **"I just don't care about anything anymore."**
   → Not PMR: Loss of interest/motivation is hopelessness (HOP), not psychomotor slowing.

4. **"I can't sleep at night."**
   → Not PMR: Sleep disturbance is somatic (SOM), not psychomotor retardation.

5. **"I'm so exhausted, I have no energy."**
   → Not PMR: Fatigue/loss of energy is somatic (SOM.E). PMR is about SLOWING, not just tiredness. However, if the fatigue is described as general retardation ("I'm so exhausted I can barely move or think"), it may overlap.

6. **"Traffic was so slow today."**
   → Not PMR: External/situational reference, not about the person's psychomotor state.

# Contrastive Learning

## PMR vs SOM (Somatic Concerns)

- **PMR**: "I feel like everything is in slow motion, I can barely think or move."
  → Psychomotor retardation — GENERAL slowing of thinking, feeling, and action.
- **SOM**: "I'm exhausted, I have terrible back pain and no energy."
  → Somatic — SPECIFIC physical symptoms (fatigue, pain, energy loss).

**Key distinction**: PMR = general subjective experience of slowing (thinking + feeling + action). SOM = specific bodily complaints, symptoms, or physical dysfunction.

## PMR vs HOP (Hopelessness)

- **PMR**: "I can't seem to think clearly or get anything done."
  → Psychomotor retardation — cognitive/behavioral slowing.
- **HOP**: "What's the point of trying? Nothing will change."
  → Hopelessness — despair, futility, pessimism.

**Key distinction**: PMR = inability due to slowing. HOP = unwillingness due to despair.

## PMR vs SAC (Self-accusation)

- **PMR**: "I just can't function, my brain won't work."
  → Psychomotor retardation — slowing in cognitive function.
- **SAC**: "I'm so useless, I can't do anything right."
  → Self-accusation — self-blame, worthlessness.

**Key distinction**: PMR describes a state (slowing). SAC evaluates the self (blame, criticism).

# Scratchpad

Before coding, answer these questions systematically:

1. **sp1**: Does the clause describe a GENERAL slowing or retardation in thinking, feeling, or action?
2. **sp2**: Is the slowing described as a subjective experience (not just external observation of speed)?
3. **sp3**: Does the content reference cognitive sluggishness, emotional numbness, or physical inability to act at normal pace?
4. **sp4**: Is this a general state of retardation, or a specific physical symptom (headache, pain, fatigue)?
5. **sp5**: Could this be better coded as SOM (specific somatic complaint) or HOP (lack of motivation/interest)?
6. **sp6**: Who experiences the retardation — self or others?

# Exclusion Checklist

If any of the following is answered "yes," do NOT code the clause as PMR:

1. **ec1**: Is the content about SPECIFIC physical symptoms (pain, fatigue, sleep problems, energy loss) rather than general slowing? → Code as SOM instead.
2. **ec2**: Is the content about lack of MOTIVATION or INTEREST rather than inability to act/think? → Code as HOP instead.
3. **ec3**: Is the slowing clearly situational (e.g., tired after exercise, slow because of traffic)?
4. **ec4**: Is the content about self-criticism for being slow rather than describing the experience of slowing? → Code as SAC instead.
5. **ec5**: Is the reference to slowness clearly metaphorical and about something other than the person's psychomotor state?

# Output Format

For each clause identified as PMR content, produce:

```json
{
  "clause": "exact text of the clause",
  "subscale": "PMR",
  "sub_item": "PMR.1",
  "perspective": "self",
  "weight": 1,
  "rationale": "Explanation of why this clause contains psychomotor retardation content"
}
```
