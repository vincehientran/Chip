import pybullet as p

# Initialize PyBullet and set up the simulation environment
p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Create a ground plane
plane_id = p.createCollisionShape(p.GEOM_BOX, halfExtents=[100, 100, 0.01])
p.createMultiBody(0, plane_id)

# Run the simulation
while True:
    p.stepSimulation()
