import sys

from bridge import BRIDGE


BEACON = 2

def main() -> int:
    light = BRIDGE.lights[BEACON]()
    state = light.get("state", {})
    attrs = ['name', 'on', 'bri', 'hue', 'sat', 'xy']
    for attr in attrs:
        if attr in state:
            print(f"{attr}: {state[attr]}")

if __name__ == "__main__":
    sys.exit(main())
