"""Doménové výjimky s bezpečnými hláškami pro CLI a dashboard."""


class MikeError(RuntimeError):
    """Základní očekávaná chyba aplikace."""


class ConfigError(MikeError):
    """Konfigurace je neplatná nebo nebezpečná."""


class CollisionError(MikeError):
    """Instalaci nebo start blokuje cizí proces či port."""


class FeatureDisabledError(MikeError):
    """Uživatel výslovně nezapnul volitelnou schopnost."""


class PolicyError(MikeError):
    """Požadavek porušuje bezpečnostní politiku."""
