#!/bin/bash
# Post-buildout ZCML for the Naaya instances; run it from the buildout directory after each buildout.
# pas.plugins.ldap pulls in Products.CMFPlone, whose ZCML is excluded; loaded before five:loadProducts.
for pkg_dir in parts/*/etc/package-includes; do
    if [ -d "$pkg_dir" ]; then
        cat > "$pkg_dir/016.5-pas.plugins.ldap-configure.zcml" << 'ZCML'
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:zcml="http://namespaces.zope.org/zcml">
  <configure zcml:condition="installed Products.CMFPlone">
    <exclude package="Products.CMFPlone" />
  </configure>
  <configure zcml:condition="installed pas.plugins.ldap">
    <include package="pas.plugins.ldap" />
  </configure>
</configure>
ZCML
        cat > "$pkg_dir/999-additional-overrides.zcml" << 'ZCML'
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:browser="http://namespaces.zope.org/browser"
           xmlns:zcml="http://namespaces.zope.org/zcml">

<!-- Disable plone.protect CSRF auto-protection (not needed for Naaya) -->
<adapter
    factory="Products.NaayaCore.nocsrf.NoOpTransform"
    name="plone.protect.autocsrf"
    />

<!-- yafowil.plone JS/CSS for the pas.plugins.ldap manage page, without CMFPlone -->
<configure zcml:condition="installed naaya.groupware">
  <browser:page
      for="*"
      name="yafowil.plone.js"
      class="naaya.groupware.yafowil_resources.YafowilJS"
      permission="zope2.View"
      />
  <browser:page
      for="*"
      name="yafowil.plone.css"
      class="naaya.groupware.yafowil_resources.YafowilCSS"
      permission="zope2.View"
      />
</configure>

</configure>
ZCML
        echo "Added Naaya ZCML to $pkg_dir"
    fi
done
