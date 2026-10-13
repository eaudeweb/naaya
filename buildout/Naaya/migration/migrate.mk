# Python 2 to Python 3 Data.fs migration; include it after setting INSTANCE and DATAFS
MIGRATION := $(dir $(lastword $(MAKEFILE_LIST)))
PIP ?= bin/pip

.PHONY: migrate

migrate:
	@echo "=== Migrating $(DATAFS) with $(INSTANCE) ==="
	@MARKER_DIR=$$(dirname "$(DATAFS)"); \
	if [ ! -f "$$MARKER_DIR/.zodbupdate-done" ]; then \
		echo "[Step 0] Ensuring zodbupdate is installed"; \
		$(PIP) install -q zodbupdate; \
		echo "[Step 1/3] Convert to Python 3 (utf-8, binary attributes kept as bytes)"; \
		printf FS30 | dd of="$(DATAFS)" bs=4 count=1 conv=notrunc status=none && \
		parts/$(INSTANCE)/bin/interpreter $(MIGRATION)py3migration/analyze_py2.py "$(DATAFS)" "$$MARKER_DIR/py2-analysis.json" && \
		parts/$(INSTANCE)/bin/interpreter $(MIGRATION)py3migration/convert_py3.py "$(DATAFS)" "$$MARKER_DIR/py2-analysis.json" && \
		touch "$$MARKER_DIR/.zodbupdate-done"; \
	else \
		echo "[Step 1/3] Convert to Python 3: SKIPPED (already done)"; \
	fi
	@echo "[Step 2/3] fix_provides"
	parts/$(INSTANCE)/bin/interpreter $(MIGRATION)fix_provides.py "$(DATAFS)"
	@echo "[Step 3/3] Zope-level fixes"
	bin/$(INSTANCE) run $(MIGRATION)migrate_zodb.py
	@echo "=== Migration complete ==="
	@echo "Then reindex catalog from ZMI: portal_catalog -> Advanced -> Update Catalog"
