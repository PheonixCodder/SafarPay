# SafarPay Mobile App

Refactored microservices architecture with shared infrastructure.

## Architecture

- **Shared Libraries**: `libs/` - Configuration, Cache, Database, Messaging, Observability, Auth
- **Services**: `services/` - Auth, Bidding, Geospatial, Location, Notification, Verification, Gateway

## Key Improvements

- Centralized configuration management
- Shared async database layer with connection pooling
- Centralized Redis cache with standardized keys
- Event-driven messaging (Kafka/RabbitMQ)
- Structured JSON logging with OpenTelemetry support
- JWT-based authentication
- API Gateway with rate limiting
