# CLAUDE.md

This file provides comprehensive guidance for Claude Code when working with VD Group Member Management System - a sophisticated member display platform for VRC Division QQ group featuring 3D visualizations, secure data management, and immersive user experience.

## Project Architecture

### System Overview
- **Frontend**: Vue 3.5 + TypeScript + Three.js + GSAP for advanced 3D visualizations
- **Backend**: FastAPI + PostgreSQL + SQLModel with AES-256 encryption for security
- **Environment**: Windows, frontend-backend separated architecture with nginx reverse proxy
- **Domain**: Production accessed via tomo-loop.icu through nginx port 80
- **Build**: Deploy.sh for production deployment, scripts directory for dev/prod workflows

### Key Design Decisions
- Frontend-backend separated development with unified production build
- Asynchronous database drivers (asyncpg) with SQLModel ORM
- Global member data caching with async-safe locks
- Theme color coordination using OKLCH color space + WCAG standards
- UIN encryption/decryption moved from frontend to backend for security
- API versioning with /api/v1 prefix for all endpoints

## Quick Start Commands

### Development Environment
```bash
# Start full development stack (backend + frontend)
./scripts/dev.bat     # Windows
./scripts/dev.sh      # macOS/Linux

# Individual services
# Backend (http://localhost:8000)
cd src/backend
uv run python run.py

# Frontend (http://localhost:5173)
cd src/frontend
pnpm dev
```

### Production Build & Deploy
```bash
# Build frontend
./scripts/prod.bat     # Windows
./scripts/prod.sh      # macOS/Linux

# Manual build
cd src/frontend && pnpm build
```

### Testing & Quality
```bash
# Backend tests
cd src/backend
uv run pytest            # Run all tests
uv run pytest -v         # Verbose output
uv run pytest test_db_service.py  # Specific test file

# Frontend tests  
cd src/frontend
pnpm type-check          # TypeScript check
pnpm build              # Build to test
```

## Directory Structure

### Backend Organization (src/backend)
```
backend/
├── api/v1/               # REST API endpoints under /api/v1 prefix
├── services/             
│   ├── database/
│   │   ├── models/       # Table models organized by table name
│   │   ├── crud/         # CRUD operations per table
│   │   └── base/         # Base models
│   └── deps.py          # Dependency injection patterns
├── domain/               # Business logic services
└── scripts/              # Data import/processing utilities
```

### Frontend Organization (src/frontend)
```
frontend/
├── src/
│   ├── components/       # Vue components organized by feature
│   ├── views/           # Page-level components
│   ├── stores/          # Pinia state management modules
│   │   ├── auth.ts      # Authentication state
│   │   └── members.ts   # Member data state
│   ├── services/        # API service layer
│   │   └── api.ts       # Backend API integration
│   └── utils/           # 3D/gfx utilities (three.js, gsap)
├── scripts/             # Deployment and build scripts
├── static/              # Production build artifacts
└── logs/                # Application logs (project root)
```

## Development Standards

### Backend Specifications
- **API Routing**: All endpoints under `/api/v1` prefix with centralized router management
- **Database Models**: Organized by table name in `services/database/models/` with base/crud separation
- **Asynchronous Operations**: Async database drivers with dependency injection from `services/deps.py`
- **Security**: Authentication required for all endpoints except homepage data and login/logout
- **Caching**: Global dict caching with MemberCache module using async-safe read/write locks
- **Migrations**: Alembic commands executed as `python -m alembic` in `src/backend` directory

### Frontend Architecture
- **Technology Stack**: Vue 3.5 + TypeScript + NaiveUI + Pinia + Vue Router + GSAP + Three.js + SCSS
- **State Management**: Pinia stores for auth (auth.ts) and member data (members.ts)
- **Routing Structure**:
  - `/` - Homepage with member nebula display
  - `/badge-preview` - 3D badge preview interface
  - `/login` - Administrator authentication
  - `/settings` - Backend management with protected sub-routes
- **Theme System**: 6-layer architecture with OKLCH color space and WCAG compliance

### Core UI Features
- **Stargate**: 2D SVG implementation with three concentric circles (#AA83FF/#D4DEC7/#3F7DFB) and GSAP breathing
- **Member Display**: Random scattered layout with 40-50 members per screen, horizontal pagination
- **Connection Lines**: Dynamic breathing effects (sin(πt) alpha 0→1→0) with curved quadratic lines
- **3D Effects**: Three.js scenes with bloom effects, parallax starfields, particle systems
- **Authentication**: Backend-only UIN encryption, admin role badges in light green

## Production Environment
- **Domain**: tomo-loop.icu via nginx port 80
- **CORS**: Configured for tomo-loop.icu domain
- **Debug**: DEBUG=false in production
- **Logging**: Logs in project root (prevent uvicorn hot-reload conflicts)
- **Build**: Deploy.sh for production deployment over fix scripts

### Key Features Overview

#### 3D Badge Preview Features
- Image upload and positioning on curved badge surfaces
- Real-time manipulation: drag, rotate, scale with adjustable lighting
- Top-bottom layout: rendering area (top) + parameter controls (bottom)
- Customizable black background for optimal visibility
- Realistic badge geometry: curved surfaces, semi-circular edges

#### Cache Management
- Global dict caching with MemberCache module using async-safe locks
- Integration into CRUD operations (cache-first reads, sync on updates)
- Dashboard integration for cache monitoring and management

#### Theme System
- 6-layer architecture: state → provider → config → UI → color science → styles
- OKLCH color space with WCAG contrast validation
- Dark theme throughout with light green admin badges

### Common Tasks

#### Add New Members
```bash
cd src/backend
uv run python scripts/import_group_json.py static/qq_group_*.json
uv run python scripts/verify_import.py
```

#### Database Management
```bash
# Database migration
cd src/backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head

# Reset/debug database
uv run python debug_auth.py
```

#### Performance Optimization
- **Backend**: MemberCache module with async-safe locks for repeated queries
- **Frontend**: DevicePixelRatio scaling for HiDPI displays, canvas.width = rect.width * dpr
- **Monitoring**: 
  ```bash
  # Check backend diagnostics
  http://localhost:8000/health
  
  # Frontend performance monitor
  In browser console: `window.VITE_PERFORMANCE_MONITOR=true`
  ```

#### Special Instructions
- **Navigation**: Remove navigation from new window interfaces entirely
- **Theme Colors**: Non-transparent modals for text visibility, dark theme throughout
- **Canvas Rendering**: Scale context for HiDPI, immediate link activation on mount
- **Role Management**: Light green admin badges, remove contribution metrics
- **UI Consistency**: Dashboard.vue style titles, MemberManagement.vue table styles

## Configuration

### Environment Files
- **Backend**: `.env` (copy from `.env.example`)
- **Frontend**: `.env.development` or `.env.production`

### Key Environment Variables
```bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/vd_index
AVATAR_ROOT=./static/avatars/mems
UIN_AES_KEY=your-32-character-key  # Optional

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_3D_EFFECTS=true
```

## Package Management

### Backend (uv - Python)
```bash
cd src/backend
uv sync                 # Install dependencies
uv add package_name     # Add new dependency
uv remove package_name  # Remove dependency
```

### Frontend (pnpm - Node.js)
```bash
cd src/frontend
pnpm install           # Install dependencies
pnpm add package_name   # Add new dependency
pnpm remove package_name # Remove dependency
```

## Testing Commands

### Backend Testing
```bash
cd src/backend
uv run pytest                           # All tests
uv run pytest -k test_database          # Filter tests
uv run pytest -x --tb=short             # Stop on first failure
uv run pytest test_database_service.py::test_member_count  # Specific test
```

### Frontend Testing
```bash
cd src/frontend
pnpm type-check                        # TypeScript validation
pnpm build                            # Build test
npm run test                          # Run tests (if available)
```

## Build Process

### Build Flow
1. **Frontend**: `pnpm build` → outputs to `frontend/dist/`
2. **Backend Integration**: Built frontend assets copied to `static/`
3. **Static Serving**: Backend serves `/` in production mode

### Production Build
```bash
# Complete process
./scripts/prod.sh     # Automated full build

# Manual process
cd src/frontend && pnpm build
cd ../../ && cp -r src/frontend/dist/* static/
```

## Troubleshooting

### Common Issues
- **Postgres connection**: Ensure DATABASE_URL is correct, PostgreSQL running
- **Avatar 404s**: Run import scripts and verify avatar files in `static/avatars/mems/`
- **Frontend proxy**: Vite dev server proxies `/api` to backend:8000
- **SSL/Heroku**: Read `logs/` files for detailed error messages

### Development Debugging
```bash
# Backend logs
tail -f logs/app.log

# Frontend console errors
Browser F12 → Console tab

# Database verification
cd src/backend && uv run python test_database_connection.py
```