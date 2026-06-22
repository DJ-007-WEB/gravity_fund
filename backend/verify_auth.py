import asyncio
import sys
import os
from httpx import AsyncClient, ASGITransport

# Ensure backend folder is in Python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.db.session import SessionLocal
from app.db.models.user import User
from sqlalchemy import delete

async def clean_database():
    """
    Utility function to delete the test user records before and after tests.
    """
    async with SessionLocal() as session:
        # Delete any users starting with test_auth
        await session.execute(delete(User).where(User.email.like("test_auth%")))
        await session.commit()

async def main():
    print("Initializing Authentication Verification Tests...")
    
    # 1. Clean previous test runs
    await clean_database()
    
    # 2. Use HTTPX AsyncClient with ASGITransport to route HTTP requests directly to
    # our FastAPI 'app' in-memory, without having to spawn a subprocess.
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        try:
            print("\n--- STEP 1: Registering User (/signup) ---")
            signup_payload = {
                "email": "test_auth_user@gravityfund.com",
                "password": "supersecurepassword123"
            }
            response = await client.post("/api/v1/auth/signup", json=signup_payload)
            print(f"Signup Status: {response.status_code}")
            print(f"Signup Body: {response.json()}")
            assert response.status_code == 201, "Expected 201 Created"
            
            print("\n--- STEP 1.1: Rejecting Duplicate Emails ---")
            response = await client.post("/api/v1/auth/signup", json=signup_payload)
            print(f"Duplicate Status: {response.status_code}")
            print(f"Duplicate Body: {response.json()}")
            assert response.status_code == 400, "Expected 400 Bad Request"
            
            print("\n--- STEP 1.2: Rejecting Weak Passwords (min 8 chars) ---")
            short_payload = {
                "email": "test_auth_weak@gravityfund.com",
                "password": "short"
            }
            response = await client.post("/api/v1/auth/signup", json=short_payload)
            print(f"Weak Password Status: {response.status_code}")
            print(f"Weak Password Body: {response.json()}")
            assert response.status_code == 422, "Expected 422 Unprocessable Entity"
            
            print("\n--- STEP 2: Logging in (/login) ---")
            # OAuth2 Password flow expects URL-encoded form data (username, password)
            login_payload = {
                "username": "test_auth_user@gravityfund.com",
                "password": "supersecurepassword123"
            }
            response = await client.post("/api/v1/auth/login", data=login_payload)
            print(f"Login Status: {response.status_code}")
            login_res = response.json()
            print(f"Login Body: {login_res}")
            assert response.status_code == 200, "Expected 200 OK"
            assert "access_token" in login_res, "Expected access token in response"
            token = login_res["access_token"]
            
            print("\n--- STEP 3: Accessing Protected Endpoint (/me) with valid token ---")
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/auth/me", headers=headers)
            print(f"Get Me Status: {response.status_code}")
            print(f"Get Me Body: {response.json()}")
            assert response.status_code == 200, "Expected 200 OK"
            assert response.json()["email"] == "test_auth_user@gravityfund.com", "User email must match"
            
            print("\n--- STEP 4: Verifying API Rate Limiting ---")
            # The RateLimiter has a threshold of 10 requests per minute on /login.
            # We trigger multiple rapid requests to exceed that limit.
            print("Triggering rapid login requests to exceed rate limits...")
            rate_limit_triggered = False
            for i in range(15):
                resp = await client.post("/api/v1/auth/login", data=login_payload)
                if resp.status_code == 429:
                    print(f"SUCCESS: Rate limiting triggered successfully on request #{i+1}!")
                    print(f"Rate Limiting Response (429): {resp.json()}")
                    rate_limit_triggered = True
                    break
            assert rate_limit_triggered, "Expected rate limiter to return 429 Too Many Requests"
            
            print("\n--- STEP 5: Logging out (/logout) ---")
            response = await client.post("/api/v1/auth/logout", headers=headers)
            print(f"Logout Status: {response.status_code}")
            print(f"Logout Body: {response.json()}")
            assert response.status_code == 200, "Expected 200 OK"
            
            print("\n--- STEP 6: Verifying Token Blacklisting ---")
            # Try to access the protected endpoint again with the same token.
            # Redis should intercept it and return 401 Unauthorized.
            response = await client.get("/api/v1/auth/me", headers=headers)
            print(f"Get Me After Logout Status: {response.status_code}")
            print(f"Get Me After Logout Body: {response.json()}")
            assert response.status_code == 401, "Expected 401 Unauthorized after logout"
            
            print("\nAll User Authentication & Redis Rate-Limiting tests passed successfully!")
            
        except AssertionError as ae:
            print(f"\nASSERTION FAILED: {ae}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nTEST EXECUTION FAILED: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            print("\nCleaning database from verification users...")
            await clean_database()
            # Explicitly close the Redis connection pool to prevent Python from hanging
            from app.core.redis import redis_client
            await redis_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
