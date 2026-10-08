class DKBSignError(Exception):
    """Erreur générale du SDK DKBSign."""
    pass


class DKBSignAPIError(DKBSignError):
    """Erreur provenant de l'API DKBSign."""
    pass