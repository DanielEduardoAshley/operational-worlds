from ow import Tile, Primitive, World

tile=Tile()

establish=Primitive(
    id="OW01",
    name="Establish",
    geometry="Circle",
    category="Boundary"
)

world=World()
world.add(establish)

print(tile)
print(world)
