# Compilar la imagen de la aplicación
docker build -t adriitoral/viabi-consumer:latest -f Dockerfile ..
docker push adriitoral/viabi-consumer:latest

# Crear el deployment y el service
kubectl apply -f consumer.yaml
