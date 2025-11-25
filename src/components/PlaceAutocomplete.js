import React, { useEffect, useRef, useState } from 'react';

const PlaceAutocomplete = ({ 
  placeholder, 
  onPlaceSelect, 
  value, 
  onChange,
  className = "",
  id = ""
}) => {
  const inputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const onPlaceSelectRef = useRef(onPlaceSelect);
  const [isLoaded, setIsLoaded] = useState(false);
  
  // Update ref on every render (refs don't cause re-renders)
  onPlaceSelectRef.current = onPlaceSelect;

  useEffect(() => {
    // Check if Google Maps API is loaded
    if (window.google && window.google.maps && window.google.maps.places) {
      setIsLoaded(true);
    } else {
      // Wait for Google Maps API to load
      const checkGoogleMaps = setInterval(() => {
        if (window.google && window.google.maps && window.google.maps.places) {
          setIsLoaded(true);
          clearInterval(checkGoogleMaps);
        }
      }, 100);

      return () => clearInterval(checkGoogleMaps);
    }
  }, []);

  useEffect(() => {
    if (!isLoaded || !inputRef.current || autocompleteRef.current) return;

    // Create autocomplete with Atlanta bounds
    const atlantaBounds = new window.google.maps.LatLngBounds(
      new window.google.maps.LatLng(33.6, -84.5),  // Southwest
      new window.google.maps.LatLng(33.9, -84.3)    // Northeast
    );
    
    autocompleteRef.current = new window.google.maps.places.Autocomplete(inputRef.current, {
      bounds: atlantaBounds,
      componentRestrictions: { country: 'us' },
      fields: ['place_id', 'geometry', 'name', 'formatted_address', 'types']
    });

    // Handle place selection
    const handlePlaceSelect = () => {
      const place = autocompleteRef.current.getPlace();
      if (place.geometry) {
        const coords = place.geometry.location;
        // Use the exact name from the dropdown - don't let it change
        const selectedName = place.name || place.formatted_address;
        const placeData = {
          name: selectedName,
          address: place.formatted_address,
          coordinates: `${coords.lat()},${coords.lng()}`,
          placeId: place.place_id,
          types: place.types,
          fromAutocomplete: true  // Mark as selected from dropdown
        };
        onPlaceSelectRef.current(placeData);
      }
    };

    autocompleteRef.current.addListener('place_changed', handlePlaceSelect);

    return () => {
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
        autocompleteRef.current = null;
      }
    };
  }, [isLoaded]);

  return (
    <input
      ref={inputRef}
      type="text"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={className}
      id={id}
      autoComplete="off"
    />
  );
};

export default PlaceAutocomplete;
