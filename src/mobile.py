#! usr/bin/env python
# Project: Akrios
# Filename: mobile.py
# 
# File Description: Eventually the home of the mobiles.
# 
# By: Jubelo

import event
import livingthing

class Mobile(livingthing.LivingThing):
    def __init__(self):
        super().__init__()
        
        self.ismobile = True
        self.keywords = []
        self.events = event.Queue(self, "mobile")
        event.init_events_mobile(self)
        
    def savedata(self):
        pass
    
    def loaddata(self):
        pass
