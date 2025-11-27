import random
from utils.words import adjectives_file, nouns_file, color_file
from database.supabase import supabase


def generate_suggestions() -> list[str]:
    suggestions = []
    attempts = 0

    while len(suggestions) < 3 and attempts < 100:
        attempts += 1
        style = random.randint(0, 2)

        if style == 0:
            base = f"{random.choice(color_file)} {random.choice(adjectives_file)}{random.choice(nouns_file)}"
        elif style == 1:
            base = f"{random.choice(adjectives_file)} {random.choice(nouns_file)}"
        else:
            base = f"{random.choice(color_file)} {random.choice(nouns_file)}"

        
        nickname = f"{base}_{random.randint(1000, 9999)}"

        exists = supabase.table("profiles").select("id").eq("nickname", nickname).execute()
        if not exists.data:
            suggestions.append(nickname)
    
    return suggestions

def reserve_nickname(telegram_id: int, nickname: str) -> bool:
    # Check if nickname is already taken by another user
    existing = supabase.table("profiles").select("telegram_id").eq("nickname", nickname).execute()
    if existing.data and existing.data[0]["telegram_id"] != telegram_id:
        return False
    
    # Update the nickname for this user
    result = supabase.table("profiles").update({"nickname": nickname}).eq("telegram_id", telegram_id).execute()
    return len(result.data) > 0