import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { supabaseAdmin } from "@/lib/supabase";
import { packTotal, PACKS } from "@/lib/packs";

export const runtime = "nodejs";

const OrderInput = z.object({
  full_name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().optional(),
  gender: z.string().optional(),
  birth_datetime: z.string(), // ISO with tz
  birth_latitude: z.number(),
  birth_longitude: z.number(),
  birth_place_name: z.string().optional(),
  timezone: z.string().default("Asia/Kolkata"),
  pack_id: z.string(),
  addons: z.array(z.string()).default([]),
  user_question: z.string().optional(),
});

// POST → creates a los_orders row, returns { orderId, amount_inr }.
export async function POST(req: NextRequest) {
  try {
    const json = await req.json();
    const input = OrderInput.parse(json);
    const pack = PACKS[input.pack_id];
    if (!pack) {
      return NextResponse.json({ error: "invalid pack_id" }, { status: 400 });
    }
    const amount = packTotal(input.pack_id, input.addons);
    // The report sections this tier generates (drives report depth downstream).
    const reportAddons = Array.from(new Set([...pack.report_addons, ...input.addons]));
    const sb = supabaseAdmin();
    const { data, error } = await sb
      .from("los_orders")
      .insert({
        full_name: input.full_name,
        email: input.email,
        phone: input.phone ?? null,
        gender: input.gender ?? null,
        birth_datetime: input.birth_datetime,
        birth_latitude: input.birth_latitude,
        birth_longitude: input.birth_longitude,
        birth_place_name: input.birth_place_name ?? null,
        timezone: input.timezone,
        pack_id: input.pack_id,
        addons: reportAddons,
        user_question: input.user_question ?? null,
        amount_inr: amount,
        status: "created",
      })
      .select("id, amount_inr")
      .single();
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ orderId: data.id, amount_inr: data.amount_inr });
  } catch (e: any) {
    return NextResponse.json({ error: String(e?.message || e) }, { status: 400 });
  }
}
