class MirrorContext:
    """Placeholder: passes through the first candidate unchanged."""
    @staticmethod
    def select(phrases, history=None):
        return phrases[0] if phrases else ""

