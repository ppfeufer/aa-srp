/* global aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride, objectDeepMerge */

/* jshint -W097 */
'use strict';

// Build the settings object
let aaSrpSettings = aaSrpJsSettingsDefaults;

if (typeof aaSrpJsSettingsOverride !== 'undefined') {
    aaSrpSettings = objectDeepMerge( // eslint-disable-line no-unused-vars
        aaSrpJsSettingsDefaults,
        aaSrpJsSettingsOverride
    );
}
