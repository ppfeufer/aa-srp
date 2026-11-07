/* global aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride, bootstrap, ClipboardJS, objectDeepMerge */

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
 * Helper function: Copy text to the clipboard
 *
 * Must be called synchronously from a user click, so browsers allow it.
 * Falls back to ClipboardJS on non-secure (non-HTTPS) origins.
 *
 * @param {string} text The text to copy
 * @returns {Promise<boolean>} Whether copying succeeded
 * @private
 */
const _copyToClipboard = (text) => { // eslint-disable-line no-unused-vars
    if (window.isSecureContext && navigator.clipboard) {
        return navigator.clipboard.writeText(text)
            .then(() => true)
            .catch(() => false);
    }

    try {
        ClipboardJS.copy(text);

        return Promise.resolve(true);
    } catch (error) {
        console.error('Error copying to clipboard:', error);

        return Promise.resolve(false);
    }
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

/**
 * Helper function: Show a short-lived toast message, without reloading the page
 *
 * @param {string} message The message to show
 * @param {boolean} success Whether this is a success or an error message
 * @private
 */
const _showToast = (message, success) => { // eslint-disable-line no-unused-vars
    let container = $('#aasrp-toast-container');

    if (container.length === 0) {
        container = $('<div id="aasrp-toast-container" class="toast-container position-fixed bottom-0 end-0 p-3"></div>');

        $('body').append(container);
    }

    const toastElement = $('<div class="toast align-items-center border-0" role="status" aria-live="polite" aria-atomic="true"><div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div></div>');

    toastElement
        .addClass(success ? 'text-bg-success' : 'text-bg-danger')
        .find('.toast-body')
        .text(message);

    container.append(toastElement);

    toastElement.on('hidden.bs.toast', () => {
        toastElement.remove();
    });

    new bootstrap.Toast(toastElement[0], {delay: 6000}).show();
};
