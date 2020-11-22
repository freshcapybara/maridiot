#!/usr/bin/env python

import argparse

from src.retro_session import RetroSession


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', default='SuperMarioBros-Nes', help='specifies ROM as imported into retro')
    parser.add_argument('--state', default=None)
    parser.add_argument('--scenario', default='scenario')
    parser.add_argument('--directory', type=str, default='recordings', help='directory where the recordings should be saved to')
    parser.add_argument('--record', action='store_true', default=False, help='if the user session should be recorded')
    args = parser.parse_args()

    session = RetroSession(game=args.game, scenario=args.scenario, save_directory=args.directory, record_session=args.record, state=args.state)
    session.run()


if __name__ == '__main__':
    main()