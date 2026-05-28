import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  const orderId = req.nextUrl.searchParams.get("order_id") || "";
  return NextResponse.redirect(`${site}/thanks?status=failed&order_id=${orderId}`, 303);
}
