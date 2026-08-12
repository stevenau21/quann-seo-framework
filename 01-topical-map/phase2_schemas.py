#!/usr/bin/env python3
"""
Phase 2 Engine Task: Produce JSON-LD Schemas + sameAs Manifest
Koray Framework: Knowledge Graph & Structured Data (14 grounded rules)
Resource: ENGINE ONLY — zero human allocation required
"""
import json

# ─── CORRECTED ENTITY DATA (Walzel Properties) ───────────────────────────────

schemas = {
    "homepage": {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "RealEstateAgent",
                "@id": "https://quann.homes/#agent",
                "name": "Quan Nguyen",
                "alternateName": ["Minh Quan Nguyen", "Quan T. Nguyen"],
                "identifier": {
                    "@type": "PropertyValue",
                    "propertyID": "TX Real Estate License",
                    "value": "0774451"
                },
                "description": "Quan Nguyen is a licensed Texas REALTOR® specializing in buyer representation across Katy, Houston, Austin, Dallas, and the Rio Grande Valley. As a Walzel Properties agent leading The Quantum Team, Quan delivers an AI-powered multilingual home buying experience with a documented system proven across 75+ transactions.",
                "url": "https://quann.homes",
                "telephone": "+1-832-400-3152",
                "email": "quan@thequantumteam.net",
                "image": "https://quann.homes/images/quan-nguyen.jpg",
                "logo": "https://quann.homes/images/quantum-team-logo.png",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Katy",
                    "addressRegion": "TX",
                    "postalCode": "77494",
                    "addressCountry": "US"
                },
                "areaServed": [
                    {"@type": "City", "name": "Katy", "sameAs": "https://www.wikidata.org/wiki/Q...katy"},
                    {"@type": "City", "name": "Houston", "sameAs": "https://www.wikidata.org/wiki/Q16555"},
                    {"@type": "City", "name": "Austin", "sameAs": "https://www.wikidata.org/wiki/Q16559"},
                    {"@type": "City", "name": "Dallas", "sameAs": "https://www.wikidata.org/wiki/Q16557"},
                    {"@type": "State", "name": "Rio Grande Valley", "sameAs": "https://www.wikidata.org/wiki/Q...rgv"}
                ],
                "memberOf": [
                    {"@type": "Organization", "name": "National Association of REALTORS® (NAR)", "sameAs": "https://www.nar.realtor/"},
                    {"@type": "Organization", "name": "Texas Association of REALTORS® (TAR)", "sameAs": "https://www.texasrealestate.com/"},
                    {"@type": "Organization", "name": "Houston Association of REALTORS® (HAR)", "sameAs": "https://www.har.com/"},
                    {"@type": "Organization", "name": "Katy Area Chamber of Commerce", "sameAs": "https://www.katychamber.com/"},
                    {"@type": "Organization", "name": "Asian Real Estate Association of America (AREAA)", "sameAs": "https://areaa.org/"}
                ],
                "hasCredential": [
                    {"@type": "EducationalOccupationalCredential", "name": "ABR — Accredited Buyer's Representative", "recognizedBy": {"@type": "Organization", "name": "NAR"}},
                    {"@type": "EducationalOccupationalCredential", "name": "GRI — Graduate, REALTOR® Institute"},
                    {"@type": "EducationalOccupationalCredential", "name": "C2EX — Commitment to Excellence (NAR)"},
                    {"@type": "EducationalOccupationalCredential", "name": "MRP — Military Relocation Professional"},
                    {"@type": "EducationalOccupationalCredential", "name": "PSA — Pricing Strategy Advisor"}
                ],
                "knowsLanguage": [
                    {"@type": "Language", "name": "English"},
                    {"@type": "Language", "name": "Vietnamese"}
                ],
                "knowsAbout": [
                    {"@type": "Thing", "name": "First-time home buying in Texas"},
                    {"@type": "Thing", "name": "Builder incentives and new construction negotiation"},
                    {"@type": "Thing", "name": "Texas property taxes — MUD and PID districts"},
                    {"@type": "Thing", "name": "Down payment assistance programs"},
                    {"@type": "Thing", "name": "Cross-Texas relocation"},
                    {"@type": "Thing", "name": "AI-powered multilingual real estate advisory"}
                ],
                "worksFor": {
                    "@type": "RealEstateAgent",
                    "name": "Walzel Properties",
                    "url": "https://www.walzelproperties.com/"
                },
                "brand": {
                    "@type": "Brand",
                    "name": "The Quantum Team"
                },
                "sameAs": []  # Populate from sameAs manifest after verification
            }
        ]
    },
    "about_page": {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "about": {"@id": "https://quann.homes/#agent"},
        "mainEntity": {"@id": "https://quann.homes/#agent"},
        "dateCreated": "2025-01-01",
        "dateModified": "2026-05-25"
    },
    "article_template": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{{PAGE_TITLE}}",
        "author": {"@id": "https://quann.homes/#agent"},
        "about": {"@type": "Thing", "name": "{{PRIMARY_ENTITY}}"},
        "datePublished": "{{PUBLISH_DATE}}",
        "dateModified": "{{MODIFIED_DATE}}",
        "publisher": {
            "@type": "Organization",
            "name": "The Quantum Team",
            "url": "https://quann.homes"
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": "{{PAGE_URL}}"
        }
    },
    "local_business": {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "https://quann.homes/#business",
        "name": "The Quantum Team at Walzel Properties",
        "url": "https://quann.homes",
        "telephone": "+1-832-400-3152",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Katy",
            "addressRegion": "TX",
            "postalCode": "77494",
            "addressCountry": "US"
        },
        "areaServed": [
            "Katy, TX", "Houston, TX", "Austin, TX", "Dallas, TX", "Rio Grande Valley, TX"
        ],
        "employee": {"@id": "https://quann.homes/#agent"}
    }
}

# ─── sameAs MANIFEST ──────────────────────────────────────────────────────────

sameas_manifest = {
    "verified": {
        "website": "https://quann.homes",
        "email": "quan@thequantumteam.net",
        "phone": "+1-832-400-3152",
        "instagram": "https://instagram.com/quann.realtor",
        "telegram": "https://t.me/QuannBot"
    },
    "confirmed_exists_needs_verification": {
        "facebook": "https://www.facebook.com/quann.realtor",
        "har": "https://www.har.com/quan-nguyen/agent_XXXXXX",
        "linkedin_personal": "https://www.linkedin.com/in/quan-nguyen-realestate/",
        "linkedin_business": "https://www.linkedin.com/in/quan-nguyen-elevatus/",
        "realty_com": "https://www.realty.com/agent/quan-nguyen/XXXXXX"
    },
    "needs_creation": [
        {
            "platform": "Google Business Profile",
            "priority": "CRITICAL",
            "name_format": "Quan Nguyen — The Quantum Team at Walzel Properties",
            "category": "Real Estate Agent",
            "service_area": "Katy, TX (primary); Houston, Austin, Dallas, Rio Grande Valley",
            "notes": "No physical storefront — configure as service-area business"
        },
        {
            "platform": "Wikidata",
            "priority": "CRITICAL",
            "item_type": "Q5 (human)",
            "occupation": "Q1860857 (real estate agent)",
            "employer": "Walzel Properties",
            "notes": "This is the PRIMARY external entity signal. Google ingests Wikidata as ground truth."
        },
        {
            "platform": "Zillow",
            "priority": "HIGH",
            "name_format": "Quan Nguyen",
            "notes": "Create agent profile with bio, link to quann.homes. Add 3+ reviews."
        },
        {
            "platform": "Realtor.com",
            "priority": "HIGH",
            "name_format": "Quan Nguyen",
            "brokerage": "Walzel Properties",
            "notes": "Claim profile. Update brokerage from any stale value."
        },
        {
            "platform": "Crunchbase",
            "priority": "MEDIUM",
            "entity": "The Quantum Team",
            "industry": "Real Estate",
            "notes": "Create organization profile. Link to quann.homes."
        },
        {
            "platform": "Nextdoor",
            "priority": "MEDIUM",
            "notes": "Claim agent profile in Katy neighborhood."
        },
        {
            "platform": "YouTube",
            "priority": "LOW",
            "notes": "Create channel linked to quann.homes. Publish 3+ market update videos."
        }
    ],
    "contaminated_profiles_need_fix": [
        {
            "platform": "LinkedIn (business profile)",
            "current_brokerage": "Elevatus",
            "action": "Update to Walzel Properties OR close duplicate"
        },
        {
            "platform": "LinkedIn (Truss profile)",
            "current_brokerage": "Truss",
            "action": "Close duplicate — keep only ONE LinkedIn profile"
        },
        {
            "platform": "HAR.com",
            "current_brokerage": "Unknown (likely stale)",
            "action": "Verify via HAR member portal, update to Walzel Properties"
        },
        {
            "platform": "Realty.com",
            "current_brokerage": "Forever Realty",
            "action": "Claim and update to Walzel Properties"
        }
    ],
    "action_sequence": [
        "1. Fix LinkedIns: Close Elevatus + Truss duplicates. Keep one profile with Walzel Properties.",
        "2. Create GBP: Google Business Profile with correct NAP + Walzel Properties.",
        "3. Create Zillow: New agent profile with Walzel Properties + quann.homes link.",
        "4. Create Wikidata: This is the anchor. Google trusts Wikidata as ground truth.",
        "5. Fix HAR.com + Realty.com: Update brokerage on existing profiles.",
        "6. Create Realtor.com: Fresh profile with correct data.",
        "7. Add sameAs to schema: Populate the empty sameAs[] array once all URLs are confirmed.",
        "8. Create Crunchbase (The Quantum Team entity).",
        "9. Create Nextdoor, YouTube (lower priority)."
    ]
}

# ─── ENTITY DESCRIPTIONS (Koray KG Pattern) ──────────────────────────────────

entity_descriptions = {
    "quan_nguyen": {
        "definitive_description": "Quan Nguyen is a licensed Texas REALTOR® (license #0774451) with Walzel Properties, leading The Quantum Team. He specializes in buyer representation across the Katy-Houston metro area with extended service in Austin, Dallas, and the Rio Grande Valley. He holds five professional certifications (ABR, GRI, C2EX, MRP, PSA) and has closed 75+ transactions. His practice is 85% buyer-focused, serving first-time homebuyers, out-of-state relocators, and new-construction clients. Quan operates an AI-powered multilingual advisory service enabling seamless communication with buyers in any language.",
        "related_entities": [
            "Walzel Properties (employer/brokerage)",
            "Katy, Texas (primary service area)",
            "Houston Association of REALTORS® (professional association)",
            "The Quantum Team (brand)",
            "Texas Real Estate Commission (licensing body)"
        ],
        "no_subjective_opinions": True,
        "pattern": "definitive → answers what/who → includes related entities → zero subjective language"
    },
    "walzel_properties": {
        "definitive_description": "Walzel Properties is a licensed Texas real estate brokerage operating across the Houston metropolitan area.",
        "related_entities": [
            "Quan Nguyen (agent)",
            "Texas Real Estate Commission (regulatory body)",
            "Houston Association of REALTORS® (MLS access)"
        ],
        "no_subjective_opinions": True
    }
}

# ─── KG PANEL TRACKING CONFIG ────────────────────────────────────────────────

kg_tracking = {
    "locations_to_track": [
        "US (default) — Google.com",
        "US-TX — Google.com region=Texas",
        "US-TX-Houston — Google.com locality=Houston",
        "US-VN — Google.com language=Vietnamese (for Vietnamese-American audience)"
    ],
    "queries_to_monitor": [
        "Quan Nguyen real estate",
        "Quan Nguyen real estate Katy TX",
        "The Quantum Team Walzel Properties",
        "Quann Homes",
        "Quan Nguyen Walzel Properties"
    ],
    "success_criteria": "Knowledge Panel appears for brand-name queries within 4-8 weeks of Wikidata + GBP creation"
}

# --- OUTPUT ---
output = {
    "metadata": {
        "engine": "Phase 2 — Knowledge Graph & Structured Data",
        "koray_framework": "knowledge-graph-structured-data",
        "grounded_rules_applied": 14,
        "artifacts": ["homepage_schema", "about_page_schema", "article_template", "local_business_schema", "sameas_manifest", "entity_descriptions", "kg_tracking"]
    },
    "schemas": schemas,
    "sameas_manifest": sameas_manifest,
    "entity_descriptions": entity_descriptions,
    "kg_tracking": kg_tracking
}

with open("/home/steve/SEO-quann.homes/06-topical-map/phase2-schemas.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Phase 2 engine output: {len(json.dumps(output))} bytes")
print(f"Schemas: {len(schemas)} generated")
print(f"sameAs entries: {len(sameas_manifest['verified'])} verified, {len(sameas_manifest['needs_creation'])} needed")
print(f"Contaminated profiles: {len(sameas_manifest['contaminated_profiles_need_fix'])}")
