# Deploying WASM-Enabled Containers with CRI-O

## Building CRI-O from the Latest Main Branch
1. Clone the CRI-O repository:
bash
```bash
git clone https://github.com/cri-o/cri-o.git
cd cri-o
```
2. You can either use the CRI-O releases >= 1.27 or build it from the main branch:

```bash
$ make binaries
```
### Configure CRI-O:
Create the CRI-O configuration file (crio-wasm.conf):

```toml
[crio.runtime]
default_runtime = "crun-wasm"

[crio.runtime.runtimes.crun-wasm]
runtime_path = "/usr/bin/crun"
platform_runtime_paths = {"wasi/wasm32" = "/usr/bin/crun-wasm"}
```

### Run CRI-O with the custom configuration:
```bash
sudo crio --config crio-wasm.conf
```

### Creating and Interacting with the Kubernetes Pod
1. Create a Kubernetes cluster with CRI-O as the contianer runtime
```bash
$ git clone git@github.com:kubernetes/kubernetes.git
$ cd kubernetes
(I used this direnv settings for running a cluster with CRI-O)
$ cat .envrc 
#!/bin/sh
IP=192.168.1.16
echo "Using IP: $IP"
export GOPATH=/home/skunkerk/dev
export GO_OUT=./_output/local/bin/linux/amd64/
export KUBE_PATH=$GOPATH/src/k8s.io/kubernetes
export PATH=$PATH:$GOPATH/bin:$KUBE_PATH/third_party/etcd:$KUBE_PATH/_output/local/bin/linux/amd64/
export CONTAINER_RUNTIME=remote
export CGROUP_DRIVER=systemd
export CONTAINER_RUNTIME_ENDPOINT='unix:///var/run/crio/crio.sock'
export ALLOW_SECURITY_CONTEXT=","
export ALLOW_PRIVILEGED=1
export DNS_SERVER_IP=$IP
export API_HOST=$IP
export API_HOST_IP=$IP
export KUBELET_HOST=$IP
export HOSTNAME_OVERRIDE=$IP
export KUBE_ENABLE_CLUSTER_DNS=true
export ENABLE_HOSTPATH_PROVISIONER=true
export KUBE_ENABLE_CLUSTER_DASHBOARD=true
export KUBELET_FLAGS="--anonymous-auth=true --authorization-mode=AlwaysAllow --resolv-conf=/run/systemd/resolve/resolv.conf --config=/tmp/kubelet-config"
export KUBELET_READ_ONLY_PORT="10255"

$ ./hack/local-up-cluster.sh
```

2. Deploying a Pod with a WASM-Enabled Container

```yaml
Copy code
apiVersion: v1
kind: Pod
metadata:
  labels:
    name: http-server
  name: http-server
  namespace: default
spec:
  containers:
    - name: http-server
      image: quay.io/crio/example-wasm-http:latest
      command: ["/http_server.wasm"]
      ports:
        - containerPort: 1234
          protocol: TCP
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
      livenessProbe:
        tcpSocket:
          port: 1234
        initialDelaySeconds: 3
        periodSeconds: 30
```

```bash
$ kubectl apply -f http-server.yaml
```
### Using Curl to Interact with the HTTP Server
1. Retrieve the IP address of the pod:
```bash
$ kubectl get pods -o wide
```
2. Use curl to interact with the HTTP server:
```bash
curl -d "Hello world" -X POST http://<pod_ip>:1234
```
Replace <pod_ip> with the IP address of the pod obtained from the previous step.
