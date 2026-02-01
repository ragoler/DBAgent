import asyncio
import os
from backend.core.agent_manager import agent_manager

async def run_repro():
    print("🚀 Starting Streaming Reproduction...")
    user_id = "repro_user"
    session_id = "repro_session_1"
    
    # 1. Ask for table list (should involve tool call)
    print("\n--- TEST case 1: 'What tables are available?' ---")
    message = "What tables are available?"
    chunk_count = 0
    full_text = ""
    
    async for chunk in agent_manager.chat_stream(user_id, session_id, message):
        chunk_count += 1
        print(f"[{chunk_count}] Chunk type: {type(chunk)} | Value: {repr(chunk)}")
        full_text += str(chunk)
    
    print(f"\n✅ Finished Test 1. Total chunks: {chunk_count}")
    print(f"Full Text:\n{full_text}")

    # 2. Ask for description (should involve tool call + markdown)
    print("\n--- TEST case 2: 'Describe the flights table' ---")
    message = "Describe the flights table"
    chunk_count = 0
    full_text = ""
    
    async for chunk in agent_manager.chat_stream(user_id, session_id, message):
        chunk_count += 1
        print(f"[{chunk_count}] Chunk type: {type(chunk)} | Value: {repr(chunk)}")
        full_text += str(chunk)
        
    print(f"\n✅ Finished Test 2. Total chunks: {chunk_count}")
    print(f"Full Text:\n{full_text}")

if __name__ == "__main__":
    asyncio.run(run_repro())
