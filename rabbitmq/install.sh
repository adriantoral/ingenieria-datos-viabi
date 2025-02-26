# Instalar RabbitMQ Cluster Operator
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"

# Verificar que el operador se haya instalado correctamente
kubectl get all -n rabbitmq-system
kubectl get customresourcedefinitions.apiextensions.k8s.io

# Instalar RabbitMQ Cluster
kubectl apply -f rabbitmq.yaml
