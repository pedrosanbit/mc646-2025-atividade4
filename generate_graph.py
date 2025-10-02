from staticfg import CFGBuilder
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a control flow graph (CFG) from a Python script.")
    parser.add_argument("-s", "--script", help="Path to the Python script file.")
    parser.add_argument("-n", "--name", help="Name for the output CFG image file.", default="cfg_output")
    args = parser.parse_args()

    cfg = CFGBuilder().build_from_file(args.name, args.script)

    cfg.build_visual(f"cfg/{args.name}", "png")
