# Deployment

This directory contains deployment configurations and scripts for various environments.

## Structure

### `/docker/`
Docker-related deployment files:
- `Dockerfile` - Main application Docker image
- `docker-compose.yml` - Multi-service development environment
- `docker-compose.prod.yml` - Production deployment configuration
- `nginx/` - Nginx configuration for web interface
- `scripts/` - Docker build and deployment scripts

### `/kubernetes/`
Kubernetes deployment manifests:
- `namespace.yaml` - Kubernetes namespace configuration
- `deployment.yaml` - Main application deployment
- `service.yaml` - Service definitions
- `configmap.yaml` - Configuration management
- `secrets.yaml` - Secrets management (template)
- `ingress.yaml` - Ingress configuration
- `hpa.yaml` - Horizontal Pod Autoscaler

### `/aws/`
AWS-specific deployment configurations:
- `cloudformation/` - CloudFormation templates
- `terraform/` - Terraform infrastructure as code
- `lambda/` - AWS Lambda deployment packages
- `ecs/` - ECS service definitions
- `s3/` - S3 bucket configurations

### `/scripts/`
Deployment automation scripts:
- `deploy.sh` - Main deployment script
- `health_check.sh` - Health check script
- `backup.sh` - Backup automation
- `rollback.sh` - Rollback procedures

## Deployment Options

1. **Local Development**: Use docker-compose for local development
2. **Container Orchestration**: Kubernetes manifests for scalable deployment
3. **Cloud Deployment**: AWS-specific configurations for cloud deployment
4. **Serverless**: Lambda functions for serverless extraction tasks

## Environment Variables

All deployments support configuration through environment variables:
- `SCRAG_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `SCRAG_CONFIG_PATH` - Path to configuration files
- `SCRAG_STORAGE_BACKEND` - Storage backend type
- `SCRAG_MAX_WORKERS` - Maximum number of worker processes