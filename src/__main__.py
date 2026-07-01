from src.map_parser import Parser, ParseError
from src.GUI import GUI
from src.Pathfinder import Pathfinder
from src.Simulation import Simulation
import sys


def choice() -> str:
    """Function to choose the desired map."""
    maps = [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/medium/02_circular_loop.txt",
        "maps/medium/03_priority_puzzle.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/hard/02_capacity_hell.txt",
        "maps/hard/03_ultimate_challenge.txt",
        "maps/challenger/01_the_impossible_dream.txt"
    ]
    print("Welcome to ejulien's fly-in. Please chose a map:\n")
    for i, m in enumerate(maps):
        print(f"{i + 1}: {m.split('/')[2]}")
    while True:
        print("")
        choice: int | str = input("Choice: ")
        try:
            choice = int(choice)
            if choice < 1 or choice > 10:
                raise ValueError
            try:
                with open(maps[choice - 1]) as _:
                    pass
            except FileNotFoundError:
                print("Error: maps not found. Please put the maps directory at"
                      " the root of the repository")
                sys.exit(1)
            return maps[choice - 1]
        except ValueError:
            print("Invalid choice, try again...")


def main() -> None:
    """Main function of the program."""
    try:
        filename = choice()
        parser = Parser()
        graph = parser.parse_file(filename)
        p = Pathfinder(graph)
        path = p.get_actual_path(p.dijkstra())
        if path is None:
            raise ValueError("Could not find any path through the graph.")
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
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
