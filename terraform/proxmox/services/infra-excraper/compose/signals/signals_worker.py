"""
signals-worker: Servicio de enriquecimiento de leads
Responsable de: Google Maps, PageSpeed, Web signals

Puerto: 3001
Arquitectura: infra-excraper (LXC 620) - 192.168.1.120:3001
"""
from flask import Flask, request, jsonify
import os
import requests
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# API Keys
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_KEY", "")
GOOGLE_PAGESPEED_API_KEY = os.getenv("PAGESPEED_KEY", "")


# ============================================================
# HELPER: Hash de señales
# ============================================================

def hash_signals(data: Dict) -> str:
    """Genera hash de señales para detectar cambios."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


# ============================================================
# GOOGLE PLACES API
# ============================================================

def search_place_by_company(company_name: str, location: str = "") -> Optional[Dict]:
    """
    Busca una empresa en Google Places API.
    Retorna el primer resultado o None.
    """
    if not GOOGLE_PLACES_API_KEY:
        return None
    
    query = f"{company_name} {location}".strip()
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and len(data.get("results", [])) > 0:
            return data["results"][0]
        
        return None
    except Exception as e:
        print(f"Error searching Google Places: {e}")
        return None


def get_place_details(place_id: str) -> Optional[Dict]:
    """
    Obtiene detalles completos de un place usando su place_id.
    """
    if not GOOGLE_PLACES_API_KEY:
        return None
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "place_id,name,formatted_address,rating,user_ratings_total,types,website,formatted_phone_number,opening_hours,photos,business_status,price_level",
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK":
            return data.get("result")
        
        return None
    except Exception as e:
        print(f"Error getting place details: {e}")
        return None


def calculate_places_score(place_data: Dict, pack: str) -> int:
    """
    Calcula puntos adicionales basados en Google Maps data.
    """
    score = 0
    
    # Pesos por pack
    if pack == "GUARDIAN":
        weights = {
            "rating_4_5_plus": 15,
            "rating_4_0_plus": 10,
            "reviews_10_50": 10,
            "reviews_51_100": 15,
            "reviews_100_plus": 20,
            "photos_count_10_plus": 10,
            "has_website": 5,
            "operational": 5
        }
    elif pack == "MOTOR":
        weights = {
            "rating_4_5_plus": 20,
            "rating_4_0_plus": 10,
            "reviews_50_100": 15,
            "reviews_100_500": 20,
            "reviews_500_plus": 25,
            "photos_count_20_plus": 15,
            "has_website": 10,
            "operational": 5
        }
    elif pack == "FORTALEZA":
        weights = {
            "rating_4_0_plus": 25,
            "reviews_100_plus": 30,
            "photos_count_30_plus": 20,
            "has_website": 10,
            "operational": 5
        }
    else:
        weights = {}
    
    # Rating
    rating = place_data.get("rating", 0)
    if rating >= 4.5:
        score += weights.get("rating_4_5_plus", 15)
    elif rating >= 4.0:
        score += weights.get("rating_4_0_plus", 10)
    
    # Reviews
    reviews = place_data.get("user_ratings_total", 0)
    if reviews >= 500:
        score += weights.get("reviews_500_plus", 25)
    elif reviews >= 100:
        score += weights.get("reviews_100_plus", 20)
    elif reviews >= 50:
        score += weights.get("reviews_50_100", 15)
    elif reviews >= 10:
        score += weights.get("reviews_10_50", 10)
    
    # Photos
    photos_count = len(place_data.get("photos", []))
    if photos_count >= 30:
        score += weights.get("photos_count_30_plus", 20)
    elif photos_count >= 20:
        score += weights.get("photos_count_20_plus", 15)
    elif photos_count >= 10:
        score += weights.get("photos_count_10_plus", 10)
    
    # Website
    if place_data.get("website"):
        score += weights.get("has_website", 10)
    
    # Business status
    if place_data.get("business_status") == "OPERATIONAL":
        score += weights.get("operational", 5)
    
    return score


# ============================================================
# PAGESPEED INSIGHTS API
# ============================================================

def get_pagespeed_insights(url: str) -> Optional[Dict]:
    """
    Obtiene métricas de PageSpeed Insights para una URL.
    """
    if not GOOGLE_PAGESPEED_API_KEY:
        return None
    
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": GOOGLE_PAGESPEED_API_KEY,
        "strategy": "mobile",  # mobile o desktop
        "category": "performance"
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extraer métricas clave
        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        
        return {
            "performance_score": lighthouse.get("categories", {}).get("performance", {}).get("score", 0) * 100,
            "lcp": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "fid": audits.get("max-potential-fid", {}).get("numericValue"),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "fcp": audits.get("first-contentful-paint", {}).get("numericValue"),
            "opportunities": len([
                a for a in audits.values() 
                if a.get("details", {}).get("type") == "opportunity"
            ])
        }
    except Exception as e:
        print(f"Error getting PageSpeed data: {e}")
        return None


# ============================================================
# WEB SCRAPING BÁSICO
# ============================================================

def get_web_signals(url: str) -> Optional[Dict]:
    """
    Scraping ligero: title, meta, CMS hints, stack hints.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SignalsBot/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text.lower()
        
        # Detectar CMS/stack básico
        cms_hints = []
        if "wp-content" in html or "wordpress" in html:
            cms_hints.append("WordPress")
        if "shopify" in html:
            cms_hints.append("Shopify")
        if "wix" in html:
            cms_hints.append("Wix")
        if "squarespace" in html:
            cms_hints.append("Squarespace")
        
        return {
            "reachable": True,
            "status_code": response.status_code,
            "cms_hints": cms_hints,
            "has_ssl": url.startswith("https://"),
            "content_length": len(html)
        }
    except Exception as e:
        print(f"Error getting web signals: {e}")
        return {
            "reachable": False,
            "error": str(e)
        }


# ============================================================
# ENDPOINT: /health
# ============================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "signals-worker",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "capabilities": {
            "google_places": bool(GOOGLE_PLACES_API_KEY),
            "google_pagespeed": bool(GOOGLE_PAGESPEED_API_KEY)
        }
    })


# ============================================================
# ENDPOINT: /enrich (principal)
# ============================================================

@app.route('/enrich', methods=['POST'])
def enrich_company():
    """
    Enriquece una empresa con todas las señales disponibles.
    
    Body:
    {
        "company": "Clínica Dental López",
        "location": "Madrid, Spain",
        "website": "https://clinicalopez.com",
        "pack": "GUARDIAN"
    }
    
    Response:
    {
        "enriched": true,
        "signals": {
            "google_places": {...},
            "pagespeed": {...},
            "web": {...}
        },
        "score_boost": 35,
        "signal_hash": "abc123..."
    }
    """
    data = request.json
    
    company = data.get('company')
    location = data.get('location', '')
    website = data.get('website')
    pack = data.get('pack', 'GUARDIAN')
    
    if not company:
        return jsonify({"error": "company is required"}), 400
    
    result = {
        "enriched": False,
        "signals": {},
        "score_boost": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Google Places
    if GOOGLE_PLACES_API_KEY:
        place_result = search_place_by_company(company, location)
        
        if place_result:
            place_id = place_result.get("place_id")
            place_details = get_place_details(place_id)
            
            if place_details:
                result["signals"]["google_places"] = {
                    "place_id": place_id,
                    "name": place_details.get("name"),
                    "rating": place_details.get("rating"),
                    "user_ratings_total": place_details.get("user_ratings_total"),
                    "types": place_details.get("types", []),
                    "website": place_details.get("website"),
                    "phone": place_details.get("formatted_phone_number"),
                    "address": place_details.get("formatted_address"),
                    "business_status": place_details.get("business_status"),
                    "photos_count": len(place_details.get("photos", []))
                }
                
                # Calcular score boost
                score_boost = calculate_places_score(place_details, pack)
                result["score_boost"] += score_boost
                result["signals"]["google_places"]["score_boost"] = score_boost
                result["enriched"] = True
    
    # 2. PageSpeed (si hay website)
    if website and GOOGLE_PAGESPEED_API_KEY:
        pagespeed_data = get_pagespeed_insights(website)
        
        if pagespeed_data:
            result["signals"]["pagespeed"] = pagespeed_data
            result["enriched"] = True
    
    # 3. Web signals (si hay website)
    if website:
        web_data = get_web_signals(website)
        
        if web_data:
            result["signals"]["web"] = web_data
            result["enriched"] = True
    
    # Generar hash de señales
    if result["signals"]:
        result["signal_hash"] = hash_signals(result["signals"])
    
    return jsonify(result)


# ============================================================
# ENDPOINT: /enrich/places (solo Google Places)
# ============================================================

@app.route('/enrich/places', methods=['POST'])
def enrich_places_only():
    """
    Solo Google Places (más rápido).
    
    Body:
    {
        "company": "Empresa SL",
        "location": "Barcelona",
        "pack": "MOTOR"
    }
    """
    data = request.json
    
    company = data.get('company')
    location = data.get('location', '')
    pack = data.get('pack', 'GUARDIAN')
    
    if not company:
        return jsonify({"error": "company is required"}), 400
    
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Places API key not configured"}), 503
    
    # Buscar
    place_result = search_place_by_company(company, location)
    
    if not place_result:
        return jsonify({
            "found": False,
            "message": f"No se encontró '{company}' en Google Places"
        }), 404
    
    # Obtener detalles
    place_id = place_result.get("place_id")
    place_details = get_place_details(place_id)
    
    if not place_details:
        return jsonify({"error": "Error getting place details"}), 500
    
    # Calcular score
    score_boost = calculate_places_score(place_details, pack)
    
    return jsonify({
        "found": True,
        "place_id": place_id,
        "data": {
            "name": place_details.get("name"),
            "rating": place_details.get("rating"),
            "user_ratings_total": place_details.get("user_ratings_total"),
            "types": place_details.get("types", []),
            "website": place_details.get("website"),
            "phone": place_details.get("formatted_phone_number"),
            "address": place_details.get("formatted_address"),
            "business_status": place_details.get("business_status")
        },
        "score_boost": score_boost,
        "signal_hash": hash_signals(place_details)
    })


# ============================================================
# ENDPOINT: /enrich/batch (múltiples empresas)
# ============================================================

@app.route('/enrich/batch', methods=['POST'])
def enrich_batch():
    """
    Enriquece múltiples empresas en batch.
    
    Body:
    {
        "companies": [
            {"company": "Empresa 1", "location": "Madrid", "pack": "GUARDIAN"},
            {"company": "Empresa 2", "location": "Barcelona", "pack": "MOTOR"}
        ]
    }
    """
    data = request.json
    companies = data.get('companies', [])
    
    if not companies or len(companies) > 20:
        return jsonify({"error": "companies array required (max 20)"}), 400
    
    results = []
    
    for company_data in companies:
        try:
            # Enriquecer cada una (solo Places por eficiencia)
            place_result = search_place_by_company(
                company_data.get('company'),
                company_data.get('location', '')
            )
            
            if place_result:
                place_id = place_result.get("place_id")
                place_details = get_place_details(place_id)
                
                if place_details:
                    score_boost = calculate_places_score(
                        place_details,
                        company_data.get('pack', 'GUARDIAN')
                    )
                    
                    results.append({
                        "company": company_data.get('company'),
                        "found": True,
                        "place_id": place_id,
                        "rating": place_details.get("rating"),
                        "reviews": place_details.get("user_ratings_total"),
                        "score_boost": score_boost
                    })
                else:
                    results.append({
                        "company": company_data.get('company'),
                        "found": False,
                        "error": "Details not found"
                    })
            else:
                results.append({
                    "company": company_data.get('company'),
                    "found": False,
                    "error": "Not found in Places"
                })
                
        except Exception as e:
            results.append({
                "company": company_data.get('company'),
                "found": False,
                "error": str(e)
            })
    
    return jsonify({
        "total": len(companies),
        "enriched": len([r for r in results if r.get("found")]),
        "results": results
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔶 signals-worker starting...")
    print("=" * 60)
    print(f"Port: 3001")
    print(f"Google Places API: {'✅ Configured' if GOOGLE_PLACES_API_KEY else '❌ Not configured'}")
    print(f"PageSpeed API: {'✅ Configured' if GOOGLE_PAGESPEED_API_KEY else '❌ Not configured'}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=3001, debug=False)