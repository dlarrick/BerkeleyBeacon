import argparse
import signal
import sys

BEACON = 2

from conf import SEQUENCES, SLEEP_DURATION
from sequencer import ColorSequencer, turn_off

current_sequencer = None

def signal_handler(sig, frame):
    print(f"Got Ctrl+C, {current_sequencer=}")
    if current_sequencer:
        turn_off(beacon=BEACON)
        current_sequencer.stop()
    sys.exit(0)

def main() -> int:
    global current_sequencer
    parser = argparse.ArgumentParser(
        description="Test holiday Hue light sequences")
    parser.add_argument(
        "-s",
        "--sequence",
        type=str,
        metavar="sequence",
        required=True,
        help=f"Holiday to test, from {SEQUENCES.keys()}")
    args = parser.parse_args()

    sequencer = ColorSequencer(SLEEP_DURATION, debug=True, beacon=BEACON)
    sequence = SEQUENCES.get(args.sequence)
    if not sequence:
        print(f"Sequence {args.sequence} not in {SEQUENCES.keys()}")
        return 1
    sequencer.set_sequence(sequence)
    current_sequencer = sequencer
    sequencer.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == "__main__":
    sys.exit(main())
