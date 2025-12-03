from features.nickname.schemas import NicknameResponse
from database.supabase import supabase
import random   
from utils.words import adjectives_file, nouns_file, color_file
from fastapi import HTTPException


def generate_nickname() -> NicknameResponse:
    adjectives = adjectives_file
    nouns = nouns_file
    colors = color_file

    while True:
        style = random.choice([0, 1, 2])
        if style == 0:
            # Color + Noun
            word_part = f"{random.choice(colors).capitalize()}{random.choice(nouns).capitalize()}"
        elif style == 1:
            # Adjective + Color + Noun 
            word_part = f"{random.choice(adjectives).capitalize()}{random.choice(colors).capitalize()}{random.choice(nouns).capitalize()}"
        else:
            # Adjective + Noun
            word_part = f"{random.choice(adjectives).capitalize()}{random.choice(nouns).capitalize()}"
        
        number_part = random.randint(1000, 9999)
        nickname = f"{word_part}_{number_part}"
        if is_nickname_available(nickname):
            break
    if reserve_nickname(nickname):
        return NicknameResponse(nickname=nickname)
    else:
        raise HTTPException(status_code=500, detail="Failed to reserve nickname")

def is_nickname_available(nickname: str) -> bool:
    response = supabase.table("nicknames").select("*").eq("nickname", nickname).execute()
    return response.data is None or len(response.data) == 0

def reserve_nickname(nickname: str) -> bool:
    insert_response = supabase.table("nicknames").insert({"nickname": nickname}).execute()
    return insert_response.data is not None