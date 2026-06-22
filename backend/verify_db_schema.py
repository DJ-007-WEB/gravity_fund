import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Ensure backend folder is in Python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.models import User, UserProfile

async def main():
    print("Initializing Database Connection...")
    # Initialize connection engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    # Configure an async session factory
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with SessionLocal() as session:
        try:
            print("\n--- STEP 1: Test Insert into 'users' and 'user_profiles' ---")
            # 1. Create a dummy User
            new_user = User(
                email="test_schema@gravityfund.com",
                password_hash="hashedpassword123",
                is_active=True
            )
            
            # 2. Create a UserProfile linked to the new user
            new_profile = UserProfile(
                user=new_user,
                age=28,
                annual_income=1500000.0,
                monthly_expenses=60000.0,
                investment_horizon_years=7,
                risk_tolerance_answers={"question_1": 5, "question_2": 4},
                risk_score=4.5,
                risk_category="Aggressive"
            )
            
            # Add both objects to the active session tracker
            session.add(new_user)
            session.add(new_profile)
            
            # Commit the transaction to save changes to the database
            await session.commit()
            print("SUCCESS: Test User and Profile inserted successfully.")

            print("\n--- STEP 2: Test Fetching User & Relationships (Async Eager Loading) ---")
            # 3. Query the user back.
            # CRITICAL CONCEPT: In asynchronous SQLAlchemy, we cannot just call 'user.profile' because
            # lazy loading executes a synchronous DB call under the hood, which crashes in async.
            # We use `selectinload` to eager-load the relationship asynchronously in the initial query.
            stmt = (
                select(User)
                .options(selectinload(User.profile))
                .where(User.email == "test_schema@gravityfund.com")
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"SUCCESS: Retrieved User -> ID: {user.id}, Email: {user.email}")
                if user.profile:
                    print(f"SUCCESS: Retrieved Associated Profile -> Age: {user.profile.age}, Risk Category: {user.profile.risk_category}")
                else:
                    print("ERROR: User profile was not loaded!")
            else:
                print("ERROR: User record was not found!")

            print("\n--- STEP 3: Test Database Cascade Delete ---")
            # 4. Delete the User. Since user_profiles has `ForeignKey("users.id", ondelete="CASCADE")`,
            # deleting the user must automatically delete the associated profile inside PostgreSQL.
            user_id = user.id
            await session.delete(user)
            await session.commit()
            print("SUCCESS: Deleted User from the session.")
            
            # 5. Check if the UserProfile is gone
            stmt_profile = select(UserProfile).where(UserProfile.user_id == user_id)
            result_profile = await session.execute(stmt_profile)
            profile_check = result_profile.scalar_one_or_none()
            
            if profile_check is None:
                print("SUCCESS: Cascade delete confirmed! UserProfile was automatically deleted in PostgreSQL.")
            else:
                print("ERROR: UserProfile was NOT deleted (Cascade delete failed)!")
                
            print("\nDatabase Schema verification passed successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"\nERROR: Database Schema verification failed: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            await session.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
