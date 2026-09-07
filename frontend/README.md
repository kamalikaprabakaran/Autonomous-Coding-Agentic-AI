# Frontend for Autonomous Coding Agentic AI

This is a Vite-based React + TypeScript frontend foundation for interacting with the FastAPI backend.

## Installation
Run `npm install` inside the `frontend` directory.

## Development
Run `npm run dev` to start the frontend server on port 5173.

## Environment Variables
Copy `.env.example` to `.env` or set `VITE_API_BASE_URL` locally. The React app reads this securely via `import.meta.env.VITE_API_BASE_URL`.

## Testing
Run `npm test` to execute the Vitest suite using React Testing Library.

## Build
Run `npm run build` to compile the TypeScript definitions and output the static bundle to `dist/`.
