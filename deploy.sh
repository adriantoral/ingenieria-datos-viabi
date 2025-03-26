kubectl apply -f namespace.yaml
echo "Namespace created"

for dir in */; do
  if [ -f "$dir/install.sh" ]; then
    echo "Installing $dir"
    bash "$dir/install.sh"
  fi
done

echo "All services installed"
