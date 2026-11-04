/* global aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride, objectDeepMerge, bootstrap */

/* jshint -W097 */
'use strict';

// Build the settings object
const aaSrpSettings = (typeof aaSrpJsSettingsOverride !== 'undefined') // eslint-disable-line no-unused-vars
    ? objectDeepMerge(aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride) // jshint ignore:line
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
const _bootstrapTooltip = ({selector = 'body', namespace = 'aa-srp'}) => { // eslint-disable-line no-unused-vars
    document.querySelectorAll(`${selector} [data-bs-tooltip="${namespace}"]`)
        .forEach((tooltipTriggerEl) => {
            // Dispose existing tooltip instance if it exists
            const existing = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (existing) {
                existing.dispose();
            }

            // Remove any leftover tooltip elements
            $('.bs-tooltip-auto').remove();

            // Create new tooltip instance
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
};

/**
 * Remove search from column control.
 *
 * @param {Array} columnControl Column control.
 * @param {int} index Index of the column to remove search from.
 * @return {Array} Modified column control.
 * @private
 */
const _removeSearchFromColumnControl = (columnControl, index = 1) => { // eslint-disable-line no-unused-vars
    const cc = JSON.parse(JSON.stringify(columnControl));

    if (cc[index]) {
        cc[index].content = [];
    }

    return cc;
};

/**
 * Filter DataTable
 *
 * @param {Object} dt The DataTable instance.
 * @param {string} selector The selector for the filter button.
 * @param {callback} predicate The predicate function to filter rows.
 * @private
 */
const _filterDataTable = (dt, selector, predicate) => { // eslint-disable-line no-unused-vars
    $(selector).click(() => {
        // Clear any existing custom filters before applying a new one
        $.fn.dataTable.ext.search = [];

        /**
         * Custom filter function.
         *
         * @param {Object} settings DataTable settings object.
         * @param {Array} searchData Search data for the row.
         * @param {int} index Row index.
         * @param {Object} rowData Row data object.
         * @return {boolean} True if the row matches the filter, false otherwise.
         */
        const filter = (settings, searchData, index, rowData) => {
            if (!rowData) {
                return true;
            }

            return predicate(rowData);
        };

        $.fn.dataTable.ext.search.push(filter);

        dt.draw();
    });
};
