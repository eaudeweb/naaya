#!/bin/bash
# Post-buildout ZCML for the Naaya instances; run it from the buildout directory after each buildout.
# Own file, so 999-additional-overrides.zcml from zcml-additional is kept.
for pkg_dir in parts/*/etc/package-includes; do
    if [ -d "$pkg_dir" ]; then
        # Older versions of this script wrote the adapter into 999-additional-overrides.zcml
        if grep -qs "plone.protect.autocsrf" "$pkg_dir/999-additional-overrides.zcml"; then
            rm "$pkg_dir/999-additional-overrides.zcml"
        fi
        cat > "$pkg_dir/998-naaya-overrides.zcml" << 'ZCML'
<configure xmlns="http://namespaces.zope.org/zope">

<!-- Disable plone.protect CSRF auto-protection (not needed for Naaya) -->
<adapter
    factory="Products.NaayaCore.nocsrf.NoOpTransform"
    name="plone.protect.autocsrf"
    />

</configure>
ZCML
        echo "Added Naaya ZCML to $pkg_dir"
    fi
done
