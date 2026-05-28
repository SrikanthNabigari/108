"""Nadi Jyotish API endpoints — CKN, Nadi Amsha, Sudarshana Chakra, Karakamsha, Kalachakra."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CKNRequest(BaseModel):
    natal_planets: dict
    current_jupiter_sign: str
    moon_rashi: str | None = None


class NadiAmshaRequest(BaseModel):
    natal_planets: dict
    lagna_longitude: float | None = None


class SensitivePointsRequest(BaseModel):
    natal_planets: dict
    lagna_rashi: str
    lagna_longitude: float | None = None


class SudarshanaRequest(BaseModel):
    natal_planets: dict
    lagna_rashi: str
    moon_rashi: str
    sun_rashi: str


class KarakamshnaRequest(BaseModel):
    natal_planets: dict
    d9_planets: dict | None = None


class NakshatraPadaRequest(BaseModel):
    planets: dict


class KalachakraRequest(BaseModel):
    birth_datetime: str
    moon_longitude: float
    query_datetime: str | None = None
    periods_count: int = 12


@router.post("/chandra-kala-nadi")
async def chandra_kala_nadi_endpoint(request: CKNRequest) -> dict:
    """
    Chandra Kala Nadi reading — planet combinations + Jupiter timing.

    Based on Deva Keralam. Reads natal planet conjunctions and predicts
    life events activated when Jupiter transits each sign.
    """
    try:
        from packages.self.src.chandra_kala_nadi import get_ckn_reading

        return get_ckn_reading(
            request.natal_planets,
            request.current_jupiter_sign,
            request.moon_rashi,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/nadi-amsha")
async def nadi_amsha_endpoint(request: NadiAmshaRequest) -> dict:
    """
    Nadi Amsha (D-150) chart — finest divisional chart, 0.2° per part.

    Used in Nadi Jyotish and KP sublord analysis.
    Requires birth time accurate to ±30 seconds.
    """
    try:
        from packages.self.src.nadi_amsha_interpreter import get_nadi_amsha_chart

        return get_nadi_amsha_chart(
            request.natal_planets,
            request.lagna_longitude,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/nadi-amsha/position")
async def nadi_amsha_position(longitude: float) -> dict:
    """Get D-150 Nadi Amsha position for a single longitude."""
    try:
        from packages.self.src.nadi_amsha_interpreter import calculate_nadi_amsha_position

        return calculate_nadi_amsha_position(longitude)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/kp-sublord")
async def kp_sublord(longitude: float, house_num: int | None = None) -> dict:
    """Get KP sublord for any longitude (house cusp or planet position)."""
    try:
        from packages.self.src.nadi_amsha_interpreter import get_kp_sublord

        return get_kp_sublord(longitude, house_num)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sensitive-points")
async def sensitive_points_endpoint(request: SensitivePointsRequest) -> dict:
    """
    Sensitive points (Sphutas): Bhrigu Bindu, Indu Lagna, Sree Lagna.

    Classical timing and wealth trigger points from BPHS and Brighu Nadi tradition.
    """
    try:
        from packages.self.src.sensitive_points import get_all_sensitive_points

        return get_all_sensitive_points(
            request.natal_planets,
            request.lagna_rashi,
            request.lagna_longitude,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sudarshana-chakra")
async def sudarshana_chakra_endpoint(request: SudarshanaRequest) -> dict:
    """Sudarshana Chakra — triple-wheel analysis from Lagna, Moon, Sun."""
    try:
        from packages.self.src.sudarshana_chakra import get_sudarshana_chakra

        return get_sudarshana_chakra(
            request.natal_planets,
            request.lagna_rashi,
            request.moon_rashi,
            request.sun_rashi,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/karakamsha")
async def karakamsha_endpoint(request: KarakamshnaRequest) -> dict:
    """Karakamsha Lagna analysis — soul-level karma from BPHS Chapter 35."""
    try:
        from packages.self.src.karakamsha import analyze_karakamsha

        return analyze_karakamsha(request.natal_planets, request.d9_planets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/nakshatra-padas")
async def nakshatra_padas_endpoint(request: NakshatraPadaRequest) -> dict:
    """Nakshatra Pada (108 divisions) analysis — vargottama + pushkara detection."""
    try:
        from packages.cosmos.src.nakshatras import get_chart_pada_summary

        return get_chart_pada_summary(request.planets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/kalachakra-dasha")
async def kalachakra_dasha_endpoint(request: KalachakraRequest) -> dict:
    """Kalachakra Dasha — sign-based 173-year cycle from BPHS Chapter 46."""
    try:
        from packages.context.src.kalachakra_dasha import get_kalachakra_dasha_periods

        return get_kalachakra_dasha_periods(
            request.birth_datetime,
            request.moon_longitude,
            request.query_datetime,
            request.periods_count,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
