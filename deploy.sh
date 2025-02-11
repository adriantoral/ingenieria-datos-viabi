#!/bin/bash

NAMESPACE="monitoring-stack"

echo "🚀 Creando el namespace..."
kubectl apply -f namespace.yaml

echo "🟢 Desplegando RabbitMQ..."
kubectl apply -f rabbitmq/rabbitmq.yaml

echo "📊 Desplegando InfluxDB..."
kubectl apply -f influxdb/influxdb.yaml

echo "📡 Desplegando Telegraf..."
kubectl apply -f telegraf/telegraf-configmap.yaml
kubectl apply -f telegraf/telegraf.yaml

echo "📈 Desplegando Grafana..."
kubectl apply -f grafana/grafana.yaml

echo "🗄️ Desplegando MinIO como datalakehouse..."
kubectl apply -f minio/minio.yaml

echo "🌍 Creando servicios para exponer los pods..."
kubectl apply -f services.yaml

echo "⏳ Esperando a que los pods se inicien..."
kubectl wait --for=condition=Ready pod --all -n $NAMESPACE --timeout=300s

echo "✅ Stack desplegado exitosamente en Kubernetes!"
echo "🔍 Puedes verificar con: kubectl get pods -n $NAMESPACE"
