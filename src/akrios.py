#! usr/bin/env python
# Project: Akrios
# Filename: akrios.py
# 
# File Description: Main "startup" file for Akrios.
# 
# By: Jubelo

"""
    Starting point for launching AkriosMUD.
"""

import logging

import server
from world import serverlog
    
if __name__ == "__main__":
    logging.basicConfig(filename=serverlog, filemode='w',
                        format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    game = server.Server()
    game.run()
