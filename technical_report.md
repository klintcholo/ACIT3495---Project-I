# Technical Report — Student Grade Analytics

## 1. Security

The application separates authentication, grade submission, analytics, and results into individual services. The Authentication Service validates login credentials and issues JSON Web Tokens (JWTs). The Enter Data Service verifies tokens and validates grade submissions before storing them in MySQL. Invalid authentication and invalid grade data are rejected.

Database services are not directly exposed through published host ports. Application ports are bound to localhost, and credentials are configured through environment variables in a `.env` file rather than hard-coded in application code.

**Evidence:** `auth-service/app.py`, `enter-data/app.py`, `compose.yaml`, and `.gitignore`. Demonstrate rejected unauthenticated requests and invalid grade submissions. The current Trivy workflow reports high- and critical-severity vulnerabilities but uses `exit-code: "0"`, so findings do not automatically fail the build.

## 2. Reliability

Docker Compose health checks monitor service availability, while dependency conditions help ensure that dependent services start after their required databases become healthy. The recommended `restart: unless-stopped` policy supports recovery after unexpected container termination.

The Analytics Service handles errors during its periodic processing loop, allowing subsequent runs to retry failed operations.

**Evidence:** `compose.yaml`, service health endpoints, and `analytics/analytics.py`. Capture `docker compose ps` showing healthy services and logs demonstrating recovery or successful subsequent analytics updates. Confirm that restart policies are present in the final Compose configuration.

## 3. Optimization

The application separates responsibilities across services, allowing components to be built, tested, and maintained independently. Docker image builds use service-specific contexts, and the CI workflow can reuse build cache. Production images should install only necessary runtime dependencies and use multi-stage builds where appropriate.

CPU and memory limits can restrict resource consumption. These limits should be configured and adjusted based on observed usage rather than assumed to be optimal.

**Evidence:** Dockerfiles, `compose.yaml`, and the CI workflow. Show resource limits and any implemented multi-stage Dockerfile. Record `docker stats` output to support optimization decisions.

## 4. Performance

The Analytics Service periodically reads grades from MySQL, calculates the number of grades, minimum, maximum, and average, and stores the latest results in MongoDB. The Results Service retrieves the latest statistics through an API rather than recalculating them for every dashboard request.

This design reduces repeated statistical calculations during dashboard access. Actual response-time improvements have not been established without measurements.

**Evidence:** `analytics/analytics.py`, `results/server.js`, and the statistics endpoint at `http://localhost:3001/api/statistics`. Record response times and test results under a defined workload if performance measurements are required.

## 5. Persistence

MySQL stores submitted grades, while MongoDB stores calculated analytics results. Named Docker volumes preserve database files across ordinary container recreation and application shutdown.

**Evidence:** The volume declarations and database service configuration in `compose.yaml`. Demonstrate persistence by submitting a grade, recreating the containers without deleting volumes, and verifying that the grade remains available. The same principle applies to the stored analytics document.

Named volumes alone are not a backup strategy; production use would require a tested backup and restore procedure.

## 6. CI/CD Evidence

The GitHub Actions workflow automates application checks, Docker image builds, vulnerability scanning, and image publishing. The intended pipeline supports multi-architecture images for `linux/amd64` and `linux/arm64`. The workflow should include all four application services: `auth-service`, `enter-data`, `analytics`, and `results`.

Automated tests cover Analytics calculations and, once configured and passing, Results API behavior. Trivy provides visibility into image vulnerabilities.

**Evidence to include:**
- A successful GitHub Actions run showing completed checks and tests.
- Build logs for all four application services.
- Trivy scan output.
- Successful Docker Hub publishing steps.
- Output from `docker buildx imagetools inspect <image>:latest` confirming both `linux/amd64` and `linux/arm64`.
- Test output from the Analytics and Results test suites.

Multi-architecture support and successful CI/CD execution should be reported as verified only after the corresponding builds and publishing steps succeed.


