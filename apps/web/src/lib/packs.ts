// Product catalogue. amount_inr is in PAISE (₹1 = 100).
export type Pack = {
  id: string;
  name: string;
  tagline: string;
  amount_inr: number; // paise
  includes: string[];
  // Report section add-ons this tier generates (keys match narrative.py
  // addon_builders). Stored on the order so the report depth matches the tier.
  report_addons: string[];
  pages: string; // rough page count, for marketing
};

export const PACKS: Record<string, Pack> = {
  core: {
    id: "core",
    name: "Core Reading",
    tagline: "Your chart decoded — who you are, the chapter you're in, and what to do next.",
    amount_inr: 10800, // ₹108
    pages: "~30 pages",
    includes: [
      "Your birth chart + every classical diagram",
      "The Arc So Far — your life story, decoded",
      "This Chapter of Your Life",
      "Your Hidden Strengths (yogas)",
      "Structural Challenges (doshas)",
      "What To Do Next — three precise moves",
    ],
    report_addons: [],
  },
  full: {
    id: "full",
    name: "Full Life Reading",
    tagline: "Everything in Core, plus the predictive spine — your past, your decades, your year ahead.",
    amount_inr: 25000, // ₹250
    pages: "~55 pages",
    includes: [
      "Everything in Core",
      "Answer to your personal question",
      "Past 5 Years — decoded against your dashas",
      "Next 5 Years — the strategic map",
      "Lifetime Overview — your 120-year arc",
      "Sade Sati deep-dive (when active)",
    ],
    report_addons: ["past_5_years", "next_5_years", "lifetime"],
  },
  super: {
    id: "super",
    name: "Complete Reading",
    tagline: "The whole operating system — every life domain, deep-dived and dated.",
    amount_inr: 35000, // ₹350
    pages: "~85 pages",
    includes: [
      "Everything in Full",
      "Career & Wealth deep-dives",
      "Relationships, Marriage & Health",
      "Foreign, Property, Business, Education",
      "Children & Spiritual Path",
      "Gemstone prescription + 12-month Muhurta calendar",
    ],
    report_addons: [
      "past_5_years",
      "next_5_years",
      "lifetime",
      "career_deep_dive",
      "wealth_deep_dive",
      "relationships_deep_dive",
      "health_deep_dive",
      "spiritual_deep_dive",
      "children_deep_dive",
      "education_deep_dive",
      "foreign_settlement",
      "property_vehicle",
      "business_launch",
      "gem_prescription",
      "muhurta_calendar",
    ],
  },
};

export const ADDONS: Record<string, { name: string; amount_inr: number }> = {
  career: { name: "Career & Money", amount_inr: 39900 },
  marriage: { name: "Relationships & Marriage", amount_inr: 39900 },
  foreign: { name: "Foreign Settlement", amount_inr: 29900 },
  health: { name: "Health & Body", amount_inr: 29900 },
  gem: { name: "Gemstone Prescription", amount_inr: 19900 },
};

export function packTotal(packId: string, addons: string[] = []): number {
  const base = PACKS[packId]?.amount_inr ?? 0;
  const extra = addons.reduce((s, a) => s + (ADDONS[a]?.amount_inr ?? 0), 0);
  return base + extra;
}
