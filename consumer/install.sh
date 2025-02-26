# Compilar la imagen de la aplicación
docker build -t consumer-deployment:latest -f Dockerfile ..

# Crear el deployment y el service
kubectl apply -f consumer.yaml
