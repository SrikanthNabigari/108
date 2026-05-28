// Product catalogue. amount_inr is in PAISE (₹1 = 100).
export type Pack = {
  id: string;
  name: string;
  tagline: string;
  amount_inr: number; // paise
  includes: string[];
};

export const PACKS: Record<string, Pack> = {
  core: {
    id: "core",
    name: "Core Reading",
    tagline: "Your chart decoded — who you are, the chapter you're in, what to do next.",
    amount_inr: 99900, // ₹999
    includes: [
      "Birth chart + all diagrams",
      "The Arc So Far",
      "This Chapter of Your Life",
      "Your Hidden Strengths",
      "Structural Challenges",
      "What To Do Next",
    ],
  },
  full: {
    id: "full",
    name: "Full Life Reading",
    tagline: "Everything in Core + the predictive Life Story Spine + your submitted question.",
    amount_inr: 199900, // ₹1,999
    includes: [
      "Everything in Core",
      "Answer to your personal question",
      "Life Story Spine — 20-year forecast",
      "Year-Ahead month-by-month",
      "Sade Sati deep-dive",
    ],
  },
  super: {
    id: "super",
    name: "Super Reading",
    tagline: "The complete operating system — all 15 deep-dive add-ons.",
    amount_inr: 399900, // ₹3,999
    includes: [
      "Everything in Full",
      "Career, Wealth, Marriage, Health add-ons",
      "Foreign, Property, Business, Education",
      "Children, Spiritual, Gemstone, Muhurta calendar",
      "Lifetime overview + Past/Next 5 years",
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
