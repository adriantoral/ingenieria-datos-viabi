# Compilar la imagen de la aplicación
docker build -t nilerdar/viabi-consumer:latest -f Dockerfile ..
docker push nilerdar/viabi-consumer:latest

# Crear el deployment y el service
kubectl apply -f consumer.yaml
