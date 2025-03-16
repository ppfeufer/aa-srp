const globals = require('globals');
const js = require('@eslint/js');

/** @type {import('eslint').Linter.FlatConfig[]} */

module.exports = [
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.commonjs,
                ...globals.jquery,
            },
            parserOptions: {
                ...js.configs.recommended.parserOptions,
                ecmaVersion: 'latest',
                ecmaFeatures: {
                    impliedStrict: true,
                },
                sourceType: 'module',
            },
        },
        rules: {
            ...js.configs.recommended.rules,
            indent: ['error', 4],
            quotes: ['error', 'single', {
                avoidEscape: true,
                allowTemplateLiterals: true
            }],
            semi: [2, 'always'],
        },
    }
];
