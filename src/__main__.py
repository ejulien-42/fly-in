from src.map_parser import Parser, ParseError
from src.GUI import GUI
from src.Pathfinder import Pathfinder
from src.Simulation import Simulation
import sys


def main() -> None:
    filename = "maps/medium/02_circular_loop.txt"
    parser = Parser()
    try:
        graph = parser.parse_file(filename)
        p = Pathfinder(graph)
        path = p.get_actual_path(p.dijkstra())
        if path is None:
            raise ValueError("Could not find any path through the graph.")
        sys.exit(1)
        sim = Simulation(path, graph)
        turns = sim.simulate()
        gui = GUI(graph)
        gui.run(turns)
    except ParseError as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected: closing...")
        sys.exit(0)


if __name__ == "__main__":
    main()
