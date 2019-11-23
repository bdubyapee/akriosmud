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

import server
    
if __name__ == "__main__":
    game = server.Server()
    game.run()
