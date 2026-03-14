## PyServer development environment

> [!Warning]
> This is a testing environment, do not use in production.

This folder contains the development environment for the AssetGuard 4.x versions. It includes the following components:

- **assetguard-master**: Master node.
- **assetguard-worker1**: Worker node #1.
- **assetguard-worker2**: Worker node #2.
- **nginx-lb**: NGINX load balancer to distribute agent connections among nodes.
- **assetguard-agent**: Agent.
- **assetguard-indexer**: Indexer

### Working with docker environment
The following commands runs a cluster:
1. Run `docker compose build`
2. Run `docker compose up`

If a single docker is needed, it is possible to run:
1. Move to the dockefile location for instance:
 `cd assetguard-manager`
2. Run `docker build -t dev-assetguard-manager --target server ./assetguard-manager`
3. Define .env with the necessary environment variables
4. Run docker:
```
docker run -d \
--name assetguard-master \
--hostname assetguard-master \
-p 55000:55000 \
-v ${ASSETGUARD_LOCAL_PATH}/framework/scripts:/var/assetguard-manager/framework/scripts \
-v ${ASSETGUARD_LOCAL_PATH}/api/scripts:/var/assetguard-manager/api/scripts \
-v ${ASSETGUARD_LOCAL_PATH}/framework/assetguard:/var/assetguard-manager/framework/python/lib/python${ASSETGUARD_PYTHON_VERSION}/site-packages/assetguard \
-v ${ASSETGUARD_LOCAL_PATH}/api/api:/var/assetguard-manager/framework/python/lib/python${ASSETGUARD_PYTHON_VERSION}/site-packages/api \
dev-assetguard-manager \
/scripts/entrypoint.sh assetguard-master master-node master
```
If we need more agents we can use:
`docker compose up --scale assetguard-agent=<number_of_agents>`

### Troubleshooting
- Use option **-no-cache** when you have building issues.

`docker compose build --no-cache`

- To completely clean the environment (including volumes), run:
  ```bash
  docker compose down -v
  ```
