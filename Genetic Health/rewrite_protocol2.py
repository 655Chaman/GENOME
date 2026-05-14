import re

with open('scripts/run_full_analysis.py', 'r') as f:
    content = f.read()

start_idx = content.find('def generate_actionable_protocol(')
end_idx = content.find('# =============================================================================\n# MAIN PIPELINE')

new_func = """def generate_actionable_protocol(health_results: dict, disease_findings: dict,
                                  output_path, subject_name: str = None):
    \"\"\"Generate comprehensive, user-friendly actionable health protocol.\"\"\"
    print_step("Generating actionable health protocol (user-friendly)")

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    subject_line = f"Prepared for: **{subject_name}**\\n" if subject_name else ""

    findings_dict = {f['gene']: f for f in health_results['findings']}

    report = f\"\"\"# Your Personalized Daily Action Plan
{subject_line}*Generated: {now}*

This isn't a generic health blog. This protocol is built strictly from the unique bottlenecks, strengths, and risks found in your raw DNA. 

We have stripped away the complex medical jargon. Below is exactly what you should be doing, what you should avoid, and *why* it matters specifically for your biology.

---

## 💊 The Nutrient Protocol

Based on your genetics, your body has specific deficiencies and high-risk areas. We have separated these into two categories: Clinical Supplements (concentrated doses for immediate impact) and Science-Backed Natural/Ayurvedic Sources (for long-term foundational health).

### 1. Clinical Supplements (Concentrated Doses)

\"\"\"

    supp_found = False
    
    supp_report = ""
    natural_report = "### 2. Science-Backed Natural & Ayurvedic Sources\\n\\n"

    # 1. MTHFR 
    if 'MTHFR' in findings_dict and findings_dict['MTHFR']['magnitude'] >= 2:
        supp_found = True
        supp_report += "* **Methylfolate (L-5-MTHF) & Methylcobalamin (B12)**\\n"
        supp_report += "  * **The Dose:** 400-800mcg of Methylfolate and 1000mcg of B12 daily.\\n"
        supp_report += "  * **The Why:** You have the 'MTHFR' gene variation. Your body struggles to convert standard B-vitamins into the active form your brain needs for energy.\\n"
        supp_report += "  * **Pro-Tip:** Never buy cheap vitamins with 'folic acid'—your body can't process it.\\n\\n"
        
        natural_report += "* **Natural Folate Sources (For MTHFR):**\\n"
        natural_report += "  * **Foods:** Beef liver, dark leafy greens (spinach, kale), asparagus, and avocados.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Moringa oleifera (Drumstick tree leaves) is exceptionally high in natural, highly bioavailable folate and B-vitamins.\\n\\n"

    # 2. Vitamin D (GC)
    if 'GC' in findings_dict and findings_dict['GC'].get('status') == 'low':
        supp_found = True
        supp_report += "* **High-Dose Vitamin D3 + K2**\\n"
        supp_report += "  * **The Dose:** 2000-5000 IU of D3 daily.\\n"
        supp_report += "  * **The Why:** Your body produces lower amounts of the protein that carries Vitamin D through your blood.\\n\\n"
        
        natural_report += "* **Natural D3 & Calcium Routing (For GC Gene):**\\n"
        natural_report += "  * **Foods:** Wild-caught salmon, egg yolks, and sun-exposed mushrooms.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Shilajit (rich in fulvic acid and trace minerals) helps optimize bone density and mineral absorption, synergizing with natural sunlight exposure.\\n\\n"

    # 3. Omega 3 (FADS1)
    if 'FADS1' in findings_dict and findings_dict['FADS1'].get('status') == 'low_conversion':
        supp_found = True
        supp_report += "* **Marine Omega-3s (EPA/DHA)**\\n"
        supp_report += "  * **The Dose:** 1-2g of high-quality fish oil or algae oil daily.\\n"
        supp_report += "  * **The Why:** You lack the genetic hardware to convert plant-based Omega-3s into the EPA/DHA your brain uses.\\n\\n"
        
        natural_report += "* **Natural Brain Lipids (For FADS1):**\\n"
        natural_report += "  * **Foods:** Mackerel, sardines, and fatty wild fish. Walnuts and chia seeds will *not* work for your specific genetic profile.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Brahmi (Bacopa monnieri) combined with high-quality Ghee (clarified butter). Ghee provides the fat backbone, while Brahmi is scientifically proven to reduce neuro-inflammation.\\n\\n"

    # 4. Stress (COMT)
    if 'COMT' in findings_dict and findings_dict['COMT'].get('status') == 'slow':
        supp_found = True
        supp_report += "* **Magnesium Glycinate**\\n"
        supp_report += "  * **The Dose:** 300-400mg in the evening.\\n"
        supp_report += "  * **The Why:** Your 'Slow COMT' gene means your brain holds onto adrenaline for a long time. Magnesium acts as a biochemical 'brake pedal'.\\n\\n"
        
        natural_report += "* **Natural Adrenaline Clearance (For Slow COMT):**\\n"
        natural_report += "  * **Foods:** Pumpkin seeds, almonds, and cacao (all high in natural magnesium).\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Ashwagandha (KSM-66) and L-Theanine (from Green Tea). These are powerful adaptogens proven to lower cortisol and counteract your genetic tendency to hold onto stress hormones.\\n\\n"

    # 5. Liver (PEMT)
    if 'PEMT' in findings_dict:
        supp_found = True
        supp_report += "* **Choline (CDP-Choline or Alpha-GPC)**\\n"
        supp_report += "  * **The Dose:** 250-500mg daily.\\n"
        supp_report += "  * **The Why:** Your liver genetically struggles to produce enough choline on its own.\\n\\n"
        
        natural_report += "* **Natural Liver & Choline Support (For PEMT):**\\n"
        natural_report += "  * **Foods:** Pasture-raised egg yolks (2-3 per day provides enough natural choline to bypass this gene flaw), beef liver.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Kutki (Picrorhiza kurroa) or Milk Thistle to support your liver's fat-processing capabilities, which are strained by your genetics.\\n\\n"

    # 6. Diabetes/Metabolic Risk Additions
    has_diabetes_risk = 'TCF7L2' in findings_dict or any('diabetes' in f.get('traits', '').lower() for f in disease_findings.get('pathogenic', []) + disease_findings.get('risk_factor', []))
    if has_diabetes_risk:
        supp_found = True
        supp_report += "* **Berberine HCL (The 'Natural Metformin')**\\n"
        supp_report += "  * **The Dose:** 500mg before your largest carbohydrate meals.\\n"
        supp_report += "  * **The Why:** You have a severely elevated genetic risk for Type 2 Diabetes and insulin resistance. Berberine is clinically proven to activate AMPK (your body's metabolic master switch) and shuttle sugar out of your blood and into your muscles.\\n\\n"
        
        natural_report += "* **Natural Blood Sugar Control (For Diabetes Risk):**\\n"
        natural_report += "  * **Foods:** Ceylon Cinnamon (1 tsp daily), Apple Cider Vinegar (1 tbsp in water before meals).\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Gymnema Sylvestre (often called 'Gurmar', meaning 'destroyer of sugar' in Hindi) and Bitter Melon (Karela). Both are legendary Ayurvedic interventions clinically shown to lower HbA1c and curb sugar cravings.\\n\\n"

    # 7. Cardiovascular & Hypertension Risk Additions
    has_cardio_risk = any(g in findings_dict for g in ['AGTR1', 'ACE', 'AGT', 'GNB3']) or any('heart' in f.get('traits', '').lower() or 'hypertension' in f.get('traits', '').lower() for f in disease_findings.get('risk_factor', []))
    if has_cardio_risk:
        supp_found = True
        supp_report += "* **Coenzyme Q10 (Ubiquinol) & L-Citrulline**\\n"
        supp_report += "  * **The Dose:** 100-200mg Ubiquinol, 3-6g L-Citrulline daily.\\n"
        supp_report += "  * **The Why:** You have multiple genetic triggers for high blood pressure and cardiovascular plaque. CoQ10 protects the heart muscle from oxidative stress, and L-Citrulline drastically increases nitric oxide to keep your blood vessels relaxed and wide open.\\n\\n"
        
        natural_report += "* **Natural Cardiovascular Defense (For Heart/BP Risk):**\\n"
        natural_report += "  * **Foods:** Beets and Arugula (highest natural sources of dietary nitrates to dilate blood vessels), Pomegranate juice.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Terminalia Arjuna (Arjuna Bark) and aged Garlic extract. Arjuna is the most revered Ayurvedic herb for the heart, scientifically proven to improve cardiac muscle function and lower blood pressure.\\n\\n"

    # 8. High Systemic Inflammation Additions
    has_inflammation = 'IL6' in findings_dict or 'CRP' in findings_dict or any('autoimmune' in f.get('traits', '').lower() for f in disease_findings.get('risk_factor', []))
    if has_inflammation:
        supp_found = True
        supp_report += "* **Curcumin Phytosome (High Absorption)**\\n"
        supp_report += "  * **The Dose:** 500-1000mg daily.\\n"
        supp_report += "  * **The Why:** Your genetic baseline for systemic inflammation (like IL-6) is set unnaturally high. High absorption Curcumin acts as a master anti-inflammatory switch, downregulating inflammatory cytokines before they cause joint or tissue damage.\\n\\n"
        
        natural_report += "* **Natural Anti-Inflammatory Baseline (For High Inflammation):**\\n"
        natural_report += "  * **Foods:** Bone broth (rich in collagen and glycine to heal the gut), wild blueberries.\\n"
        natural_report += "  * **Ayurvedic/Herbal:** Turmeric Root (must be consumed with black pepper/piperine and fat like Ghee for absorption) and Boswellia Serrata (Indian Frankincense). Together, these form the ultimate Ayurvedic duo for crushing joint pain and systemic inflammation.\\n\\n"

    if not supp_found:
        report += "Your genetics don't show any severe nutrient processing bottlenecks! A standard, high-quality multivitamin is sufficient.\\n\\n"
    else:
        report += supp_report + "\\n" + natural_report

    report += "---\\n\\n## 🥗 How You Should Actually Eat\\n\\n"

    diet_found = False

    if 'APOA2' in findings_dict and findings_dict['APOA2'].get('status') == 'sensitive':
        diet_found = True
        report += "* **Treat Saturated Fat like a toxin for weight gain.**\\n"
        report += "  * **The Why:** Because of your APOA2 gene, your body is hyper-sensitive to saturated fat. Eating butter, fatty red meat, and coconut oil will lead to rapid weight gain. Stick to olive oil and avocados.\\n\\n"

    if 'MTHFR' in findings_dict and findings_dict['MTHFR']['magnitude'] >= 2:
        diet_found = True
        report += "* **Aggressively hunt for natural Folate.**\\n"
        report += "  * **The Why:** Avoid cheap processed bread and cereals fortified with synthetic 'folic acid', as it clogs up your system.\\n\\n"

    if 'MCM6/LCT' in findings_dict and 'intolerant' in findings_dict['MCM6/LCT'].get('status', ''):
        diet_found = True
        report += "* **Ditch the Dairy.**\\n"
        report += "  * **The Why:** You are genetically lactose intolerant. Dairy is likely causing low-grade systemic inflammation and bloating in your gut.\\n\\n"

    caffeine_issues = []
    if 'CYP1A2' in findings_dict and findings_dict['CYP1A2'].get('status') in ['slow', 'intermediate']:
        caffeine_issues.append("slow caffeine metabolizer")
    if 'COMT' in findings_dict and findings_dict['COMT'].get('status') == 'slow':
        caffeine_issues.append("slow adrenaline clearance")

    if caffeine_issues:
        diet_found = True
        report += f"* **Hard stop on Caffeine after 10 AM.**\\n"
        report += f"  * **The Why:** Because you are a {caffeine_issues[0]}, caffeine stays in your bloodstream far longer than average, silently destroying your deep sleep architecture.\\n\\n"

    if not diet_found:
        report += "Your genetics don't dictate any extreme dietary restrictions. Focus on a standard whole-food, anti-inflammatory diet.\\n\\n"


    report += "---\\n\\n## 🏃‍♂️ How You Should Move and Recover\\n\\n"

    life_found = False

    if 'ACTN3' in findings_dict:
        life_found = True
        status = findings_dict['ACTN3'].get('status', '')
        if status == 'endurance':
            report += "* **Focus on high-volume Endurance training.**\\n"
            report += "  * **The Why:** Your muscle fibers are genetically biased toward endurance (aerobic) capacity rather than explosive power. You will recover much faster from high-rep or distance training.\\n\\n"
        elif status == 'power':
            report += "* **Focus on explosive Power and Sprint training.**\\n"
            report += "  * **The Why:** You have the 'sprinter gene.' Your muscle fibers are built for explosive, heavy, high-intensity output.\\n\\n"

    if 'ARNTL' in findings_dict:
        life_found = True
        report += "* **Fiercely protect your Circadian Rhythm.**\\n"
        report += "  * **The Why:** You have a genetically weaker internal clock. You need strict, consistent sleep and wake times, even on weekends.\\n\\n"

    if 'MC1R' in findings_dict:
        life_found = True
        report += "* **Aggressive Sun Protection.**\\n"
        report += "  * **The Why:** Your skin is genetically highly vulnerable to UV damage. You will experience accelerated skin aging if you don't use daily SPF 30+.\\n\\n"

    if not life_found:
        report += "Your baseline physiology is well-rounded. Follow standard guidelines for 150+ minutes of aerobic work and 2 days of strength training per week.\\n\\n"


    report += "---\\n\\n## 🩺 What To Tell Your Doctor (Lab Tests & Meds)\\n\\n"
    report += "Do not wait until you are sick to test these. Demand these specific lab panels at your next physical based on your genetic blind spots.\\n\\n"

    report += "### 🩸 Blood Tests to Demand Annually\\n"
    
    labs = []
    if 'MTHFR' in findings_dict:
        labs.append("* **Homocysteine:** Check this annually. Your MTHFR gene means your body might struggle to clear out this inflammatory amino acid.")
    if 'GC' in findings_dict:
        labs.append("* **25-OH Vitamin D:** You are genetically prone to low Vitamin D. Aim for the optimal range of 40-60 ng/mL.")
    if any(g in findings_dict for g in ['AGTR1', 'ACE', 'AGT', 'GNB3']):
        labs.append("* **Detailed Lipid & Blood Pressure Panel:** You have multiple genetic triggers for high blood pressure.")
    if 'TCF7L2' in findings_dict:
        labs.append("* **HbA1c & Fasting Insulin:** Because of your strong genetic risk for Type 2 Diabetes, track these markers ruthlessly.")
    if 'HFE' in findings_dict:
        labs.append("* **Ferritin / Iron Panel:** You carry a gene that makes your body absorb too much iron. If this is high, donating blood is highly effective.")

    if labs:
        for l in labs:
            report += f"{l}\\n"
    else:
        report += "* **Standard Comprehensive Metabolic Panel:** Your genetics don't point to any hidden systemic crises.\\n"

    report += "\\n### ⚠️ Dangerous Medication Warnings\\n"
    report += "If a doctor ever prescribes you a new drug, specifically check if it interacts with these genetic quirks.\\n\\n"

    level_1 = [f for f in health_results['pharmgkb_findings'] if f['level'] in ['1A', '1B']]
    level_2 = [f for f in health_results['pharmgkb_findings'] if f['level'] in ['2A', '2B']]
    all_drugs = level_1 + level_2

    if all_drugs:
        seen = set()
        count = 0
        for f in all_drugs:
            if f['gene'] not in seen:
                seen.add(f['gene'])
                drugs = f['drugs'][:50] + '...' if len(f['drugs']) > 50 else f['drugs']
                report += f"* **Watch out for {drugs}:** Because of a quirk in your {f['gene']} gene, your body might metabolize these drugs too fast or too slow. Ask your doctor to adjust the dose based on pharmacogenomics.\\n"
                count += 1
                if count >= 8: break
    else:
        report += "* You have no high-risk pharmaceutical sensitivities detected in this scan.\\n"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"    Written to: {output_path}")

"""

new_content = content[:start_idx] + new_func + content[end_idx:]

with open('scripts/run_full_analysis.py', 'w') as f:
    f.write(new_content)
print("Updated successfully")
