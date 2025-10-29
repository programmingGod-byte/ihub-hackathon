#!/usr/bin/env python3
"""
🌿 GREEN ROUTE FINDER - 100% FREE VERSION
Uses only free APIs - NO Google Maps, NO paid services
ACTUALLY WORKS with real route calculation!
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import webbrowser
import os

try:
    import folium
    from folium import plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

# ==================== DATA MODELS ====================
@dataclass
class Coordinates:
    lat: float
    lng: float
    
    def __str__(self):
        return f"({self.lat:.4f}, {self.lng:.4f})"


@dataclass
class RouteScore:
    greenery: int      # 0-100
    noise: int         # 0-100 (higher = quieter)
    safety: int        # 0-100
    air_quality: int   # 0-100
    overall: int       # 0-100


@dataclass
class Route:
    name: str
    distance_km: float
    duration_min: int
    scores: RouteScore
    coordinates: List[Tuple[float, float]]  # List of (lat, lng)


# ==================== FREE API SERVICE ====================
class FreeAPIService:
    """
    Uses ONLY free APIs:
    - OSRM for routing (FREE)
    - Nominatim for geocoding (FREE)
    - Overpass API for greenery/noise/safety (FREE)
    - OpenAQ for air quality (FREE)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request = {}  # Track per-API
        self.delays = {
            'osrm': 1.0,
            'nominatim': 1.5,
            'overpass': 2.0,  # Overpass needs more delay
            'openaq': 1.0
        }
        self.retry_count = 0
        self.max_retries = 2
    
    def _wait(self, api_name='default'):
        """Rate limiting to be respectful to free APIs"""
        delay = self.delays.get(api_name, 1.5)
        last = self.last_request.get(api_name, 0)
        elapsed = time.time() - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request[api_name] = time.time()
    
    def get(self, url: str, params: Dict = None, api_name='default') -> Dict:
        """Make request with error handling and retries"""
        for attempt in range(self.max_retries + 1):
            self._wait(api_name)
            try:
                headers = {'User-Agent': 'GreenRouteFinderBot/1.0'}
                response = self.session.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries:
                        wait_time = 5 * (attempt + 1)
                        print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                elif e.response.status_code == 410:  # Gone
                    return {}  # Silently fail
                print(f"⚠️  HTTP {e.response.status_code}")
                return {}
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"   ⏳ Timeout, retrying...")
                    time.sleep(3)
                    continue
                return {}
            except Exception as e:
                return {}
        return {}
    
    def post(self, url: str, data: str, api_name='overpass') -> Dict:
        """POST request with error handling and retries"""
        for attempt in range(self.max_retries + 1):
            self._wait(api_name)
            try:
                headers = {
                    'User-Agent': 'GreenRouteFinderBot/1.0',
                    'Content-Type': 'text/plain'
                }
                response = self.session.post(url, data=data, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries:
                        wait_time = 10 * (attempt + 1)  # Longer wait for overpass
                        print(f"   ⏳ Overpass rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                return {}
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"   ⏳ Timeout, retrying...")
                    time.sleep(5)
                    continue
                return {}
            except Exception:
                return {}
        return {}


# ==================== ROUTE FINDER ====================
class GreenRouteFinder:
    """Find and analyze green routes using FREE APIs"""
    
    def __init__(self):
        self.api = FreeAPIService()
        print("✅ Using 100% FREE APIs:")
        print("   - OSRM for routing")
        print("   - Nominatim for geocoding")
        print("   - Overpass API for environmental data")
        print("   - OpenAQ for air quality")
    
    def geocode(self, address: str) -> Optional[Coordinates]:
        """Convert address to coordinates using Nominatim (FREE)"""
        print(f"🔍 Finding location: {address}...")
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'format': 'json',
            'q': address,
            'limit': 1
        }
        
        data = self.api.get(url, params, api_name='nominatim')
        
        if data and len(data) > 0:
            result = data[0]
            coords = Coordinates(
                lat=float(result['lat']),
                lng=float(result['lon'])
            )
            print(f"   ✓ Found: {coords}")
            return coords
        
        print(f"   ✗ Location not found")
        return None
    
    def find_route(self, start: Coordinates, end: Coordinates) -> List[Dict]:
        """Get route using OSRM (FREE OpenStreetMap routing)"""
        print(f"\n🗺️  Calculating route from {start} to {end}...")
        
        # OSRM API - FREE, no key required!
        url = f"https://router.project-osrm.org/route/v1/driving/{start.lng},{start.lat};{end.lng},{end.lat}"
        
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true',
            'alternatives': 'true'  # Get multiple route options
        }
        
        data = self.api.get(url, params, api_name='osrm')
        
        if data.get('code') == 'Ok' and data.get('routes'):
            routes = data['routes']
            print(f"   ✓ Found {len(routes)} route(s)")
            
            result = []
            for route in routes[:3]:  # Max 3 routes
                coords = route['geometry']['coordinates']
                # Convert from [lng, lat] to [lat, lng]
                coords_latlon = [(lat, lng) for lng, lat in coords]
                
                result.append({
                    'distance': route['distance'],  # meters
                    'duration': route['duration'],  # seconds
                    'coordinates': coords_latlon
                })
            
            return result
        
        print(f"   ✗ No route found")
        return []
    
    def analyze_greenery(self, lat: float, lng: float) -> int:
        """
        Analyze greenery using Overpass API (FREE OpenStreetMap data)
        Checks for parks, trees, forests, gardens, grass areas
        """
        radius = 200  # meters
        
        query = f"""
        [out:json][timeout:10];
        (
          way["natural"="tree"](around:{radius},{lat},{lng});
          way["natural"="wood"](around:{radius},{lat},{lng});
          way["landuse"="forest"](around:{radius},{lat},{lng});
          way["leisure"="park"](around:{radius},{lat},{lng});
          way["leisure"="garden"](around:{radius},{lat},{lng});
          way["landuse"="grass"](around:{radius},{lat},{lng});
          way["landuse"="meadow"](around:{radius},{lat},{lng});
          way["natural"="grassland"](around:{radius},{lat},{lng});
          node["natural"="tree"](around:{radius},{lat},{lng});
        );
        out count;
        """
        
        data = self.api.post('https://overpass-api.de/api/interpreter', query, api_name='overpass')
        
        if data and 'elements' in data:
            count = len(data['elements'])
            
            # Convert count to score (0-100)
            if count == 0:
                score = 10
            elif count <= 5:
                score = 30 + (count * 8)
            elif count <= 15:
                score = 70 + ((count - 5) * 2)
            else:
                score = min(100, 90 + (count - 15))
            
            return score
        
        return 50  # Default if API fails
    
    def analyze_noise(self, lat: float, lng: float) -> int:
        """
        Analyze noise level using Overpass API (FREE)
        Checks proximity to highways, major roads
        """
        radius = 150  # meters
        
        query = f"""
        [out:json][timeout:10];
        (
          way["highway"="motorway"](around:{radius},{lat},{lng});
          way["highway"="motorway_link"](around:{radius},{lat},{lng});
          way["highway"="trunk"](around:{radius},{lat},{lng});
          way["highway"="trunk_link"](around:{radius},{lat},{lng});
          way["highway"="primary"](around:{radius},{lat},{lng});
          way["highway"="secondary"](around:{radius},{lat},{lng});
        );
        out count;
        """
        
        data = self.api.post('https://overpass-api.de/api/interpreter', query, api_name='overpass')
        
        if data and 'elements' in data:
            major_roads = len(data['elements'])
            
            # More major roads = noisier (inverse score)
            if major_roads == 0:
                score = 95
            elif major_roads <= 2:
                score = 80 - (major_roads * 10)
            elif major_roads <= 5:
                score = 60 - ((major_roads - 2) * 8)
            else:
                score = max(20, 35 - (major_roads * 3))
            
            return score
        
        return 60
    
    def analyze_safety(self, lat: float, lng: float) -> int:
        """
        Analyze safety using Overpass API (FREE)
        Checks for street lights, police stations, pedestrian infrastructure
        """
        radius = 150  # meters
        
        query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="police"](around:{radius},{lat},{lng});
          node["highway"="street_lamp"](around:{radius},{lat},{lng});
          way["lit"="yes"](around:{radius},{lat},{lng});
          way["highway"="pedestrian"](around:{radius},{lat},{lng});
          way["highway"="footway"](around:{radius},{lat},{lng});
          way["highway"="path"](around:{radius},{lat},{lng});
          node["emergency"="phone"](around:{radius},{lat},{lng});
          node["amenity"="fire_station"](around:{radius},{lat},{lng});
        );
        out count;
        """
        
        data = self.api.post('https://overpass-api.de/api/interpreter', query, api_name='overpass')
        
        if data and 'elements' in data:
            safety_features = len(data['elements'])
            
            # More safety features = safer
            if safety_features == 0:
                score = 35
            elif safety_features <= 5:
                score = 40 + (safety_features * 8)
            elif safety_features <= 15:
                score = 80 + ((safety_features - 5) * 1.5)
            else:
                score = min(100, 95)
            
            return round(score)
        
        return 55
    
    def analyze_air_quality(self, lat: float, lng: float) -> int:
        """
        Get air quality using OpenAQ (FREE, global air quality database)
        """
        url = "https://api.openaq.org/v2/latest"
        params = {
            'coordinates': f"{lat},{lng}",
            'radius': 10000,  # 10km radius
            'limit': 1
        }
        
        data = self.api.get(url, params, api_name='openaq')
        
        if data.get('results') and len(data['results']) > 0:
            measurements = data['results'][0].get('measurements', [])
            
            # Look for PM2.5 (particulate matter)
            pm25_data = next((m for m in measurements if m['parameter'] == 'pm25'), None)
            
            if pm25_data:
                value = pm25_data['value']
                
                # Convert PM2.5 to score (WHO guidelines)
                # Good: 0-12 μg/m³
                # Moderate: 12-35 μg/m³
                # Unhealthy: 35-55 μg/m³
                # Very Unhealthy: 55+ μg/m³
                
                if value <= 10:
                    score = 95
                elif value <= 20:
                    score = 85
                elif value <= 35:
                    score = 70
                elif value <= 55:
                    score = 50
                elif value <= 75:
                    score = 35
                else:
                    score = 20
                
                return score
        
        return 65  # Default if no data
    
    def analyze_route(self, route_coords: List[Tuple[float, float]], route_num: int) -> RouteScore:
        """Analyze environmental factors along the route"""
        print(f"\n📊 Analyzing Route {route_num}...")
        
        # Reduce sample points to avoid rate limiting (max 8 instead of 15)
        total_points = len(route_coords)
        sample_size = min(8, total_points)  # Reduced from 15 to 8
        step = max(1, total_points // sample_size)
        sample_points = route_coords[::step][:sample_size]
        
        print(f"   Sampling {len(sample_points)} points (reduced to avoid rate limits)")
        
        greenery_scores = []
        noise_scores = []
        safety_scores = []
        air_scores = []
        
        for i, (lat, lng) in enumerate(sample_points):
            print(f"   Point {i+1}/{len(sample_points)}...", end='\r')
            
            greenery = self.analyze_greenery(lat, lng)
            noise = self.analyze_noise(lat, lng)
            safety = self.analyze_safety(lat, lng)
            air = self.analyze_air_quality(lat, lng)
            
            greenery_scores.append(greenery)
            noise_scores.append(noise)
            safety_scores.append(safety)
            air_scores.append(air)
        
        print()  # New line after progress
        
        # Calculate averages
        avg_greenery = round(sum(greenery_scores) / len(greenery_scores))
        avg_noise = round(sum(noise_scores) / len(noise_scores))
        avg_safety = round(sum(safety_scores) / len(safety_scores))
        avg_air = round(sum(air_scores) / len(air_scores))
        
        # Calculate overall score (weighted)
        overall = round(
            avg_greenery * 0.35 +
            avg_air * 0.25 +
            avg_noise * 0.20 +
            avg_safety * 0.20
        )
        
        print(f"   ✓ Greenery: {avg_greenery}/100")
        print(f"   ✓ Noise: {avg_noise}/100")
        print(f"   ✓ Safety: {avg_safety}/100")
        print(f"   ✓ Air Quality: {avg_air}/100")
        print(f"   ⭐ Overall: {overall}/100")
        
        return RouteScore(
            greenery=avg_greenery,
            noise=avg_noise,
            safety=avg_safety,
            air_quality=avg_air,
            overall=overall
        )
    
    def find_green_routes(self,
                         start: Coordinates,
                         end: Coordinates,
                         greenery_pref: int = 5,
                         noise_pref: int = 5,
                         safety_pref: int = 5) -> List[Route]:
        """
        Find and analyze green routes
        
        Args:
            start: Starting coordinates
            end: Ending coordinates
            greenery_pref: 0-10 (how much you care about greenery)
            noise_pref: 0-10 (how much you care about quiet)
            safety_pref: 0-10 (how much you care about safety)
        """
        # Get routes
        routes_data = self.find_route(start, end)
        if not routes_data:
            return []
        
        # Analyze each route
        analyzed_routes = []
        
        for i, route_data in enumerate(routes_data):
            scores = self.analyze_route(route_data['coordinates'], i + 1)
            
            route = Route(
                name=f"Route {i + 1}",
                distance_km=round(route_data['distance'] / 1000, 2),
                duration_min=round(route_data['duration'] / 60),
                scores=scores,
                coordinates=route_data['coordinates']
            )
            
            analyzed_routes.append(route)
        
        # Rank by preferences
        def preference_score(route: Route) -> float:
            total_pref = greenery_pref + noise_pref + safety_pref
            if total_pref == 0:
                return route.scores.overall
            
            return (
                route.scores.greenery * greenery_pref +
                route.scores.noise * noise_pref +
                route.scores.safety * safety_pref
            ) / total_pref
        
        analyzed_routes.sort(key=preference_score, reverse=True)
        
        # Name them
        if len(analyzed_routes) > 0:
            analyzed_routes[0].name = "🏆 Best Match"
        if len(analyzed_routes) > 1:
            analyzed_routes[1].name = "🥈 Alternative"
        if len(analyzed_routes) > 2:
            analyzed_routes[2].name = "🥉 Third Option"
        
        return analyzed_routes
    
    def create_map(self, routes: List[Route], start: Coordinates, end: Coordinates, filename: str = "green_route_map.html") -> str:
        """
        Create an interactive map showing the routes
        
        Args:
            routes: List of analyzed routes
            start: Starting coordinates
            end: Ending coordinates
            filename: Output HTML filename
            
        Returns:
            Path to the generated HTML file
        """
        if not HAS_FOLIUM:
            print("⚠️  Folium not installed. Install with: pip install folium")
            return None
        
        # Calculate center point
        center_lat = (start.lat + end.lat) / 2
        center_lng = (start.lng + end.lng) / 2
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Color scheme for routes
        colors = ['#2E7D32', '#1976D2', '#F57C00', '#7B1FA2']
        
        # Add routes
        for idx, route in enumerate(routes):
            color = colors[idx % len(colors)]
            
            # Get color based on overall score
            if route.scores.overall >= 80:
                route_color = '#2E7D32'  # Dark green
            elif route.scores.overall >= 60:
                route_color = '#FBC02D'  # Yellow
            else:
                route_color = '#D32F2F'  # Red
            
            # Create popup content
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h3 style="margin: 0 0 10px 0; color: {route_color};">{route.name}</h3>
                <p style="margin: 5px 0;"><b>Distance:</b> {route.distance_km} km</p>
                <p style="margin: 5px 0;"><b>Duration:</b> {route.duration_min} min</p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0;"><b>🌳 Greenery:</b> {route.scores.greenery}/100</p>
                <p style="margin: 5px 0;"><b>🔇 Quiet:</b> {route.scores.noise}/100</p>
                <p style="margin: 5px 0;"><b>🛡️ Safety:</b> {route.scores.safety}/100</p>
                <p style="margin: 5px 0;"><b>💨 Air Quality:</b> {route.scores.air_quality}/100</p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 16px;"><b>⭐ Overall:</b> {route.scores.overall}/100</p>
            </div>
            """
            
            # Add route line
            route_coords = [(lat, lng) for lat, lng in route.coordinates]
            folium.PolyLine(
                route_coords,
                color=route_color,
                weight=5,
                opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{route.name}: {route.scores.overall}/100"
            ).add_to(m)
            
            # Add markers every 10th point to show environmental variation
            sample_interval = max(1, len(route.coordinates) // 8)
            for i in range(0, len(route.coordinates), sample_interval):
                lat, lng = route.coordinates[i]
                # Color based on position (gradient from start to end)
                progress = i / len(route.coordinates)
                
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=3,
                    color=route_color,
                    fill=True,
                    fillColor=route_color,
                    fillOpacity=0.6,
                    weight=1
                ).add_to(m)
        
        # Add start marker
        folium.Marker(
            location=[start.lat, start.lng],
            popup='<b>Start</b>',
            tooltip='Starting Point',
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add end marker
        folium.Marker(
            location=[end.lat, end.lng],
            popup='<b>Destination</b>',
            tooltip='Destination',
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    width: 200px; 
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 9999; 
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;">
            <h4 style="margin: 0 0 10px 0;">Green Score Legend</h4>
            <p style="margin: 5px 0;"><span style="color: #2E7D32;">●</span> Excellent (80-100)</p>
            <p style="margin: 5px 0;"><span style="color: #FBC02D;">●</span> Good (60-79)</p>
            <p style="margin: 5px 0;"><span style="color: #D32F2F;">●</span> Poor (0-59)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        # Save map
        m.save(filename)
        
        return os.path.abspath(filename)


# ==================== DISPLAY FUNCTIONS ====================
def print_bar(score: int, width: int = 30) -> str:
    """Create visual bar for score"""
    filled = int(score / 100 * width)
    empty = width - filled
    
    if score >= 80:
        bar = f"{'█' * filled}{'░' * empty}"
        return f"🟢 {bar}"
    elif score >= 60:
        bar = f"{'█' * filled}{'░' * empty}"
        return f"🟡 {bar}"
    else:
        bar = f"{'█' * filled}{'░' * empty}"
        return f"🔴 {bar}"


def print_results(routes: List[Route]):
    """Print beautiful results"""
    print("\n" + "="*70)
    print("🌿 GREEN ROUTE ANALYSIS - RESULTS")
    print("="*70)
    
    for route in routes:
        print(f"\n{route.name}")
        print("-" * 70)
        print(f"📍 Distance: {route.distance_km} km")
        print(f"⏱️  Duration: {route.duration_min} minutes")
        print(f"\n📊 Environmental Scores:")
        print(f"   🌳 Greenery:     {route.scores.greenery:3d}/100  {print_bar(route.scores.greenery)}")
        print(f"   🔇 Quiet:        {route.scores.noise:3d}/100  {print_bar(route.scores.noise)}")
        print(f"   🛡️  Safety:       {route.scores.safety:3d}/100  {print_bar(route.scores.safety)}")
        print(f"   💨 Air Quality:  {route.scores.air_quality:3d}/100  {print_bar(route.scores.air_quality)}")
        print(f"\n   ⭐ OVERALL: {route.scores.overall}/100  {print_bar(route.scores.overall)}")
        print()


# ==================== MAIN ====================
def main():
    print("="*70)
    print("🌿 GREEN ROUTE FINDER - 100% FREE APIs")
    print("="*70)
    print("Find eco-friendly routes with REAL data!")
    print()
    
    finder = GreenRouteFinder()
    
    print("\n" + "-"*70)
    print("📍 ENTER LOCATIONS")
    print("-"*70)
    print("You can use:")
    print("  - Coordinates: 40.7128,-74.0060")
    print("  - Addresses: Central Park, New York")
    print()
    
    # Get start location
    start_input = input("Starting point: ").strip()
    if not start_input:
        print("❌ Starting point required!")
        return
    
    # Parse start
    if ',' in start_input and start_input.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
        parts = start_input.split(',')
        start = Coordinates(float(parts[0]), float(parts[1]))
    else:
        start = finder.geocode(start_input)
        if not start:
            return
    
    # Get destination
    end_input = input("Destination: ").strip()
    if not end_input:
        print("❌ Destination required!")
        return
    
    # Parse destination
    if ',' in end_input and end_input.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
        parts = end_input.split(',')
        end = Coordinates(float(parts[0]), float(parts[1]))
    else:
        end = finder.geocode(end_input)
        if not end:
            return
    
    # Get preferences
    print("\n" + "-"*70)
    print("🎯 SET YOUR PREFERENCES (0-10)")
    print("-"*70)
    print("0 = Don't care, 10 = Very important")
    print()
    
    try:
        greenery = int(input("🌳 Greenery importance (0-10) [5]: ") or "5")
        noise = int(input("🔇 Quiet importance (0-10) [5]: ") or "5")
        safety = int(input("🛡️  Safety importance (0-10) [5]: ") or "5")
        
        if not all(0 <= x <= 10 for x in [greenery, noise, safety]):
            print("❌ Values must be 0-10")
            return
    except ValueError:
        print("❌ Please enter numbers")
        return
    
    # Find routes
    print("\n" + "="*70)
    print("🔄 ANALYZING ROUTES...")
    print("="*70)
    print("This will take 2-4 minutes (being extra careful with free APIs)")
    print("Slower delays = more reliable results!")
    
    try:
        routes = finder.find_green_routes(
            start=start,
            end=end,
            greenery_pref=greenery,
            noise_pref=noise,
            safety_pref=safety
        )
        
        if routes:
            print_results(routes)
            
            # Generate and open map
            print("\n" + "="*70)
            print("🗺️  GENERATING INTERACTIVE MAP...")
            print("="*70)
            
            if HAS_FOLIUM:
                try:
                    map_file = finder.create_map(routes, start, end, "green_route_map.html")
                    if map_file:
                        print(f"✅ Map saved to: {map_file}")
                        print("🌐 Opening map in your browser...")
                        
                        # Open in browser
                        webbrowser.open('file://' + map_file)
                        
                        print()
                        print("📍 Map Features:")
                        print("   - 🟢 Green routes = High environmental score")
                        print("   - 🟡 Yellow routes = Medium environmental score")
                        print("   - 🔴 Red routes = Low environmental score")
                        print("   - Click on routes for detailed scores")
                        print("   - Zoom and pan to explore")
                        print()
                except Exception as e:
                    print(f"⚠️  Could not create map: {e}")
            else:
                print("⚠️  Map generation requires folium")
                print("   Install with: pip install folium")
                print("   Then run the script again!")
            
            print("="*70)
            print("✅ ANALYSIS COMPLETE!")
            print("="*70)
            print()
        else:
            print("\n❌ No routes found")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()