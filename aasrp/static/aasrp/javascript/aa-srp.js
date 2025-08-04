/* global aaSrpJsSettingsDefaults, aaSrpJsSettingsOverride */

/* jshint -W097 */
'use strict';

/**
 * Checks if the given item is a plain object, excluding arrays and dates.
 *
 * @param {*} item - The item to check.
 * @returns {boolean} True if the item is a plain object, false otherwise.
 */
function isObject (item) {
    return (
        item && typeof item === 'object' && !Array.isArray(item) && !(item instanceof Date)
    );
}

/**
 * Recursively merges properties from source objects into a target object. If a property at the current level is an object,
 * and both target and source have it, the property is merged. Otherwise, the source property overwrites the target property.
 * This function does not modify the source objects and prevents prototype pollution by not allowing __proto__, constructor,
 * and prototype property names.
 *
 * @param {Object} target - The target object to merge properties into.
 * @param {...Object} sources - One or more source objects from which to merge properties.
 * @returns {Object} The target object after merging properties from sources.
 */
function deepMerge (target, ...sources) {
    if (!sources.length) {
        return target;
    }

    // Iterate through each source object without modifying the `sources` array.
    sources.forEach(source => {
        if (isObject(target) && isObject(source)) {
            for (const key in source) {
                if (isObject(source[key])) {
                    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
                        continue; // Skip potentially dangerous keys to prevent prototype pollution.
                    }

                    if (!target[key] || !isObject(target[key])) {
                        target[key] = {};
                    }

                    deepMerge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
        }
    });

    return target;
}

// Build the settings object
let aaSrpSettings = aaSrpJsSettingsDefaults;
if (typeof aaSrpJsSettingsOverride !== 'undefined') {
    aaSrpSettings = deepMerge( // eslint-disable-line no-unused-vars
        aaSrpJsSettingsDefaults,
        aaSrpJsSettingsOverride
    );
}

/**
 * Fetch data from an ajax URL
 *
 * @param {string} url The URL to fetch data from
 * @param {string} method The HTTP method to use for the request (default: 'get')
 * @param {string|null} csrfToken The CSRF token to include in the request headers (default: null)
 * @param {string|null} payload The payload (JSON) to send with the request (default: null)
 * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
 * @returns {Promise<any>} The fetched data
 */
const _fetchAjaxData = async ({
    url,
    method = 'get',
    csrfToken = null,
    payload = null,
    responseIsJson = true
}) => {
    const normalizedMethod = method.toLowerCase();

    // Validate the method
    if (!['get', 'post'].includes(normalizedMethod)) {
        throw new Error(`Invalid method: ${method}. Valid methods are: get, post`);
    }

    const headers = {};

    // Set headers based on response type
    if (responseIsJson) {
        headers['Accept'] = 'application/json'; // jshint ignore:line
        headers['Content-Type'] = 'application/json';
    }

    let requestUrl = url;
    let body = null;

    if (normalizedMethod === 'post') {
        if (!csrfToken) {
            throw new Error('CSRF token is required for POST requests');
        }

        headers['X-CSRFToken'] = csrfToken;

        if (payload !== null && !isObject(payload)) {
            throw new Error('Payload must be an object when using POST method');
        }

        body = payload ? JSON.stringify(payload) : null;
    } else if (normalizedMethod === 'get' && payload) {
        const queryParams = new URLSearchParams(payload).toString(); // jshint ignore:line

        requestUrl += (url.includes('?') ? '&' : '?') + queryParams;
    }

    try {
        const response = await fetch(requestUrl, {
            method: method.toUpperCase(),
            headers: headers,
            body: body
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return responseIsJson ? await response.json() : await response.text();
    } catch (error) {
        console.log(`Error: ${error.message}`);

        throw error;
    }
};

/**
 * Fetch data from an ajax URL using the GET method.
 * This function is a wrapper around _fetchAjaxData to simplify GET requests.
 *
 * @param {string} url The URL to fetch data from
 * @param {string|null} payload The payload (JSON) to send with the request (default: null)
 * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
 */
const fetchGet = ({ // eslint-disable-line no-unused-vars
    url,
    payload = null,
    responseIsJson = true
}) => {
    return _fetchAjaxData({
        url: url,
        method: 'get',
        payload: payload,
        responseIsJson: responseIsJson
    });
};

/**
 * Fetch data from an ajax URL using the POST method.
 * This function is a wrapper around _fetchAjaxData to simplify POST requests.
 * It requires a CSRF token for security purposes.
 *
 * @param {string} url The URL to fetch data from
 * @param {string|null} csrfToken The CSRF token to include in the request headers (default: null)
 * @param {string|null} payload The payload (JSON) to send with the request (default: null)
 * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
 */
const fetchPost = ({ // eslint-disable-line no-unused-vars
    url,
    csrfToken,
    payload = null,
    responseIsJson = true
}) => {
    return _fetchAjaxData({
        url: url,
        method: 'post',
        csrfToken: csrfToken,
        payload: payload,
        responseIsJson: responseIsJson
    });
};
