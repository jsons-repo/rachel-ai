# Getting Started

[Installation](install.md)

[Configure LAN setup](lan_setup.md)

[Getting Started](getting_started.md)

[How It Works](how_it_works.md)

[config.yaml Reference](docs/config.md)

Once everything is installed and configured you can launch the app using the provided script:

#### Backend:
```bash
pip install -e .
start
```

This will start the **backend** (FastAPI).

> Note: Start the backend before the frontend due to config dependencies.

---

#### Front-end:
```bash
cd rachel-view
yarn install
yarn dev
```
This will start the **front end** (Node.JS and React)

### Default URLs

The app reads port and host settings from `config.yaml`. By default:

- **Backend** runs at:  
  ```
  {network.be.protocol}://{network.be.host}:{network.be.port}
  → http://localhost:7766
  ```

- **Frontend** runs at:  
  ```
  {network.fe.protocol}://{network.fe.host}:{network.fe.port}
  → http://localhost:6677
  ```

You can update these values in your `config.yaml` under the `network` section:

```yaml
network:
  fe:
    host: "localhost"
    port: 6677
    protocol: "http"
  be:
    host: "localhost"
    port: 7766
    protocol: "http"
```

Once both services are running:

- Open the app at your configured frontend URL (e.g., `http://localhost:6677`)
- API docs are available at /docs and /redoc (e.g., `http://localhost:6677/docs`)
- Transcripts and analysis will stream in as audio is processed
