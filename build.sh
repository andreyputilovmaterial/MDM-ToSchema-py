#!/usr/bin/env bash
# POSIX (macOS / Linux) counterpart of build.bat.
# NOTE: pinliner bundling is intentionally disabled here for now (see build.bat).

set -u

echo "Clear up dist/..."
rm -rf dist
mkdir -p dist

echo "-"
echo "-"
echo "Update program version"
mkdir -p src/GENERATED
printf "%s\n" "'''For auto-generated files'''" > src/GENERATED/__init__.py
printf "%s\n" "# THIS IS AUTO-GENERATED" > src/GENERATED/_VERSION.py
python -c "from datetime import datetime; print(f'# {datetime.now()}')" >> src/GENERATED/_VERSION.py
printf "%s\n" "_VERSION = '''" >> src/GENERATED/_VERSION.py
git describe --tags --dirty >> src/GENERATED/_VERSION.py
printf "%s\n" "'''" >> src/GENERATED/_VERSION.py
echo "Done"

echo "-"
echo "-"
echo "Bring LICENSE, README.md and requirements.txt to dist..."
if [ ! -f requirements.txt ]; then
    printf "%s\n" "# Runtime dependencies, one per line." > requirements.txt
fi
cp LICENSE dist/LICENSE
cp README.md dist/README.md
cp requirements.txt dist/requirements.txt
echo "Done"

echo "-"
echo "-"
echo "Copy and adapt run_init scripts to dist..."
sed -e 's#src/lib#optional_dependencies#g' run_init.sh > dist/run_init.sh
sed -e 's#src\\lib#optional_dependencies#g' run_init.bat > dist/run_init.bat
chmod +x dist/run_init.sh
chmod +x dist/run_init.bat
echo "Done"

echo "-"
echo "-"
echo "All done, the end"
