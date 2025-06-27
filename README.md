# Lochlan’s Location Locator API

A simple REST API for locating places by name.

## Prerequisites

- [Docker](https://www.docker.com/get-started) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/location-locator.git
   cd location-locator
   ```

2. **Build and run with Docker Compose**

From the project root (where docker-compose.yml lives), simply run:

```
 docker compose up --build
```

This will:

- Build the API image
- Start the server on port 80

## Testing

Once the containers are up:

```
curl http://localhost:80
```

You should see:

```
{"message":"Welcome to Lochlan's Location Locator API"}
```
