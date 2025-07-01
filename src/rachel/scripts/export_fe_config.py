# src/rachel/scripts/export_fe_config.py

import os, sys
import os
from pathlib import Path
from rachel.core.config import get_config

if __name__ == "__main__":
    """
This script reads the current Rachel backend configuration (via get_config)
and generates a frontend-compatible TypeScript file (`sharedConfig.ts`) that exports
selected config values as constants. This allows the frontend to stay in sync
with backend settings such as network addresses, model parameters, and audio chunking.

Expected to be run from the `rachel-view` project root (set by Node via `cwd`).

Output:
- Generates or overwrites: `rachel-view/src/sharedConfig.ts`

Exported Constants:
- FE_HOST, FE_PORT, FE_PROTOCOL: Frontend server configuration
- BE_HOST, BE_PORT, BE_PROTOCOL: Backend API configuration
- DEEP_NAME, DEEP_SEARCH_TEMP, DEEP_TEMP: Deep LLM settings
- CHUNK_DURATION, OVERLAP_DURATION: Audio processing parameters

"""


    config = get_config()
    network = config.network
    audio = config.audio
    deep = config.model.deep_LLM

    repo_root = Path(__file__).resolve().parents[2]
    ts_output = Path.cwd() / "src/sharedConfig.ts"
    os.makedirs(ts_output.parent, exist_ok=True)

    with open(ts_output, "w") as out:
        out.write("// AUTO-GENERATED FROM config.yaml via export_fe_config.py\n")
        out.write(f"export const FE_HOST = '{network.fe.host}';\n")
        out.write(f"export const FE_PORT = {network.fe.port};\n")
        out.write(f"export const FE_PROTOCOL = '{network.fe.protocol}';\n")
        out.write(f"export const BE_HOST = '{network.be.host}';\n")
        out.write(f"export const BE_PORT = {network.be.port};\n")
        out.write(f"export const BE_PROTOCOL = '{network.be.protocol}';\n")
        out.write(f"export const DEEP_NAME = '{deep.name}';\n")
        out.write(f"export const DEEP_SEARCH_TEMP = {deep.deep_search_temp};\n")
        out.write(f"export const DEEP_TEMP = {deep.deep_search_temp};\n")
        out.write(f"export const CHUNK_DURATION = {audio.chunk_duration};\n")
        out.write(f"export const OVERLAP_DURATION = {audio.overlap_duration};\n")

    print(f"✅ Wrote sharedConfig.ts to {ts_output}")
