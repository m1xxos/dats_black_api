from pydantic import BaseModel


class CannonShot(BaseModel):
    x: int
    y: int


class Ship(BaseModel):
    id: int
    changeSpeed: int | None = None
    rotate: int | None = None
    cannonShoot: CannonShot | None = None


class ShipCommand(BaseModel):
    ships: list[Ship]
