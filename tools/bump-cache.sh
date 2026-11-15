#!/bin/bash
# Setzt die Cache-Version in sw.js auf den Fingerabdruck von index.html.
# Nach jeder Änderung an index.html ausführen: ./tools/bump-cache.sh
cd "$(dirname "$0")/.." || exit 1
neu="aos-$(sha1sum index.html | cut -c1-12)"
sed -i.bak "s/^const CACHE = 'aos-[0-9a-f]*';/const CACHE = '$neu';/" sw.js && rm -f sw.js.bak
echo "Cache-Version: $neu"
