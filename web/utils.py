from typing import List, Tuple
import requests
import random
import string
from datetime import datetime
from google import genai
from .models import Chat
import os

def random_session() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def convert_to_matrix(data: list[list]) -> list[list[int]]:
    n = len(data)
    mat = [[0 for i in range(n)] for j in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i][j] = 0
            else:
                if i < j:
                    mat[i][j] = get_road_path(data[i][1], data[i][2], data[j][1], data[j][2])[1]
                else:
                    mat[i][j] = mat[j][i]
    return mat

def convert_chats(chats: List[Chat]) -> List[dict]:
    data = []
    for chat in chats:
        data.append({
            'message': chat.message,
            'type': chat.type
        })
    return data

def chatbot_response(input:str = None, history_obj:List[Chat] = None, route:list = None) -> str:
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"You are a bot in a Travel Assistance website. Current date and time: {date}\n"
    prompt += f"Keep the response in the range of 100 words.\nTry to highlight any important details or nearby suggestions if possible.\n"
    if route:
        stops = []
        for i in route:
            stops.append( f'{i[0]} ({i[1]},{i[2]})')
        prompt += f'The user has planned a route with {len(stops)} points from start to finish.\n'
        for i, point in enumerate(stops):
            prompt += f'{i+1}. {point}\n'
    if history_obj:
        history = convert_chats(history_obj)
        prompt += f'Here is the history of conversations:\n'
        for chat in history:
            prompt += f'{chat["type"].capitalize()}: {chat["message"]}\n'
    if input:
        prompt += f'Please answer to the users query.\n User: {input}\n'
    else:
        prompt += f'The user has selected those stops. Provide helpful suggestions and nearby locations similar to the stops. \n'
    
    key = os.getenv("GENAI_API_KEY")
    print(key)
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text

def get_road_path(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[List[List[float]], float, List[str]]:
    """Get road path between two points using OSRM"""
    cache_key = f"{lat1},{lon1}-{lat2},{lon2}"
    
    # Check if path is already cached
    if hasattr(get_road_path, 'cache') and cache_key in get_road_path.cache:
        return get_road_path.cache[cache_key]
    
    try:
        # Initialize cache if not exists
        if not hasattr(get_road_path, 'cache'):
            get_road_path.cache = {}
        
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&annotations=true&geometries=geojson"
        response = requests.get(url)
        data = response.json()
        
        if data["code"] != "Ok":
            return [], 0, []
            
        route = data["routes"][0]
        path = route["geometry"]["coordinates"]
        # Convert [lon, lat] to {lat, lng} objects for leaflet
        path = [{"lat": p[1], "lng": p[0]} for p in path]
        
        distance = route["distance"] / 1000  # Convert to km
        
        # Get turn-by-turn instructions
        steps = route["legs"][0]["steps"]
        instructions = [step.get("maneuver", {}).get("instruction", "") for step in steps]
        
        # Cache the result
        result = (path, distance, instructions)
        get_road_path.cache[cache_key] = result
        
        return result
    except Exception as e:
        print(f"Error getting road path: {str(e)}")
        return [], 0, []

def get_route_instructions(data: list[list]) -> list[dict]:
    planned_route = []
    for point in data:
        planned_route.append({
            "name": point[0],
            "lat": point[1],
            "lng": point[2],
        })
    if len(planned_route) < 2:
        return []
    final_route = []
    for i in range(len(planned_route)):
        point = planned_route[i]
        final_point = point.copy()
        
        if i > 0:
            prev_point = planned_route[i-1]
            path, distance, instructions = get_road_path(
                prev_point["lat"], prev_point["lng"],
                point["lat"], point["lng"]
            )
            final_point["path"] = path
            final_point["instructions"] = instructions
        else:
            final_point["path"] = []
            final_point["instructions"] = []
            
        final_route.append(final_point)
        
    return final_route

def travelling_salesman(m) -> Tuple[float, List[int]]:
    q = 9999
    n = len(m)
    v = [[q for i in range(n)] for j in range(1 << n)]
    path = [[(-1, -1) for i in range(n)] for j in range(1 << n)]
    v[1][0] = 0
    for s in range(3, 1 << n):

        for i in range(n):
            if s >> i & 1:
                for j in range(n):
                    if s >> j & 1 and j != i:
                        curr_cost = v[s ^ (1 << i)][j] + m[j][i]
                        if curr_cost < v[s][i]:
                            v[s][i] = curr_cost
                            path[s][i] = (s ^ (1 << i), j)  # Store previous state and city

    # Find the final minimum cost and ending city
    final_state = (1 << n) - 1
    min_cost = 9999
    last_city = -1
    
    for i in range(1, n):
        curr_cost = v[final_state][i] + m[i][0]
        if curr_cost < min_cost:
            min_cost = curr_cost
            last_city = i

    # Reconstruct the path
    current_state = final_state
    current_city = last_city
    route = []
    while current_city != -1:
        route.append(current_city)
        prev_state, prev_city = path[current_state][current_city]
        current_state = prev_state
        current_city = prev_city
    route.reverse()  # Correct the order
    route.append(0)  # Return to start

    return min_cost, route