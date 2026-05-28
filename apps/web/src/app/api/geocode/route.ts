import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

// Server-side geocode proxy — keeps the Google key off the client.
// GET ?q=City → { results: [{ description, lat, lng }] }
export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q")?.trim();
  if (!q || q.length < 3) return NextResponse.json({ results: [] });
  const key = process.env.GOOGLE_PLACES_API_KEY;
  if (!key) return NextResponse.json({ error: "places key not set" }, { status: 500 });

  // Geocoding returns formatted_address + lat/lng in one call — perfect for
  // auto-filling the birth-place + coordinates together.
  const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(q)}&key=${key}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.status !== "OK") {
    return NextResponse.json({ results: [], status: data.status });
  }
  const results = (data.results || []).slice(0, 5).map((r: any) => ({
    description: r.formatted_address,
    lat: r.geometry?.location?.lat,
    lng: r.geometry?.location?.lng,
  }));
  return NextResponse.json({ results });
}
