class BOMError(Exception):
    """Base exception for BOM operations."""


class ItemNotFoundError(BOMError):
    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Item not found: {sku}")


class BOMNotFoundError(BOMError):
    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"BOM not found for item: {sku}")


class CycleError(BOMError):
    def __init__(self, path: list[str]) -> None:
        self.path = path
        super().__init__(f"BOM cycle detected: {' -> '.join(path)}")
