#!/usr/bin/env python3
import argparse

from src.automated_session import AutomaticSession
from src.handler_replay import HandlerReplay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('recording', help="recording path to replay")
    parser.add_argument('--game', default='SuperMarioBros-Nes', help='specifies ROM as imported into retro')
    args = parser.parse_args()

    handler = HandlerReplay(args.recording)
    session = AutomaticSession(game=args.game, handler=handler, skip_frames=0)
    session.play()


if __name__ == "__main__":
    main()