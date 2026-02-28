interface PlanetStats {
  mass: number;
  radius: number;
}

function calculateGravity(stats: PlanetStats): number {
  const G = 6.6743e-11;
  return (G * stats.mass) / (stats.radius * stats.radius);
}

console.log(calculateGravity({ mass: 5.972e24, radius: 6371000 }));
