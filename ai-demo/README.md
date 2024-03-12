# wasm-ai-kubecon-demo
This repo contains the pieces required to run WASM-integrated AI models in Kubernetes with CRI-O

# Running WASM-Integrated AI Models in Kubernetes with CRI-O

This guide demonstrates how to run WebAssembly (WASM)-integrated AI models in Kubernetes using CRI-O. We'll cover building a customized crun-wasm package, configuring CRI-O, and deploying a Kubernetes pod running a WASM-enabled container.

## Prerequisites

Ensure you have the following prerequisites installed:

- Fedora/CentOS/RHEL OS
- [CRI-O](https://github.com/cri-o/cri-o)
- [Podman](https://podman.io/) (for building and pushing the container image)
- [Kubernetes](https://kubernetes.io/)

## Step 1: Building crun-wasm with wasi-nn support

You can use these [instructions](https://www.redhat.com/sysadmin/create-rpm-package) to build customized `crun-wasm` package. Alternatively, you can directly install the `crun-wasm` package from `rpmbuild/RPMS/x86/`

```bash!
$ git clone https://github.com/sohankunkerkar/wasm-ai-kubecon-demo
$ rpm -ivh rpmbuild/RMPS/x86/crun-wasm-1.14.4-1.fc39.x86_64.rpm
```
## Step 2: Configure CRI-O
1. Clone the cri-o repository and apply the patch.
```bash=
git clone https://github.com/cri-o/cri-o.git
cd cri-o
git apply 0001-add-runtime_env-to-crio-runtimeconfig.patch
```
2. Build the crio binary
```bash
$ make binaries
```
3. Create the CRI-O configuration file (crio-wasm.conf):
```toml
[crio.runtime]
default_runtime = "crun-wasm"

[crio.runtime.runtimes.crun-wasm]
runtime_path = "/usr/bin/crun"
runtime_env = [
    "WASMEDGE_PLUGIN_MOUNT=$HOME/.wasmedge/plugin",
]
platform_runtime_paths = {"wasi/wasm32" = "/usr/bin/crun-wasm"}
```

4. Run CRI-O with the custom configuration:
```bash
$ sudo ./bin/crio --config crio-wasm.conf
```

## Step 3: Building and Pushing the WASM-Enabled Container Image

1. Building and Pushing the WASM-Enabled Container Image
Create a Containerfile for your application (e.g., llama-chat.wasm):
```dockerfile=
FROM scratch

# This will load the necessary plugin required to AI models
ENV WASMEDGE_PLUGIN_PATH=${WASMEDGE_PLUGIN_PATH:-"/usr/lib/wasmedge"}
# Option to set the model
ENV WASMEDGE_WASINN_PRELOAD=${WASMEDGE_WASINN_PRELOAD:-"default:GGML:AUTO:model.gguf"}

WORKDIR /app

COPY llama-chat.wasm /app

ENTRYPOINT ["/app/llama-chat.wasm"]
```
2. Build and push the container image:
```bash
$ podman build --platform wasi/wasm32 -t quay.io/sohankunkerkar/llama-crun:v2 .
$ podman push quay.io/sohankunkerkar/llama-crun:v2
```

## Step 4: Creating and Interacting with the Kubernetes Pod
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

2. Set SELinux to permissive mode since we are mounting the wasmedge plugin directory to the container. Otherwise, you might get this error while running a wasm workload:
```inf=
write file `/proc/thread-self/attr/current`: Permission denied
```

```bash
$ sudo setenforce 0
```
3. This Pod definition will mount the volume containing the Llama2 model into the /app directory within the llama-container.
```bash
$ mkdir -p wasm-test
$ cd wasm-test
$ curl -LO https://huggingface.co/wasmedge/llama2/resolve/main/llama-2-7b-chat-q5_k_m.gguf && mv llama-2-7b-chat-q5_k_m.gguf model.gguf

```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llama-pod
spec:
  containers:
  - name: llama-container
    image: quay.io/sohankunkerkar/llama-crun:v2
    volumeMounts:
    - name: wasm-volume
      mountPath: /app
    stdin: true
    tty: true
  volumes:
  - name: wasm-volume
    hostPath:
      path: /path/to/wasm-test
  restartPolicy: Never
 ```
 
4. Create the pod:
```bash
$ kubectl apply -f llm-wasm.yaml
```

5. View logs and interact with the container:
```bash
$ kubectl logs llama-pod
```

6. Interact with bot wiht the following command:
```bash
$ kubectl attach llama-pod -c llama-container -i -t
```

## Credits
The example container application and model used in this tutorial are based on the LLM Inference [tutorial](https://wasmedge.org/docs/develop/rust/wasinn/llm_inference/) provided by WASMedge.
