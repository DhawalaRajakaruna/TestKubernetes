# 🧭 Kubectl & Minikube – Practical Command Notes

> These notes assume **Minikube** and **kubectl** are already installed and configured.

---
## Make an image available in Minikube
```bash 
eval $(minikube docker-env) # Can enter to the docker env inside minkube
docker images
docker build -t web_api_image:latest . 

minikube image load web_api_image:latest # Can load the image from local
```

## 🔹 Basic kubectl command structure

```bash
kubectl <action> <resource> <name>
```

Example:

```bash
kubectl get pods
kubectl delete pod mypod
```

---

## 🔹 Minikube & cluster status

```bash
kubectl version --client     # kubectl client version
minikube status              # Minikube cluster status
kubectl get pods -A          # Pods in all namespaces
```

---

## 🔹 Nodes

```bash
kubectl get nodes            # List cluster nodes
```

Describe a specific node:

```bash
kubectl describe node minikube
```

This includes:

* Internal IP address
* Running pods on the node
* Pod IP range
* CPU & memory capacity

More details:

```bash
kubectl get nodes -o wide    # Node IPs and extra details
```

---

## 🔹 Pods

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl delete pod <pod-name>
```

⚠️ Deleting a pod managed by a **Deployment** will recreate it automatically.

---

## 🔹 Running a simple pod (no YAML)

```bash
kubectl run nginx-app --image=nginx --port=80
```

Delete it:

```bash
kubectl delete pod nginx-app
```

> This creates a **single pod**, not a Deployment.

---

## 🔹 Applying YAML manifests

```bash
kubectl apply -f pod.yaml     # Apply a single file
kubectl apply -f k8s/         # Apply all YAMLs in a folder
kubectl delete -f pod.yaml    # Delete resources from YAML
```

---

## 🔹 Deployments (recommended way)

Deployments:

* Manage **ReplicaSets**
* ReplicaSets manage **Pods**
* Automatically restart failed pods

Create a deployment:

```bash
kubectl create deployment nginx-deploy --image=nginx
```

Scale replicas:

```bash
kubectl scale deployment nginx-deploy --replicas=3
```

Delete deployment:

```bash
kubectl delete deployment nginx-deploy
```

Check deployments:

```bash
kubectl get deployments
```

---

## 🔹 Services (stable access to pods)

At this stage, no Service exists:

```bash
kubectl get services
```

Expose the Deployment using a **NodePort** service:

```bash
kubectl expose deployment nginx-deploy \
  --type=NodePort \
  --port=80
```

Now the Service is created:

```bash
kubectl get services
```

Example output:

```
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
nginx-deploy       NodePort    10.101.81.44    <none>        80:31077/TCP     3s
```

### 🔸 Port meaning (NodePort)

```
80       → Service port (inside cluster)
31077    → NodePort (external access via node IP)
```

---

## 🔹 Accessing the service (Minikube)

Recommended way:

```bash
minikube service nginx-deploy
```

Example output:

```
http://192.168.49.2:31077
```

Manual access:

```bash
curl http://$(minikube ip):31077
```

---

## 🔹 Service types (quick summary)

| Type         | Accessible outside cluster | Use case                |
| ------------ | -------------------------- | ----------------------- |
| ClusterIP    | ❌ No                       | Internal services (DBs) |
| NodePort     | ✅ Yes                      | Dev / Minikube          |
| LoadBalancer | ✅ Yes                      | Cloud environments      |

---

## 🔹 We can ping pod to pod directly but they dont have stable ip addresses
```bash
kubectl get pods -o wide # Can find the Ip addresses of the pods for now
kubectl exec -it nginx-deploy-6f47956ff4-h76p8 -- sh  
# If sh does not work
kubectl exec -it nginx-deploy-6f47956ff4-h76p8 -- bash 
```

```bash
# assume 
  # There is a service called "app-service"
  # forward the service by port forwarding
  # <LOCAL_PORT_in_Lap>:<SERVICE_PORT_in_Kubernetes>
kubectl port-forward scv/app-service 8000:8000
```
Then you can access the app locally
```bash 
#http://localhost:<port_in_the_lap>
http://localhost:8000
```

```bash
# Using this we can directly access the node
minikube service app-service
```
## To add a HPA (HorizontalPodAutoscale)

First need to have metrics-server
```bash
# To add metrics server to minikube
minikube addons enable metrics-server 

# After adding this can see the usages of the pods and nodes
kubectl top pods
kubectl top nodes
```
### To auto scale without Hpa
```bash 
kubectl autoscale deployment app-deployment \
  --cpu-percent=70 \
  --min=1 \
  --max=5
```



## 🔹 Important kubectl rules

* **Pods are disposable**
* **Deployments recreate pods**
* **Services give stable networking**
* Never expose databases using NodePort in production

---


