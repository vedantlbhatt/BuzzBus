BuzzBus: An alternative public transporation tracker for the Georgia Institute of Technology

Current Problems in tracking:
- clunky + outdated UI
- difficulty navigating campus maps + routes
- complex view

Proposed Solution: 
- using Haversine formula to determine closest stops to both the user & destination accounting for Earth's curvature
- developing an algorithm to find a single or combination of bus stops to get to destination in the fastest amount of time -> blackbox the messy + complex map visual 
- designing a modern + easy-to-navigate interface

The goal is to create a "google-maps" type feature where users can input current and goal locations and be able to access multiple routes of varying times that meets their needs instead of having to scour the map itself

### Demo Video
[Watch the demo video](https://youtu.be/LZudv5DxLjM)

Current state:
Very simple prototype for the feature I am trying to implement. Uses a simple heuristic of finding stops that are close the the starting and ending locations and finding a common route/bus that is closest in common to both locations. 

Future:
Future plans will include accounting for the time the user takes to get to the starting location, the actual transport time, and the time the user needs to go from ending bus stop to their destination + using Google Map APIs and more of the TransLoc API for more accurate tracking.
