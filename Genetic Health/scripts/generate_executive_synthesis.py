#!/usr/bin/env python3
"""
Executive Synthesis Report Generator
Produces a plain-English, high-school-level readable health summary from raw genetic data.
No jargon. No "BS". Every line is earned by the actual data.
"""
from pathlib import Path
from datetime import datetime


def plain_condition_name(raw_trait: str) -> str:
    """Translate ugly ClinVar trait names into plain English."""
    raw = raw_trait.split(';')[0].strip()
    translations = {
        'DUFFY BLOOD GROUP SYSTEM': 'A specific blood type marker',
        'Pseudoxanthoma elasticum': 'A condition that affects your skin, eyes, and blood vessel elasticity (PXE)',
        'Alzheimer disease 2': 'A gene linked to a higher risk of Alzheimer\'s disease in later life (APOE4)',
        'Prostate cancer, hereditary': 'An inherited risk marker for prostate cancer',
        'Diabetes mellitus, noninsulin-dependent': 'A risk marker for Type 2 Diabetes',
        'Inflammatory bowel disease': 'A risk marker for severe gut inflammation (like Crohn\'s Disease)',
        'Spinocerebellar ataxia autosomal recessive': 'A rare inherited condition affecting balance and coordination',
        'Fetal hemoglobin quantitative trait locus': 'A blood trait that is typically harmless',
        'Polyagglutinable erythrocyte syndrome': 'A rare, usually symptom-free blood cell trait',
        'Spina bifida, susceptibility to': 'A genetic marker related to spinal development (relevant for family planning)',
        'Postanesthetic apnea': '⚠️ A risk of having trouble breathing after certain anesthetic drugs used in surgery',
        'Familial cancer of breast': 'An inherited risk marker for breast cancer',
        'Hypertension, essential': 'A genetic tendency toward high blood pressure',
        'Lumbar disc herniation': 'A genetic tendency toward slipped or herniated discs in the lower back',
        'Venous thrombosis': 'A higher-than-average risk of blood clots forming in veins',
        'Epilepsy, childhood absence': 'A genetic marker for a type of seizure condition',
        'Ovarian response to FSH stimulation': 'A marker affecting how the ovaries respond to fertility hormones',
    }
    for key, val in translations.items():
        if key.lower() in raw.lower():
            return val
    # Fallback: clean up common patterns
    cleaned = raw.replace('SUSCEPTIBILITY TO', '').replace(';', '').replace('ASSOCIATION WITH', '').strip()
    return cleaned.title()

def explain_condition(raw_trait: str) -> str:
    """Provide a deeper, layman-friendly explanation for a given condition, focusing on effects and seriousness."""
    raw = raw_trait.split(';')[0].strip().lower()
    
    # Blood & Heart
    if 'duffy' in raw or 'blood group' in raw or 'fetal hemoglobin' in raw or 'erythrocyte' in raw:
        return "**Seriousness: Low.** This is a quirk in how your red blood cells are built. On a day-to-day basis, you won't feel any effects at all—it's essentially harmless. However, it becomes clinically relevant if you ever need a blood transfusion or are planning to have children, as doctors need to match this specific blood architecture to avoid complications."
    if 'hypertension' in raw or 'blood pressure' in raw:
        return "**Seriousness: Moderate to High.** Your blood vessels might naturally be stiffer, or your kidneys might hold onto salt too aggressively. The danger here is that high blood pressure is a 'silent killer'—you won't feel it happening, but it slowly damages your heart, brain, and kidneys over decades. For you, aggressive cardiovascular exercise and watching sodium intake aren't just 'good ideas,' they are mandatory maintenance."
    if 'thrombosis' in raw or 'clot' in raw:
        return "**Seriousness: High.** Your blood has a genetic trigger that makes it clot much faster than normal. While great if you get a cut, this means you are at a dangerously high risk for deep vein thrombosis (DVT)—blood clots forming inside your veins. You could face life-threatening complications if a clot travels to your lungs. You must be hyper-vigilant about moving your legs during long flights, periods of bed rest, or if taking medications like birth control."
    if 'coronary' in raw or 'cardiac' in raw or 'hypertriglyceridemia' in raw:
        return "**Seriousness: High.** This indicates a genetic vulnerability to your heart's plumbing. You are highly susceptible to plaque buildup in your arteries or dangerous levels of fat (triglycerides) floating in your blood. If ignored, this is the classic pathway to early-onset heart attacks or severe cardiovascular disease. A heart-healthy diet (low in processed fats/sugars) and regular blood work are non-negotiable."
    
    # Metabolic & Digestive
    if 'diabetes' in raw:
        return "**Seriousness: High.** Your body's 'engine' struggles to process carbohydrates and sugars efficiently. If you maintain a standard modern diet high in sugar and refined carbs, you are highly susceptible to insulin resistance. The real-world effects? Chronic fatigue, severe weight gain, brain fog, and eventually full-blown Type 2 Diabetes. For you, treating sugar like a toxin rather than a treat is the ultimate biohack for longevity."
    if 'obesity' in raw or 'metabolic' in raw:
        return "**Seriousness: Moderate.** You have a genetic blueprint that leans toward metabolic slow-down and fat storage. From an evolutionary perspective, you are great at surviving famines! In the modern world, it means your body fiercely holds onto fat, making weight loss exceptionally difficult. It requires strict discipline in diet and strength training to override this genetic default."
    if 'bowel' in raw or 'crohn' in raw or 'celiac' in raw:
        return "**Seriousness: Moderate to High.** This points to a severe vulnerability in your gut lining. Your immune system is prone to mistakenly attacking your digestive tract when triggered by certain foods (like gluten) or chronic stress. If triggered, you could face agonizing stomach pain, chronic diarrhea, and severe nutrient malabsorption. Protecting your gut microbiome is your highest priority."
    if 'gilbert' in raw:
        return "**Seriousness: Very Low.** This is a common, practically harmless quirk. Your liver has a slight bottleneck in processing a waste product called bilirubin. The only real-world effect? If you are extremely stressed, sleep-deprived, or fasting, the whites of your eyes or your skin might take on a very mild yellowish tint (jaundice). It looks alarming, but it is completely benign."
        
    # Brain & Nervous
    if 'alzheimer' in raw or 'dementia' in raw:
        return "**Seriousness: Very High.** You carry a genetic marker that makes your brain less efficient at clearing out metabolic 'trash' (amyloid plaques) as you age. If unchecked, this buildup is a leading driver of severe cognitive decline, memory wipe, and Alzheimer's disease. The effects aren't immediate, but the damage compounds over decades. Protecting your deep sleep (when the brain 'washes' itself) and maintaining elite cardiovascular health in your 20s and 30s is your absolute best defense."
    if 'parkinson' in raw or 'ataxia' in raw or 'epilepsy' in raw or 'schizophrenia' in raw:
        return "**Seriousness: High.** This is a marker indicating a neurological vulnerability. It means the intricate electrical and chemical signaling in your brain or nervous system has a weaker defense against degradation. Depending on the exact condition, effects could range from progressive movement and balance issues (tremors) to severe psychological distress. This is a statistical risk factor, meaning extreme care of your neurological health is vital."
        
    # Autoimmune
    if 'hashimoto' in raw or 'thyroid' in raw or 'sclerosis' in raw or 'lupus' in raw or 'autoimmune' in raw:
        return "**Seriousness: Moderate to High.** Your immune system is genetically 'high-strung.' Instead of just attacking viruses, it has a tendency to get confused and wage war on your own body's healthy tissues—like your thyroid gland, nerves, or joints. In real life, this manifests as chronic, crushing fatigue, brain fog, unexplainable joint pain, or sudden weight changes. Keeping systemic inflammation at rock-bottom through diet and aggressive stress reduction is mandatory to keep this sleeping giant asleep."
    if 'sepsis' in raw:
        return "**Seriousness: High.** If you catch a severe bacterial infection, your body is genetically wired to trigger an apocalyptic, life-threatening inflammatory response (sepsis) rather than a measured defense. This means you can never ignore deep cuts, severe fevers, or lingering infections. Prompt medical treatment with antibiotics during severe illness is critical for you."
        
    # Cancer
    if 'cancer' in raw or 'tumor' in raw or 'carcinoma' in raw or 'prostate' in raw or 'breast' in raw:
        return "**Seriousness: High.** You have an inherited gap in your cellular armor against specific types of cancer. It simply means your body's natural defense mechanism for destroying mutated, pre-cancerous cells is statistically weaker than average. While this does *not* mean you will definitely get cancer, it dictates that early, proactive, and frequent medical screenings later in life are an absolute requirement, not an option."
        
    # Bones & Joints
    if 'disc' in raw or 'osteoarthritis' in raw or 'bone' in raw or 'joint' in raw:
        return "**Seriousness: Moderate.** The cartilage in your joints or the shock-absorbing discs in your spine are genetically prone to accelerated wear-and-tear. The real-world effect? If you have poor posture, lift heavy weights with bad form, or do high-impact sports, you are fast-tracking your way to debilitating lower back pain, slipped discs, or early-onset arthritis. Core strength and mobility work are essential for you."
    if 'spina bifida' in raw:
        return "**Seriousness: Varies.** For you personally, this has little day-to-day effect. However, it is a marker related to spinal development in the womb. This is primarily a crucial piece of information for family planning, as it indicates a higher risk of a child's spine not closing properly during pregnancy. High doses of folic acid during pregnancy planning are usually the protocol."
    if 'pseudoxanthoma elasticum' in raw:
        return "**Seriousness: Moderate.** This is a rare anomaly that causes calcium and other minerals to slowly accumulate in the elastic fibers of your body. The effects are mostly physical and visual: it can lead to premature, severe wrinkling and aging of the skin, and eventually, it can cause complications in your eyes (vision loss) and stiffening of your blood vessels."

    # Catch-all
    return "**Seriousness: Varies.** This is a genetic susceptibility marker. While not an immediate diagnosis, it highlights a structural weakness in your biology that is highly vulnerable to aging, poor diet, or environmental stress. Taking proactive, preventative care of your overall health will dramatically reduce the chances of this gene ever 'turning on.'"

def plain_drug_alert(drug: str, gene: str, annotation: str) -> str:
    """Translate a PharmGKB drug annotation into a one-line plain-English warning."""
    drug_clean = drug.split(';')[0].strip()

    # Map known high-risk drugs
    drug_plain = {
        'warfarin': 'Warfarin (a common blood thinner)',
        'fluorouracil': 'Fluorouracil / 5-FU (a chemotherapy drug)',
        'capecitabine': 'Capecitabine (a chemotherapy drug)',
        'simvastatin': 'Simvastatin (a cholesterol-lowering statin)',
        'efavirenz': 'Efavirenz (an HIV antiviral drug)',
        'succinylcholine': 'Succinylcholine (a muscle relaxant used during surgery)',
        'desflurane': 'Anesthetic gases (used to put you to sleep for surgery)',
        'ivacaftor': 'Ivacaftor (a cystic fibrosis drug)',
        'elexacaftor / tezacaftor / ivacaftor': 'Trikafta (a cystic fibrosis drug combo)',
        'interferons': 'Interferon drugs (used to treat Hepatitis C)',
        'peginterferon alfa-2a': 'Peginterferon (used to treat Hepatitis C)',
        'boceprevir': 'Boceprevir (a Hepatitis C drug)',
        'risperidone': 'Risperidone (an antipsychotic drug)',
        'antipsychotics': 'Antipsychotic medications',
        'antidepressants': 'Antidepressant medications',
        'paroxetine': 'Paroxetine / Paxil (an antidepressant)',
        'atorvastatin': 'Atorvastatin / Lipitor (a cholesterol drug)',
        'tacrolimus': 'Tacrolimus (an organ transplant anti-rejection drug)',
        'cetuximab': 'Cetuximab (a cancer immunotherapy drug)',
        'cisplatin': 'Cisplatin (a chemotherapy drug)',
        'rosiglitazone': 'Rosiglitazone (a diabetes drug)',
    }

    friendly_drug = None
    for key, val in drug_plain.items():
        if key.lower() in drug_clean.lower():
            friendly_drug = val
            break

    if not friendly_drug:
        friendly_drug = f"`{drug_clean}`"

    # Determine impact from annotation
    if 'toxicity' in annotation.lower() or 'bleeding' in annotation.lower() or 'fatal' in annotation.lower():
        impact = "⚠️ You may have a **higher risk of side effects or toxicity**"
    elif 'dosage' in annotation.lower() or 'dose' in annotation.lower():
        impact = "💊 Your doctor may need to **adjust the standard dose**"
    elif 'efficacy' in annotation.lower() or 'response' in annotation.lower():
        impact = "📉 This drug **may not work as effectively** for you"
    elif 'no altered risk' in annotation.lower() or 'not clinically actionable' in annotation.lower():
        return ""  # Skip non-actionable ones
    else:
        impact = "ℹ️ Your genetics may affect how your body responds"

    return f"* **{friendly_drug}** — {impact}. Your gene involved: `{gene}`."


def generate_synthesis_report(health_results: dict, disease_findings: dict, output_path: Path, subject_name: str = None):
    """
    Generates a plain-English, high-school-level readable health synthesis.
    Every section is driven by actual data. No generic copy-paste.
    """
    now = datetime.now().strftime("%B %d, %Y")
    findings_map = {f['gene']: f for f in health_results.get('findings', [])}
    pharmgkb = health_results.get('pharmgkb_findings', [])
    pathogenic = disease_findings.get('pathogenic', []) if disease_findings else []
    likely_pathogenic = disease_findings.get('likely_pathogenic', []) if disease_findings else []
    risk_factors = disease_findings.get('risk_factor', []) if disease_findings else []

    # ==========================================================================
    # SECTION 1: BRAIN & MOOD
    # ==========================================================================
    comt = findings_map.get('COMT')
    bdnf = findings_map.get('BDNF')

    brain_parts = []
    if comt:
        status = comt.get('status', '').lower()
        if 'slow' in status:
            brain_parts.append(
                "**Your brain holds onto stress hormones longer than most people.** "
                "Think of it like a sink that drains slowly. When you get stressed, anxious, or drink coffee, "
                "those feelings linger much longer before clearing out.\n\n"
                "* ✅ **The upside:** When life is calm, you have razor-sharp focus and can think deeply for hours.\n"
                "* ⚠️ **The downside:** Under heavy pressure, stress piles up fast. You are more prone to anxiety and burnout than the average person.\n"
                "* 💊 **What to do:** Before bed, take **Magnesium Glycinate** — it actively helps your body clear out those lingering stress chemicals. "
                "Cut off caffeine strictly before noon, since coffee hits you harder and lasts longer than it does for most people."
            )
        elif 'fast' in status:
            brain_parts.append(
                "**Your brain clears out stress hormones quickly.** "
                "Think of it like a sink that drains very fast — pressure washes away rapidly.\n\n"
                "* ✅ **The upside:** You handle stress, chaos, and high-pressure situations better than most people.\n"
                "* ⚠️ **The downside:** Your motivation can dip in boring or repetitive situations because your brain runs low on the 'feel good' chemical (dopamine).\n"
                "* 💡 **What to do:** You naturally thrive in challenging, high-stimulation work environments."
            )
        else:
            brain_parts.append(
                "Your stress-response system runs in a balanced range — not too high-strung, not too sluggish. "
                "Standard stress management techniques work well for you."
            )

    if bdnf and bdnf.get('magnitude', 0) >= 2:
        brain_parts.append(
            "* **Memory & Learning:** Your brain has a slightly reduced ability to build new connections and memories compared to average. "
            "Exercise (especially cardio) is one of the most powerful ways to counteract this — it directly boosts the chemicals your brain needs to learn."
        )

    brain_section = "\n\n".join(brain_parts) if brain_parts else "No major brain or mood related findings were detected in your DNA."

    # ==========================================================================
    # SECTION 2: FOOD & VITAMINS
    # ==========================================================================
    mthfr = findings_map.get('MTHFR')
    mtrr = findings_map.get('MTRR')
    gc = findings_map.get('GC')
    pemt = findings_map.get('PEMT')
    fads1 = findings_map.get('FADS1')
    fut2 = findings_map.get('FUT2')
    tcf7l2 = findings_map.get('TCF7L2')

    fuel_parts = []

    if mthfr and mthfr.get('magnitude', 0) >= 2:
        pct = "70%" if 'homozygous' in mthfr.get('description', '').lower() else "35%"
        fuel_parts.append(
            f"**🔁 Your body struggles to use standard B-vitamins (MTHFR gene).**\n"
            f"Imagine a vitamin filter in your body that is about {pct} clogged. The cheap form of B-vitamin (folic acid) found in most supplements and fortified cereals gets stuck and piles up unused — or worse, as a waste product.\n\n"
            f"* ✅ **The fix:** Read your supplement labels. You need **Methylfolate** (not 'folic acid') and **Methylcobalamin** (not just 'B12' or 'cyanocobalamin'). "
            f"These are the 'pre-activated' versions your body can actually absorb and use directly."
        )

    if mtrr and mtrr.get('magnitude', 0) >= 2:
        fuel_parts.append(
            "**🔋 Your body also has trouble recycling Vitamin B12 (MTRR gene).**\n"
            "Even if your blood test shows 'normal' B12 levels, your cells may not be using it efficiently. "
            "Low functional B12 can cause brain fog, fatigue, and nerve issues.\n\n"
            "* ✅ **The fix:** Use **Methylcobalamin B12** (the active form) — ideally sublingual (dissolved under your tongue) for the best absorption."
        )

    if gc and gc.get('status', '').lower() == 'low':
        fuel_parts.append(
            "**☀️ You are built to be Vitamin D deficient (GC gene).**\n"
            "Your body is genetically worse at absorbing and holding onto Vitamin D from sunlight and food, no matter where you live or how much sun you get.\n\n"
            "* ✅ **The fix:** Take **Vitamin D3 (2,000 to 5,000 IU)** every single day with a meal that has fat in it. "
            "Pair it with **Vitamin K2 (100mcg)** — K2 makes sure the calcium that Vitamin D activates goes into your bones, not your arteries."
        )

    if pemt and pemt.get('magnitude', 0) >= 2:
        fuel_parts.append(
            "**🥚 Your liver and brain need more choline than most people (PEMT gene).**\n"
            "Choline is a nutrient that your body uses to build cell walls and make a key brain chemical. "
            "Most people make enough on their own, but your gene variant means you need more from your diet.\n\n"
            "* ✅ **The fix:** Eat **2-3 whole eggs per day** — egg yolks are one of the richest natural sources of choline. "
            "This is the simplest and most effective way to cover this deficit."
        )

    if tcf7l2 and tcf7l2.get('magnitude', 0) >= 2:
        fuel_parts.append(
            "**🍞 Your body is less efficient at handling large amounts of carbohydrates (TCF7L2 gene).**\n"
            "You have an elevated genetic risk of developing Type 2 Diabetes, especially if your diet is high in refined carbs and sugar.\n\n"
            "* ✅ **The fix:** Prioritize protein and healthy fats at meals. Reduce white rice, bread, and sugary drinks. "
            "This single dietary change is the most powerful tool you have to offset this risk."
        )

    fuel_section = "\n\n---\n\n".join(fuel_parts) if fuel_parts else "Your nutritional processing genes are performing at standard baseline levels. A balanced, whole-food diet is sufficient."

    # ==========================================================================
    # SECTION 3: FITNESS & HEART HEALTH
    # ==========================================================================
    actn3 = findings_map.get('ACTN3')
    apo_e = findings_map.get('APOE')
    il6 = findings_map.get('IL6') or findings_map.get('IL-6')
    ace = findings_map.get('ACE')
    agtr1 = findings_map.get('AGTR1')
    slco1b1 = findings_map.get('SLCO1B1')

    phys_parts = []

    if actn3:
        s = actn3.get('status', '').lower()
        if 'power' in s:
            phys_parts.append(
                "**💪 Your muscles are built for explosive power (ACTN3 gene).**\n"
                "You have a higher proportion of fast-twitch muscle fibers — the kind that make you naturally stronger and faster in short bursts.\n\n"
                "* ✅ **Best training style:** Heavy compound lifts (squats, deadlifts, bench press), sprints, and explosive movements will give you the best results."
            )
        elif 'endurance' in s:
            phys_parts.append(
                "**🏃 Your muscles are built for endurance (ACTN3 gene).**\n"
                "You have a higher proportion of slow-twitch muscle fibers — the kind that keep you going for long periods without tiring.\n\n"
                "* ✅ **Best training style:** Running, cycling, swimming, and high-rep resistance training will work best for your body type."
            )
        else:
            phys_parts.append(
                "**🔀 Your muscles are balanced between power and endurance (ACTN3 gene).**\n"
                "You don't have an extreme lean in either direction, which means you adapt well to almost any type of training.\n\n"
                "* ✅ **Best training style:** A mix of heavy lifting AND cardio will give you the best of both worlds."
            )

    if ace and ace.get('magnitude', 0) >= 2 or agtr1 and agtr1.get('magnitude', 0) >= 2:
        phys_parts.append(
            "**🩺 Your genetics make you more susceptible to high blood pressure (ACE / AGTR1 genes).**\n"
            "You have multiple gene variants that naturally push your blood pressure higher over time. This is not a crisis — it's a heads-up.\n\n"
            "* ✅ **What to do:** Check your blood pressure a few times a year. Keep your salt intake low. Regular cardio (even walking) is one of the most effective long-term treatments for this."
        )

    if apo_e and 'e4' in apo_e.get('status', '').lower():
        phys_parts.append(
            "**🧠 You carry the APOE4 gene — a major flag for long-term brain and heart health.**\n"
            "Think of APOE4 as a gene that makes your body slightly worse at cleaning up cholesterol and inflammation in the brain. "
            "Over decades, this significantly raises the risk of heart disease and Alzheimer's disease.\n\n"
            "This is not a diagnosis. Many APOE4 carriers live long, healthy lives. But it means the lifestyle choices you make in your 20s and 30s matter more than they do for the average person.\n\n"
            "* ✅ **Your most important defenses:**\n"
            "  * **Sleep 7-9 hours** every night (your brain literally cleans itself while you sleep)\n"
            "  * **Omega-3 fish oil (2-3g/day)** — reduces brain inflammation\n"
            "  * **Regular cardio** — the single most evidence-backed protection against cognitive decline\n"
            "  * **Keep processed foods, sugar, and alcohol low**"
        )

    if il6 and il6.get('magnitude', 0) >= 2:
        phys_parts.append(
            "**🔥 Your body runs with higher baseline inflammation (IL-6 gene).**\n"
            "Inflammation is your immune system's 'alarm' — it's necessary for fighting infections. But when the alarm is always slightly on, it silently damages organs and speeds up aging.\n\n"
            "* ✅ **Your key anti-inflammatory tools:** Omega-3 fish oil, colorful vegetables, consistent sleep, and avoiding processed seed oils."
        )

    phys_section = "\n\n---\n\n".join(phys_parts) if phys_parts else "Your cardiovascular and fitness-related genes are at a standard baseline."

    # ==========================================================================
    # SECTION 4: CONDITIONS FOUND IN YOUR DNA
    # ==========================================================================
    condition_parts = []
    seen_conditions = set()

    for p in pathogenic:
        name = plain_condition_name(p.get('traits', 'Unknown'))
        if name in seen_conditions:
            continue
        seen_conditions.add(name)
        copies = "two copies" if p.get('is_homozygous') else "one copy"
        stars = p.get('gold_stars', 0)
        confidence = "High confidence" if stars >= 2 else "Moderate confidence"
        condition_parts.append(f"* **{name}** — {confidence} finding. You carry {copies} of this genetic marker.")

    for p in likely_pathogenic[:5]:
        name = plain_condition_name(p.get('traits', 'Unknown'))
        if name in seen_conditions:
            continue
        seen_conditions.add(name)
        condition_parts.append(f"* **{name}** — Possible finding. More research or a doctor's interpretation is needed.")

    conditions_section = (
        "> ⚠️ **Important:** These are genetic markers — not diagnoses. Having a gene marker does NOT mean you have the disease. It means your risk is higher than average. Think of it like being told you have a higher chance of rain — you still might not get wet.\n\n"
        + "\n".join(condition_parts)
    ) if condition_parts else "No major disease markers were found in your DNA."

    # ==========================================================================
    # SECTION 5: MEDICATION ALERTS (CRITICAL)
    # ==========================================================================
    l1_findings = [f for f in pharmgkb if f.get('level') in ['1A', '1B']]
    drug_lines = []
    seen_drugs = set()
    for f in l1_findings:
        drug_key = f['drugs'].split(';')[0].strip().lower()
        if drug_key in seen_drugs:
            continue
        line = plain_drug_alert(f['drugs'], f['gene'], f.get('annotation', ''))
        if line:
            drug_lines.append(line)
            seen_drugs.add(drug_key)

    if drug_lines:
        drug_section = (
            "Your DNA affects how your body processes certain medications. This is NOT about avoiding these drugs forever — "
            "it's about making sure your doctor knows BEFORE they prescribe them so they can adjust your dose. "
            "Just show this section to any doctor before a new prescription.\n\n"
            + "\n".join(drug_lines)
        )
    else:
        drug_section = "No critical medication interaction flags were detected."

    # ==========================================================================
    # SECTION 6: DAILY ACTION PLAN
    # ==========================================================================
    morning_supps = []
    evening_supps = []
    food_rules = []

    if mthfr and mthfr.get('magnitude', 0) >= 2:
        morning_supps.append("**L-Methylfolate (400-800mcg)** — The active form of Folate your body can actually use. Do NOT buy 'Folic Acid'.")
    if mtrr and mtrr.get('magnitude', 0) >= 2:
        morning_supps.append("**Methylcobalamin B12 (1000mcg)** — The active form of B12. Dissolve under your tongue for best results.")
    if gc and gc.get('status', '').lower() == 'low':
        morning_supps.append("**Vitamin D3 (2,000-5,000 IU) + K2 (100mcg)** — Take with a fatty meal (like eggs or avocado) for proper absorption.")
    if apo_e or il6:
        morning_supps.append("**Omega-3 Fish Oil (2-3g)** — Look for labels showing 'EPA + DHA' combined. Reduces brain and body inflammation.")

    if comt and 'slow' in comt.get('status', '').lower():
        evening_supps.append("**Magnesium Glycinate (300-400mg)** — Helps your brain physically clear out stress chemicals. Dramatically improves sleep quality.")

    if pemt and pemt.get('magnitude', 0) >= 2:
        food_rules.append("🥚 Eat **2-3 whole eggs per day** (your body needs extra choline that these provide naturally)")
    if tcf7l2 and tcf7l2.get('magnitude', 0) >= 2:
        food_rules.append("🍚 **Reduce refined carbs** — white rice, white bread, pasta, and sugary drinks are your biggest dietary risk")
    if ace or agtr1:
        food_rules.append("🧂 **Cut back on salt** — your heart genes make you more sensitive to sodium than most people")
    if apo_e:
        food_rules.append("🐟 **Eat oily fish (salmon, sardines, mackerel) 2x per week** — the Omega-3s directly counteract your APOE4 risk")

    morning_str = "\n".join([f"  * {s}" for s in morning_supps]) if morning_supps else "  * No specific supplements indicated for you."
    evening_str = "\n".join([f"  * {s}" for s in evening_supps]) if evening_supps else "  * No specific evening supplements indicated."
    food_str = "\n".join(food_rules) if food_rules else "  * A standard balanced diet is sufficient."

    # ==========================================================================
    # ASSEMBLE FINAL REPORT
    # ==========================================================================
    name_line = f"Prepared for: **{subject_name}**\n" if subject_name else ""

    report = f"""# 🧬 Your Personal Genetic Health Manual
{name_line}*Generated: {now} | Based on analysis of your 23andMe genome file*

> **What is this?**
> Think of your DNA like an instruction manual for your body. Most people never get to read it. This report translates yours from complex genetic code into simple, actionable English. It is not a diagnosis. It is your personal owner's manual — written by your genes, translated for you.

---

## 🧠 Section 1: How Your Brain and Mood Work

{brain_section}

---

## 🍎 Section 2: Food, Vitamins & What Your Body Actually Absorbs

{fuel_section}

---

## 💪 Section 3: Your Body, Fitness & Long-Term Health

{phys_section}

---

## 🔬 Section 4: Conditions Flagged in Your Genetic Data

{conditions_section}

---

## 💊 Section 5: Medications Your Doctor Needs to Know About

{drug_section}

---

## ✅ Section 6: Your Daily Action Plan

This is the simplest summary of everything above. If you do nothing else, do this.

**Take in the morning (with breakfast):**
{morning_str}

**Take in the evening (1 hour before bed):**
{evening_str}

**Food rules specific to YOUR DNA:**
{food_str}

---

*⚕️ Disclaimer: This report is generated from raw genetic data for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider before making changes to your supplements, diet, or medications.*
"""

    with open(output_path, 'w') as f:
        f.write(report)
    print(f"    Executive Synthesis generated at: {output_path}")
