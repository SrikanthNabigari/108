import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  const form = await req.formData();
  const orderId = String(form.get("udf1") || form.get("txnid") || "");
  return NextResponse.redirect(`${site}/thanks?status=failed&order_id=${orderId}`, 303);
}

export async function GET() {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  return NextResponse.redirect(`${site}/thanks?status=failed`, 303);
}
