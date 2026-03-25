from __future__ import annotations

import math
import string

from synthetic_profiles.models.schemas import GeneratedPassword
from synthetic_profiles.utils.randomizer import GenerationContext


class PasswordGenerator:
    """Gera senhas fortes e estima a entropia."""

    def generate(
        self,
        context: GenerationContext,
        *,
        length: int,
        uppercase: bool = True,
        lowercase: bool = True,
        digits: bool = True,
        symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> GeneratedPassword:
        pools: list[str] = []
        if uppercase:
            pools.append(string.ascii_uppercase)
        if lowercase:
            pools.append(string.ascii_lowercase)
        if digits:
            pools.append(string.digits)
        if symbols:
            pools.append("!@#$%^&*()-_=+[]{}:,.?")
        rng = context.rng("password")

        characters = "".join(pools)
        if exclude_ambiguous:
            ambiguous = set("O0Il1|")
            characters = "".join(char for char in characters if char not in ambiguous)
            pools = ["".join(char for char in pool if char not in ambiguous) for pool in pools]

        if not characters or any(not pool for pool in pools):
            raise ValueError("O conjunto de caracteres da senha não pode estar vazio")

        password_chars = [rng.choice(pool) for pool in pools]
        while len(password_chars) < length:
            password_chars.append(rng.choice(characters))
        rng.shuffle(password_chars)
        password = "".join(password_chars[:length])
        entropy = round(math.log2(len(characters) ** length), 2)
        strength = "very_strong" if entropy >= 100 else "strong" if entropy >= 72 else "moderate"
        return GeneratedPassword(value=password, length=length, entropy_bits=entropy, strength=strength)
