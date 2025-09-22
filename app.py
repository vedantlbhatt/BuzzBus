import streamlit as st

# Paste your buildings with coordinates dictionary
BUILDINGS = {
    "Tech Tower": (33.772389, -84.394722),
    "Georgia Tech Library": (33.7743, -84.3956),
    "Clough Commons": (33.7747, -84.3963),
    "Hopkins Hall": (33.7760, -84.3993),
    "Folk Hall": (33.7726, -84.4032),
    "Montag Hall": (33.7736, -84.4012),
    "Student Center": (33.7744, -84.3987),
    "Campus Rec Center": (33.7735, -84.4036),
    "D.M. Smith": (33.7728, -84.3950),
    "Bobby Dodd Stadium": (33.7718, -84.3931),
}

def your_route_function(begin_coord, dest_coord):
    # Replace this placeholder with the full function you wrote
    # that finds the best route, e.g., your 'best_route' logic
    # Return a string describing the route summary
    return f"Calculated best route from {begin_coord} to {dest_coord}."

# Streamlit app UI
st.title("Georgia Tech Route Finder")

begin_building = st.selectbox("Select Beginning Building", list(BUILDINGS.keys()))
dest_building = st.selectbox("Select Destination Building", list(BUILDINGS.keys()))

if st.button("Find Route"):
    begin_coord = BUILDINGS[begin_building]
    dest_coord = BUILDINGS[dest_building]
    # Call your complex route function using coordinates
    result = your_route_function(begin_coord, dest_coord)
    st.write(result)
