/* global aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride, objectDeepMerge, bootstrap */

/* jshint -W097 */
'use strict';

// Build the settings object
const aaSrpSettings = (typeof aaSrpJsSettingsOverride !== 'undefined') // eslint-disable-line no-unused-vars
    ? objectDeepMerge(aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride)  // jshint ignore:line
    : aaSrpJsSettingsDefaults;

/**
 * Bootstrap tooltip
 *
 * @param {string} [selector=body] Selector for the tooltip elements, defaults to 'body'
 *                                 to apply to all elements with the data-bs-tooltip attribute.
 *                                 Example: 'body', '.my-tooltip-class', '#my-tooltip-id'
 *                                 If you want to apply it to a specific element, use that element's selector.
 *                                 If you want to apply it to all elements with the data-bs-tooltip attribute,
 *                                 use 'body' or leave it empty.
 * @param {string} [namespace=aa-srp] Namespace for the tooltip
 * @returns {void}
 */
const aasrpBootstrapTooltip = ({selector = 'body', namespace = 'aa-srp'}) => { // eslint-disable-line no-unused-vars
    document.querySelectorAll(`${selector} [data-bs-tooltip="${namespace}"]`)
        .forEach((tooltipTriggerEl) => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
};
