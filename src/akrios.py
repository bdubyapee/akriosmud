#! usr/bin/env python
# Project: Akrios
# Filename: akrios.py
# 
# File Description: Main "startup" file for Akrios.
# 
# By: Jubelo

#import cProfile
import server
    
if __name__ == "__main__":
    game = server.Server()
    game.run()
    #cProfile.run(game.run())
