

def get_last_token(response: str | None) -> str:
        """Devuelve el último token no vacío de una respuesta SCPI."""
        if not response:
            return ""
        response = response.replace(",", " ").replace(":", " ").replace('"', "").strip()
        parts = response.split()
        return parts[-1] if parts else ""