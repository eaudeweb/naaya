#!/bin/bash
# Post-buildout ZCML for the Naaya instances; run it from the buildout directory after each buildout.
for pkg_dir in parts/*/etc/package-includes; do
    if [ -d "$pkg_dir" ]; then
        cat > "$pkg_dir/999-additional-overrides.zcml" << 'ZCML'
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
