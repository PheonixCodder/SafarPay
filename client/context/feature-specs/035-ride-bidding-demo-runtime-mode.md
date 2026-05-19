# Ride And Bidding Demo Runtime Mode Prompt

Temporarily force the passenger ride, bidding, location, geospatial, and live socket integrations to return deterministic demo data because backend services are not currently available.

Preserve the real backend HTTP and WebSocket fetch/connect blocks as commented restore code directly beside each demo return. The client must remain easy to test now and easy to reconnect later.

Requirements:

- Ride repository methods return demo responses for all wired Ride service routes.
- Bidding repository methods return demo responses for all wired Bidding service routes.
- Location and Geospatial repositories return demo geocode, reverse-geocode, route, pickup-validation, surge, and ride-location data.
- Location live ride socket, Ride lifecycle socket, and Bidding negotiation socket repositories emit demo event streams.
- The bottom-sheet passenger matching UI must receive demo live bid/counter events without requiring backend services.
- Keep the production contract decisions intact:
  - Passenger UI supports `FIXED` and `HYBRID`.
  - Do not expose passenger-facing `BID_BASED`.
  - Mapbox remains map rendering only.
  - Backend calls remain documented in code for restoration.

When backend services are available again, remove the demo returns and restore the commented HTTP/WebSocket blocks.
