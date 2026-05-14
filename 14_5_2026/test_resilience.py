import asyncio
import httpx

API_URL = "http://127.0.0.1:8000/chat/resilient"

async def test_cases():
    async with httpx.AsyncClient() as client:
        print("=== Test 1: Normal (Primary OpenAI) ===")
        res = await client.post(API_URL, json={"message": "Xin chào", "simulate_delay": 0, "simulate_error": False})
        print(res.json(), "\n")

        print("=== Test 2: Timeout (Fallback to Cache) ===")
        res = await client.post(API_URL, json={"message": "Xin chào", "simulate_delay": 5.0, "simulate_error": False}, timeout=20.0)
        print(res.json(), "\n")

        print("=== Test 3: OpenAI Error (Retry 2x, then Fallback to Cache) ===")
        res = await client.post(API_URL, json={"message": "Xin chào", "simulate_delay": 0, "simulate_error": True})
        print(res.json(), "\n")

        print("=== Test 4: Trigger Circuit Breaker ===")
        for i in range(3):
            await client.post(API_URL, json={"message": "Lỗi", "simulate_delay": 0, "simulate_error": True})
        
        print("Call after Circuit is OPEN:")
        res = await client.post(API_URL, json={"message": "Bình thường", "simulate_delay": 0, "simulate_error": False})
        print(res.json(), "\n")

if __name__ == "__main__":
    asyncio.run(test_cases())