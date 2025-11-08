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
  const [isLoaded, setIsLoaded] = useState(false);

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
    if (!isLoaded || !inputRef.current) return;

    // Create autocomplete
    autocompleteRef.current = new window.google.maps.places.Autocomplete(inputRef.current, {
      bounds: new window.google.maps.LatLngBounds(
        new window.google.maps.LatLng(33.7656, -84.4063), // Southwest
        new window.google.maps.LatLng(33.7856, -84.3863)  // Northeast
      ),
      componentRestrictions: { country: 'us' },
      fields: ['place_id', 'geometry', 'name', 'formatted_address', 'types']
    });

    // Handle place selection
    const handlePlaceSelect = () => {
      const place = autocompleteRef.current.getPlace();
      if (place.geometry) {
        const coords = place.geometry.location;
        const placeData = {
          name: place.name || place.formatted_address,
          address: place.formatted_address,
          coordinates: `${coords.lat()},${coords.lng()}`,
          placeId: place.place_id,
          types: place.types
        };
        onPlaceSelect(placeData);
      }
    };

    autocompleteRef.current.addListener('place_changed', handlePlaceSelect);

    return () => {
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, [isLoaded, onPlaceSelect]);

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
