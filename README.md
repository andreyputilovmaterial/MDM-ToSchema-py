# MDM-ToSchema-py

Builds a JSON schema (a `pydantic` model) from an MDD file. It reads the MDD through
the COM API of IBM/Unicom Professional (Windows + Professional required, like
`mdmreadpy`) and prints the derived JSON schema.

## Requirements

- Python 3.
- `pydantic` (see `requirements.txt`).
- On Windows, to actually open an MDD: `pywin32` (`win32com.client`). The import is
  lazy, so the module can be imported anywhere and only fails when an MDD is opened.

## Three ways to launch

As everywhere in this toolchain, the program can be started three equivalent ways:

1. **Single-file bundle** (distribution). `build.bat`/`build.sh` would produce
   `dist/mdmtoolsap_bundle.py` and append `from src import launcher; launcher.main()`
   (pinliner bundling is currently disabled in `build.bat`, so this is not produced
   yet). Prepare the environment with `run_init`, then run the bundle with the venv
   Python:

   ```
   run_init.sh
   ./.venv/bin/python dist/mdmtoolsap_bundle.py --program mdd_to_schema --inp file.mdd
   ```

2. **Direct module** (development). Run the entry-point module directly:

   ```
   python src/read_mdd.py --inp file.mdd
   ```

3. **Launcher proxy** (development). Run the universal dispatcher directly:

   ```
   python src/launcher.py --program mdd_to_schema --inp file.mdd
   ```

   > Note: `src/launcher.py` currently references a `build_schema` module that is not
   > implemented yet; the direct module (`src/read_mdd.py`) is the working entry point.

## Build

`build.bat` (Windows) / `build.sh` (macOS/Linux) regenerate
`src/GENERATED/_VERSION.py`, copy LICENSE/README/requirements into `dist/`, and copy
`run_init.bat`/`run_init.sh` into `dist/`. `run_init` creates a `.venv` and installs
this package's `requirements.txt`.

