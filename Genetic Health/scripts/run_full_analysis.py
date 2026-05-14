#!/usr/bin/env python3
"""
Full Genetic Health Analysis Pipeline

This master script runs the complete genetic analysis workflow:
1. Lifestyle/Health Analysis -> EXHAUSTIVE_GENETIC_REPORT.md
2. Disease Risk Analysis -> EXHAUSTIVE_DISEASE_RISK_REPORT.md
3. Actionable Health Protocol -> ACTIONABLE_HEALTH_PROTOCOL.md

Usage:
    python run_full_analysis.py                     # Uses default genome.txt
    python run_full_analysis.py path/to/genome.txt  # Custom genome file
    python run_full_analysis.py --name "John Doe"   # Add name to reports
"""

import sys
import os
import shutil
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from comprehensive_snp_database import COMPREHENSIVE_SNPS
from generate_executive_synthesis import generate_synthesis_report

# Directory configuration
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_REPORTS_DIR = BASE_DIR / "reports"


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(text)
    print("=" * 70)


def print_step(text):
    """Print a step indicator."""
    print(f"\n>>> {text}")


# =============================================================================
# GENOME LOADING
# =============================================================================

def load_genome(genome_path: Path) -> tuple:
    """Load 23andMe genome file into dictionaries."""
    print_step(f"Loading genome from {genome_path}")

    genome_by_rsid = {}
    genome_by_position = {}

    with open(genome_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
                if genotype != '--':
                    genome_by_rsid[rsid] = {
                        'chromosome': chrom,
                        'position': pos,
                        'genotype': genotype
                    }
                    pos_key = f"{chrom}:{pos}"
                    genome_by_position[pos_key] = {
                        'rsid': rsid,
                        'genotype': genotype
                    }

    print(f"    Loaded {len(genome_by_rsid):,} SNPs")
    return genome_by_rsid, genome_by_position


# =============================================================================
# PHARMGKB LOADING
# =============================================================================

def load_pharmgkb() -> dict:
    """Load PharmGKB drug-gene annotations."""
    annotations_path = DATA_DIR / "clinical_annotations.tsv"
    alleles_path = DATA_DIR / "clinical_ann_alleles.tsv"

    if not annotations_path.exists() or not alleles_path.exists():
        print("    PharmGKB files not found, skipping drug interactions")
        return {}

    print_step("Loading PharmGKB data")

    pharmgkb = {}
    annotations = {}

    with open(annotations_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            ann_id = row.get('Clinical Annotation ID', '')
            variant = row.get('Variant/Haplotypes', '')
            if variant.startswith('rs'):
                annotations[ann_id] = {
                    'rsid': variant,
                    'gene': row.get('Gene', ''),
                    'drugs': row.get('Drug(s)', ''),
                    'phenotype': row.get('Phenotype(s)', ''),
                    'level': row.get('Level of Evidence', ''),
                    'category': row.get('Phenotype Category', ''),
                }

    with open(alleles_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            ann_id = row.get('Clinical Annotation ID', '')
            if ann_id in annotations:
                rsid = annotations[ann_id]['rsid']
                genotype = row.get('Genotype/Allele', '')
                if rsid not in pharmgkb:
                    pharmgkb[rsid] = {
                        'gene': annotations[ann_id]['gene'],
                        'drugs': annotations[ann_id]['drugs'],
                        'phenotype': annotations[ann_id]['phenotype'],
                        'level': annotations[ann_id]['level'],
                        'category': annotations[ann_id]['category'],
                        'genotypes': {}
                    }
                pharmgkb[rsid]['genotypes'][genotype] = row.get('Annotation Text', '')

    print(f"    Loaded {len(pharmgkb):,} drug-gene interactions")
    return pharmgkb


# =============================================================================
# LIFESTYLE/HEALTH ANALYSIS
# =============================================================================

def analyze_lifestyle_health(genome_by_rsid: dict, pharmgkb: dict) -> dict:
    """Analyze genome against lifestyle/health SNP database."""
    print_step("Running lifestyle/health analysis")

    results = {
        'findings': [],
        'pharmgkb_findings': [],
        'by_category': defaultdict(list),
        'summary': {
            'total_snps': len(genome_by_rsid),
            'analyzed_snps': 0,
            'high_impact': 0,
            'moderate_impact': 0,
            'low_impact': 0,
        }
    }

    # Check against comprehensive database
    for rsid, info in COMPREHENSIVE_SNPS.items():
        if rsid in genome_by_rsid:
            genotype = genome_by_rsid[rsid]['genotype']
            genotype_rev = genotype[::-1] if len(genotype) == 2 else genotype

            variant_info = info['variants'].get(genotype) or info['variants'].get(genotype_rev)

            if variant_info:
                finding = {
                    'rsid': rsid,
                    'gene': info['gene'],
                    'category': info['category'],
                    'genotype': genotype,
                    'status': variant_info['status'],
                    'description': variant_info['desc'],
                    'magnitude': variant_info['magnitude'],
                    'note': info.get('note', ''),
                }
                results['findings'].append(finding)
                results['by_category'][info['category']].append(finding)
                results['summary']['analyzed_snps'] += 1

                if variant_info['magnitude'] >= 3:
                    results['summary']['high_impact'] += 1
                elif variant_info['magnitude'] >= 2:
                    results['summary']['moderate_impact'] += 1
                elif variant_info['magnitude'] >= 1:
                    results['summary']['low_impact'] += 1

    # Check PharmGKB
    for rsid, info in pharmgkb.items():
        if rsid in genome_by_rsid:
            genotype = genome_by_rsid[rsid]['genotype']
            genotype_rev = genotype[::-1] if len(genotype) == 2 else genotype
            annotation = info['genotypes'].get(genotype) or info['genotypes'].get(genotype_rev)
            if annotation and info['level'] in ['1A', '1B', '2A', '2B']:
                finding = {
                    'rsid': rsid,
                    'gene': info['gene'],
                    'drugs': info['drugs'],
                    'genotype': genotype,
                    'annotation': annotation,
                    'level': info['level'],
                    'category': info['category'],
                }
                results['pharmgkb_findings'].append(finding)

    # Sort findings
    results['findings'].sort(key=lambda x: -x['magnitude'])
    results['pharmgkb_findings'].sort(key=lambda x: x['level'])

    print(f"    Found {len(results['findings'])} lifestyle/health findings")
    print(f"    Found {len(results['pharmgkb_findings'])} drug-gene interactions")

    return results


# =============================================================================
# DISEASE RISK ANALYSIS
# =============================================================================

def load_clinvar_and_analyze(genome_by_position: dict) -> tuple:
    """Load ClinVar and analyze for disease variants."""
    clinvar_path = DATA_DIR / "clinvar_alleles.tsv"

    if not clinvar_path.exists():
        print("    ClinVar file not found, skipping disease risk analysis")
        return None, None

    print_step("Loading ClinVar and analyzing disease risk")

    findings = {
        'pathogenic': [],
        'likely_pathogenic': [],
        'risk_factor': [],
        'drug_response': [],
        'protective': [],
        'other_significant': []
    }

    stats = {
        'total_clinvar': 0,
        'matched': 0,
        'pathogenic_matched': 0,
        'likely_pathogenic_matched': 0
    }

    with open(clinvar_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            stats['total_clinvar'] += 1

            chrom = row['chrom']
            pos = row['pos']
            pos_key = f"{chrom}:{pos}"

            if pos_key not in genome_by_position:
                continue

            stats['matched'] += 1

            user_data = genome_by_position[pos_key]
            user_genotype = user_data['genotype']
            ref_allele = row['ref']
            alt_allele = row['alt']
            clinical_sig = row['clinical_significance'].lower()

            # Only process true SNPs
            if len(ref_allele) != 1 or len(alt_allele) != 1:
                continue

            has_variant = alt_allele in user_genotype
            is_homozygous = user_genotype == alt_allele + alt_allele
            is_heterozygous = has_variant and not is_homozygous
            has_ref_only = user_genotype == ref_allele + ref_allele

            if has_ref_only or not has_variant:
                continue

            finding = {
                'chromosome': chrom,
                'position': pos,
                'rsid': user_data['rsid'],
                'gene': row['symbol'],
                'ref': ref_allele,
                'alt': alt_allele,
                'user_genotype': user_genotype,
                'is_homozygous': is_homozygous,
                'is_heterozygous': is_heterozygous,
                'clinical_significance': row['clinical_significance'],
                'review_status': row['review_status'],
                'gold_stars': int(row['gold_stars']) if row['gold_stars'] else 0,
                'traits': row['all_traits'],
                'inheritance': row.get('inheritance_modes', ''),
                'hgvs_p': row.get('hgvs_p', ''),
                'hgvs_c': row.get('hgvs_c', ''),
                'molecular_consequence': row.get('molecular_consequence', ''),
                'xrefs': row.get('xrefs', '')
            }

            if 'pathogenic' in clinical_sig and 'likely' not in clinical_sig and 'conflict' not in clinical_sig:
                findings['pathogenic'].append(finding)
                stats['pathogenic_matched'] += 1
            elif 'likely pathogenic' in clinical_sig or 'likely_pathogenic' in clinical_sig:
                findings['likely_pathogenic'].append(finding)
                stats['likely_pathogenic_matched'] += 1
            elif 'risk factor' in clinical_sig or 'risk_factor' in clinical_sig:
                findings['risk_factor'].append(finding)
            elif 'drug response' in clinical_sig or 'drug_response' in clinical_sig:
                findings['drug_response'].append(finding)
            elif 'protective' in clinical_sig:
                findings['protective'].append(finding)
            elif 'association' in clinical_sig or 'affects' in clinical_sig:
                findings['other_significant'].append(finding)

    print(f"    ClinVar entries scanned: {stats['total_clinvar']:,}")
    print(f"    Pathogenic variants: {stats['pathogenic_matched']}")
    print(f"    Likely pathogenic: {stats['likely_pathogenic_matched']}")
    print(f"    Risk factors: {len(findings['risk_factor'])}")

    return findings, stats


def classify_zygosity(finding):
    """Classify zygosity impact."""
    inheritance = finding['inheritance'].lower() if finding['inheritance'] else ''

    if finding['is_homozygous']:
        return 'AFFECTED', 'Homozygous for variant'
    elif finding['is_heterozygous']:
        if 'recessive' in inheritance:
            return 'CARRIER', 'Heterozygous carrier (recessive)'
        elif 'dominant' in inheritance:
            return 'AFFECTED', 'Heterozygous (dominant)'
        else:
            return 'HETEROZYGOUS', 'Heterozygous (inheritance unclear)'
    return 'UNKNOWN', 'Zygosity unclear'


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_exhaustive_genetic_report(results: dict, output_path: Path, subject_name: str = None):
    """Generate the exhaustive lifestyle/health genetic report."""
    print_step(f"Generating exhaustive genetic report")

    # Import the generator logic
    from generate_exhaustive_report import (
        generate_executive_summary, generate_priority_findings,
        generate_pathway_analysis, generate_full_findings,
        generate_pharmgkb_report, generate_action_summary, generate_disclaimer,
        CLINICAL_CONTEXT, PATHWAYS
    )

    # Build the data structure expected by generator
    data = {
        'findings': results['findings'],
        'pharmgkb_findings': results['pharmgkb_findings'],
        'summary': results['summary']
    }

    # Generate report parts
    report_parts = []
    report_parts.append(generate_executive_summary(data))
    report_parts.append(generate_priority_findings(results['findings']))
    report_parts.append(generate_pathway_analysis(results['findings']))
    report_parts.append(generate_full_findings(results['findings']))
    report_parts.append(generate_pharmgkb_report(results['pharmgkb_findings']))
    report_parts.append(generate_action_summary(results['findings']))
    report_parts.append(generate_disclaimer())

    full_report = "\n".join(report_parts)

    # Add subject name if provided
    if subject_name:
        full_report = full_report.replace(
            "# Exhaustive Genetic Health Report",
            f"# Exhaustive Genetic Health Report\n\n**Subject:** {subject_name}"
        )

    with open(output_path, 'w') as f:
        f.write(full_report)

def generate_disease_risk_report(findings: dict, stats: dict, genome_count: int,
                                  output_path: Path, subject_name: str = None):
    """Generate the exhaustive disease risk report."""
    print_step("Generating disease risk report")

    from generate_executive_synthesis import plain_condition_name, plain_drug_alert, explain_condition

    # Categorize findings
    categories = {
        'high_confidence': [], 'heart': [], 'metabolic': [], 'brain': [],
        'autoimmune': [], 'cancer': [], 'bones': [], 'drugs': [], 'other': []
    }

    all_pathogenic = findings['pathogenic'] + findings['likely_pathogenic']
    for f in all_pathogenic:
        trait_lower = f.get('traits', '').lower()
        if f['gold_stars'] >= 2:
            categories['high_confidence'].append(f)
        if any(k in trait_lower for k in ['heart', 'cardio', 'blood', 'cholesterol', 'hypertension', 'lipid']):
            categories['heart'].append(f)
        elif any(k in trait_lower for k in ['diabetes', 'obesity', 'metabolic', 'digestive', 'liver', 'celiac']):
            categories['metabolic'].append(f)
        elif any(k in trait_lower for k in ['alzheimer', 'parkinson', 'schizophrenia', 'bipolar', 'autism', 'brain', 'nerve']):
            categories['brain'].append(f)
        elif any(k in trait_lower for k in ['autoimmune', 'lupus', 'arthritis', 'crohn', 'thyroid']):
            categories['autoimmune'].append(f)
        elif any(k in trait_lower for k in ['cancer', 'tumor', 'carcinoma', 'melanoma']):
            categories['cancer'].append(f)
        elif any(k in trait_lower for k in ['disc', 'osteoarthritis', 'spina bifida', 'bone', 'skin']):
            categories['bones'].append(f)
        else:
            categories['other'].append(f)

    # Remove duplicates from high confidence
    seen = set()
    unique_high = []
    for f in categories['high_confidence']:
        trait = plain_condition_name(f.get('traits', ''))
        if trait not in seen:
            seen.add(trait)
            unique_high.append(f)

    report = f"""# Exhaustive Disease Risk Report

"""
    if unique_high:
        report += "### 1. The Highest-Confidence Genetic Conditions\n\n"
        report += "These are conditions where the genetic markers are the strongest (listed as \"Pathogenic\" or \"Affected\" in the report).\n\n"
        for f in unique_high:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            explanation = explain_condition(f.get('traits', 'Unknown'))
            report += f"* **{name}:** {explanation}\n"
        report += "\n"
        
    if categories['heart']:
        report += "### 2. Heart, Blood, and Circulation Risks\n\n"
        report += "They have a heavily loaded genetic profile for cardiovascular issues.\n\n"
        seen = set()
        for f in categories['heart'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['metabolic']:
        report += "### 3. Metabolic & Digestive System\n\n"
        seen = set()
        for f in categories['metabolic'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['brain']:
        report += "### 4. Brain, Nervous System, and Mental Health\n\n"
        seen = set()
        for f in categories['brain'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['autoimmune']:
        report += "### 5. Autoimmune & General Inflammatory Conditions\n\n"
        report += "Their baseline inflammation is genetically set \"high,\" making them prone to conditions where the immune system attacks the body.\n\n"
        seen = set()
        for f in categories['autoimmune'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['cancer']:
        report += "### 6. Cancer Susceptibilities\n\n"
        report += "Again, these are *susceptibilities*, not a diagnosis of cancer. Their genes just show a higher risk profile for:\n\n"
        seen = set()
        for f in categories['cancer'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['bones']:
        report += "### 7. Bones, Joints, and Physical Traits\n\n"
        seen = set()
        for f in categories['bones'][:10]:
            name = plain_condition_name(f.get('traits', 'Unknown'))
            if name not in seen:
                seen.add(name)
                explanation = explain_condition(f.get('traits', 'Unknown'))
                report += f"* **{name}:** {explanation}\n"
        report += "\n"

    if categories['drugs']:
        report += "### 8. Dangerous Medication Reactions\n\n"
        report += "This is perhaps the most immediately dangerous part of the report. If they are prescribed certain drugs, they could face severe toxicity.\n\n"
        seen = set()
        count = 0
        for f in categories['drugs']:
            drug = f.get('traits', 'Unknown').split(';')[0]
            if 'response' in drug:
                drug = drug.replace('response', '').strip()
            if drug not in seen and len(drug) > 3:
                seen.add(drug)
                report += f"* **{drug.title()}:** Because of a specific genetic quirk, your body might not process this drug normally. Standard doses could cause severe side effects or toxicity, or the drug might simply not work as intended. Always mention this to your doctor before being prescribed this medication.\n"
                count += 1
                if count >= 10: break

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"    Written to: {output_path}")


def generate_actionable_protocol(health_results: dict, disease_findings: dict,
                                  output_path, subject_name: str = None):
    """Generate comprehensive, user-friendly actionable health protocol."""
    print_step("Generating actionable health protocol (user-friendly)")

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    subject_line = f"Prepared for: **{subject_name}**\n" if subject_name else ""

    findings_dict = {f['gene']: f for f in health_results['findings']}

    report = f"""# Your Personalized Daily Action Plan
{subject_line}*Generated: {now}*

This isn't a generic health blog. This protocol is built strictly from the unique bottlenecks, strengths, and risks found in your raw DNA. 

We have stripped away the complex medical jargon. Below is exactly what you should be doing, what you should avoid, and *why* it matters specifically for your biology.

---

## 💊 The Nutrient Protocol

Based on your genetics, your body has specific deficiencies and high-risk areas. We have separated these into two categories: Clinical Supplements (concentrated doses for immediate impact) and Science-Backed Natural/Ayurvedic Sources (for long-term foundational health).

### 1. Clinical Supplements (Concentrated Doses)

"""

    supp_found = False
    
    supp_report = ""
    natural_report = "### 2. Science-Backed Natural & Ayurvedic Sources\n\n"

    # 1. MTHFR 
    if 'MTHFR' in findings_dict and findings_dict['MTHFR']['magnitude'] >= 2:
        supp_found = True
        supp_report += "* **Methylfolate (L-5-MTHF) & Methylcobalamin (B12)**\n"
        supp_report += "  * **The Dose:** 400-800mcg of Methylfolate and 1000mcg of B12 daily.\n"
        supp_report += "  * **The Why:** You have the 'MTHFR' gene variation. Your body struggles to convert standard B-vitamins into the active form your brain needs for energy.\n"
        supp_report += "  * **Pro-Tip:** Never buy cheap vitamins with 'folic acid'—your body can't process it.\n\n"
        
        natural_report += "* **Natural Folate Sources (For MTHFR):**\n"
        natural_report += "  * **Foods:** Beef liver, dark leafy greens (spinach, kale), asparagus, and avocados.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Moringa oleifera (Drumstick tree leaves) is exceptionally high in natural, highly bioavailable folate and B-vitamins.\n\n"

    # 2. Vitamin D (GC)
    if 'GC' in findings_dict and findings_dict['GC'].get('status') == 'low':
        supp_found = True
        supp_report += "* **High-Dose Vitamin D3 + K2**\n"
        supp_report += "  * **The Dose:** 2000-5000 IU of D3 daily.\n"
        supp_report += "  * **The Why:** Your body produces lower amounts of the protein that carries Vitamin D through your blood.\n\n"
        
        natural_report += "* **Natural D3 & Calcium Routing (For GC Gene):**\n"
        natural_report += "  * **Foods:** Wild-caught salmon, egg yolks, and sun-exposed mushrooms.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Shilajit (rich in fulvic acid and trace minerals) helps optimize bone density and mineral absorption, synergizing with natural sunlight exposure.\n\n"

    # 3. Omega 3 (FADS1)
    if 'FADS1' in findings_dict and findings_dict['FADS1'].get('status') == 'low_conversion':
        supp_found = True
        supp_report += "* **Marine Omega-3s (EPA/DHA)**\n"
        supp_report += "  * **The Dose:** 1-2g of high-quality fish oil or algae oil daily.\n"
        supp_report += "  * **The Why:** You lack the genetic hardware to convert plant-based Omega-3s into the EPA/DHA your brain uses.\n\n"
        
        natural_report += "* **Natural Brain Lipids (For FADS1):**\n"
        natural_report += "  * **Foods:** Mackerel, sardines, and fatty wild fish. Walnuts and chia seeds will *not* work for your specific genetic profile.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Brahmi (Bacopa monnieri) combined with high-quality Ghee (clarified butter). Ghee provides the fat backbone, while Brahmi is scientifically proven to reduce neuro-inflammation.\n\n"

    # 4. Stress (COMT)
    if 'COMT' in findings_dict and findings_dict['COMT'].get('status') == 'slow':
        supp_found = True
        supp_report += "* **Magnesium Glycinate**\n"
        supp_report += "  * **The Dose:** 300-400mg in the evening.\n"
        supp_report += "  * **The Why:** Your 'Slow COMT' gene means your brain holds onto adrenaline for a long time. Magnesium acts as a biochemical 'brake pedal'.\n\n"
        
        natural_report += "* **Natural Adrenaline Clearance (For Slow COMT):**\n"
        natural_report += "  * **Foods:** Pumpkin seeds, almonds, and cacao (all high in natural magnesium).\n"
        natural_report += "  * **Ayurvedic/Herbal:** Ashwagandha (KSM-66) and L-Theanine (from Green Tea). These are powerful adaptogens proven to lower cortisol and counteract your genetic tendency to hold onto stress hormones.\n\n"

    # 5. Liver (PEMT)
    if 'PEMT' in findings_dict:
        supp_found = True
        supp_report += "* **Choline (CDP-Choline or Alpha-GPC)**\n"
        supp_report += "  * **The Dose:** 250-500mg daily.\n"
        supp_report += "  * **The Why:** Your liver genetically struggles to produce enough choline on its own.\n\n"
        
        natural_report += "* **Natural Liver & Choline Support (For PEMT):**\n"
        natural_report += "  * **Foods:** Pasture-raised egg yolks (2-3 per day provides enough natural choline to bypass this gene flaw), beef liver.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Kutki (Picrorhiza kurroa) or Milk Thistle to support your liver's fat-processing capabilities, which are strained by your genetics.\n\n"

    # 6. Diabetes/Metabolic Risk Additions
    has_diabetes_risk = 'TCF7L2' in findings_dict or any('diabetes' in f.get('traits', '').lower() for f in disease_findings.get('pathogenic', []) + disease_findings.get('risk_factor', []))
    if has_diabetes_risk:
        supp_found = True
        supp_report += "* **Berberine HCL (The 'Natural Metformin')**\n"
        supp_report += "  * **The Dose:** 500mg before your largest carbohydrate meals.\n"
        supp_report += "  * **The Why:** You have a severely elevated genetic risk for Type 2 Diabetes and insulin resistance. Berberine is clinically proven to activate AMPK (your body's metabolic master switch) and shuttle sugar out of your blood and into your muscles.\n\n"
        
        natural_report += "* **Natural Blood Sugar Control (For Diabetes Risk):**\n"
        natural_report += "  * **Foods:** Ceylon Cinnamon (1 tsp daily), Apple Cider Vinegar (1 tbsp in water before meals).\n"
        natural_report += "  * **Ayurvedic/Herbal:** Gymnema Sylvestre (often called 'Gurmar', meaning 'destroyer of sugar' in Hindi) and Bitter Melon (Karela). Both are legendary Ayurvedic interventions clinically shown to lower HbA1c and curb sugar cravings.\n\n"

    # 7. Cardiovascular & Hypertension Risk Additions
    has_cardio_risk = any(g in findings_dict for g in ['AGTR1', 'ACE', 'AGT', 'GNB3']) or any('heart' in f.get('traits', '').lower() or 'hypertension' in f.get('traits', '').lower() for f in disease_findings.get('risk_factor', []))
    if has_cardio_risk:
        supp_found = True
        supp_report += "* **Coenzyme Q10 (Ubiquinol) & L-Citrulline**\n"
        supp_report += "  * **The Dose:** 100-200mg Ubiquinol, 3-6g L-Citrulline daily.\n"
        supp_report += "  * **The Why:** You have multiple genetic triggers for high blood pressure and cardiovascular plaque. CoQ10 protects the heart muscle from oxidative stress, and L-Citrulline drastically increases nitric oxide to keep your blood vessels relaxed and wide open.\n\n"
        
        natural_report += "* **Natural Cardiovascular Defense (For Heart/BP Risk):**\n"
        natural_report += "  * **Foods:** Beets and Arugula (highest natural sources of dietary nitrates to dilate blood vessels), Pomegranate juice.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Terminalia Arjuna (Arjuna Bark) and aged Garlic extract. Arjuna is the most revered Ayurvedic herb for the heart, scientifically proven to improve cardiac muscle function and lower blood pressure.\n\n"

    # 8. High Systemic Inflammation Additions
    has_inflammation = 'IL6' in findings_dict or 'CRP' in findings_dict or any('autoimmune' in f.get('traits', '').lower() for f in disease_findings.get('risk_factor', []))
    if has_inflammation:
        supp_found = True
        supp_report += "* **Curcumin Phytosome (High Absorption)**\n"
        supp_report += "  * **The Dose:** 500-1000mg daily.\n"
        supp_report += "  * **The Why:** Your genetic baseline for systemic inflammation (like IL-6) is set unnaturally high. High absorption Curcumin acts as a master anti-inflammatory switch, downregulating inflammatory cytokines before they cause joint or tissue damage.\n\n"
        
        natural_report += "* **Natural Anti-Inflammatory Baseline (For High Inflammation):**\n"
        natural_report += "  * **Foods:** Bone broth (rich in collagen and glycine to heal the gut), wild blueberries.\n"
        natural_report += "  * **Ayurvedic/Herbal:** Turmeric Root (must be consumed with black pepper/piperine and fat like Ghee for absorption) and Boswellia Serrata (Indian Frankincense). Together, these form the ultimate Ayurvedic duo for crushing joint pain and systemic inflammation.\n\n"

    if not supp_found:
        report += "Your genetics don't show any severe nutrient processing bottlenecks! A standard, high-quality multivitamin is sufficient.\n\n"
    else:
        report += supp_report + "\n" + natural_report

    report += "---\n\n## 🥗 How You Should Actually Eat\n\n"

    diet_found = False

    if 'APOA2' in findings_dict and findings_dict['APOA2'].get('status') == 'sensitive':
        diet_found = True
        report += "* **Treat Saturated Fat like a toxin for weight gain.**\n"
        report += "  * **The Why:** Because of your APOA2 gene, your body is hyper-sensitive to saturated fat. Eating butter, fatty red meat, and coconut oil will lead to rapid weight gain. Stick to olive oil and avocados.\n\n"

    if 'MTHFR' in findings_dict and findings_dict['MTHFR']['magnitude'] >= 2:
        diet_found = True
        report += "* **Aggressively hunt for natural Folate.**\n"
        report += "  * **The Why:** Avoid cheap processed bread and cereals fortified with synthetic 'folic acid', as it clogs up your system.\n\n"

    if 'MCM6/LCT' in findings_dict and 'intolerant' in findings_dict['MCM6/LCT'].get('status', ''):
        diet_found = True
        report += "* **Ditch the Dairy.**\n"
        report += "  * **The Why:** You are genetically lactose intolerant. Dairy is likely causing low-grade systemic inflammation and bloating in your gut.\n\n"

    caffeine_issues = []
    if 'CYP1A2' in findings_dict and findings_dict['CYP1A2'].get('status') in ['slow', 'intermediate']:
        caffeine_issues.append("slow caffeine metabolizer")
    if 'COMT' in findings_dict and findings_dict['COMT'].get('status') == 'slow':
        caffeine_issues.append("slow adrenaline clearance")

    if caffeine_issues:
        diet_found = True
        report += f"* **Hard stop on Caffeine after 10 AM.**\n"
        report += f"  * **The Why:** Because you are a {caffeine_issues[0]}, caffeine stays in your bloodstream far longer than average, silently destroying your deep sleep architecture.\n\n"

    if not diet_found:
        report += "Your genetics don't dictate any extreme dietary restrictions. Focus on a standard whole-food, anti-inflammatory diet.\n\n"


    report += "---\n\n## 🏃‍♂️ How You Should Move and Recover\n\n"

    life_found = False

    if 'ACTN3' in findings_dict:
        life_found = True
        status = findings_dict['ACTN3'].get('status', '')
        if status == 'endurance':
            report += "* **Focus on high-volume Endurance training.**\n"
            report += "  * **The Why:** Your muscle fibers are genetically biased toward endurance (aerobic) capacity rather than explosive power. You will recover much faster from high-rep or distance training.\n\n"
        elif status == 'power':
            report += "* **Focus on explosive Power and Sprint training.**\n"
            report += "  * **The Why:** You have the 'sprinter gene.' Your muscle fibers are built for explosive, heavy, high-intensity output.\n\n"

    if 'ARNTL' in findings_dict:
        life_found = True
        report += "* **Fiercely protect your Circadian Rhythm.**\n"
        report += "  * **The Why:** You have a genetically weaker internal clock. You need strict, consistent sleep and wake times, even on weekends.\n\n"

    if 'MC1R' in findings_dict:
        life_found = True
        report += "* **Aggressive Sun Protection.**\n"
        report += "  * **The Why:** Your skin is genetically highly vulnerable to UV damage. You will experience accelerated skin aging if you don't use daily SPF 30+.\n\n"

    if not life_found:
        report += "Your baseline physiology is well-rounded. Follow standard guidelines for 150+ minutes of aerobic work and 2 days of strength training per week.\n\n"


    report += "---\n\n## 🩺 What To Tell Your Doctor (Lab Tests & Meds)\n\n"
    report += "Do not wait until you are sick to test these. Demand these specific lab panels at your next physical based on your genetic blind spots.\n\n"

    report += "### 🩸 Blood Tests to Demand Annually\n"
    
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
            report += f"{l}\n"
    else:
        report += "* **Standard Comprehensive Metabolic Panel:** Your genetics don't point to any hidden systemic crises.\n"

    report += "\n### ⚠️ Dangerous Medication Warnings\n"
    report += "If a doctor ever prescribes you a new drug, specifically check if it interacts with these genetic quirks.\n\n"

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
                report += f"* **Watch out for {drugs}:** Because of a quirk in your {f['gene']} gene, your body might metabolize these drugs too fast or too slow. Ask your doctor to adjust the dose based on pharmacogenomics.\n"
                count += 1
                if count >= 8: break
    else:
        report += "* You have no high-risk pharmaceutical sensitivities detected in this scan.\n"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"    Written to: {output_path}")

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_full_analysis(genome_path: Path = None, subject_name: str = None, outdir: Path = None):
    """Run the complete genetic analysis pipeline."""

    print_header("FULL GENETIC HEALTH ANALYSIS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Default genome path
    if genome_path is None:
        genome_path = DATA_DIR / "genome.txt"

    if outdir is None:
        outdir = DEFAULT_REPORTS_DIR

    if not genome_path.exists():
        print(f"\nERROR: Genome file not found: {genome_path}")
        print("Please provide a valid 23andMe genome file.")
        sys.exit(1)

    # Create reports directory
    outdir.mkdir(exist_ok=True, parents=True)

    # Load genome
    genome_by_rsid, genome_by_position = load_genome(genome_path)

    # Load PharmGKB
    pharmgkb = load_pharmgkb()

    # Run lifestyle/health analysis
    health_results = analyze_lifestyle_health(genome_by_rsid, pharmgkb)

    # Save intermediate results for exhaustive report generator
    results_json = {
        'findings': health_results['findings'],
        'pharmgkb_findings': health_results['pharmgkb_findings'],
        'summary': health_results['summary'],
    }
    intermediate_path = outdir / "comprehensive_results.json"
    with open(intermediate_path, 'w') as f:
        json.dump(results_json, f, indent=2)

    # Generate exhaustive genetic report
    genetic_report_path = outdir / "EXHAUSTIVE_GENETIC_REPORT.md"
    generate_exhaustive_genetic_report(health_results, genetic_report_path, subject_name)

    # Run disease risk analysis
    disease_findings, disease_stats = load_clinvar_and_analyze(genome_by_position)

    # Generate disease risk report
    if disease_findings:
        disease_report_path = outdir / "EXHAUSTIVE_DISEASE_RISK_REPORT.md"
        generate_disease_risk_report(disease_findings, disease_stats, len(genome_by_rsid),
                                      disease_report_path, subject_name)

    # 6. Actionable Health Protocol
    print_step("Generating actionable health protocol (comprehensive)")
    protocol_path = outdir / "ACTIONABLE_HEALTH_PROTOCOL_V3.md"
    generate_actionable_protocol(health_results, disease_findings, protocol_path, subject_name)

    # 7. Executive Synthesis
    print_step("Generating executive synthesis")
    synthesis_path = outdir / "EXECUTIVE_SYNTHESIS_REPORT.md"
    generate_synthesis_report(health_results, disease_findings, synthesis_path, subject_name)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    
    print_header("ANALYSIS COMPLETE")
    print(f"\nReports generated in: {outdir}\n")
    
    print("  1. EXHAUSTIVE_GENETIC_REPORT.md")
    print(f"     - {len(health_results['findings'])} lifestyle/health findings")
    print(f"     - {len(health_results['pharmgkb_findings'])} drug-gene interactions\n")
    
    print("  2. EXHAUSTIVE_DISEASE_RISK_REPORT.md")
    print(f"     - {len(disease_findings.get('pathogenic', []))} pathogenic variants")
    print(f"     - {len(disease_findings.get('likely_pathogenic', []))} likely pathogenic")
    print(f"     - {len(disease_findings.get('risk_factor', []))} risk factors\n")
    
    print("  3. ACTIONABLE_HEALTH_PROTOCOL_V3.md")
    print("     - Comprehensive protocol (lifestyle + disease risk + carrier status)\n")

    print("  4. EXECUTIVE_SYNTHESIS_REPORT.md")
    print("     - Ultimate synthesized executive summary\n")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return {
        'health_results': health_results,
        'disease_findings': disease_findings,
        'disease_stats': disease_stats
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run full genetic health analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_full_analysis.py                        # Use default genome.txt
  python run_full_analysis.py /path/to/genome.txt   # Custom genome file
  python run_full_analysis.py --name "John Doe"     # Add name to reports
        """
    )
    parser.add_argument('genome', nargs='?', type=Path, default=None,
                       help='Path to 23andMe genome file (default: data/genome.txt)')
    parser.add_argument('--name', '-n', type=str, default=None,
                       help='Subject name to include in reports')

    args = parser.parse_args()

    run_full_analysis(args.genome, args.name)


if __name__ == "__main__":
    main()
