/* global aaSrpSettings, bootstrap, moment */

$(document).ready(() => {
    'use strict';

    const elementTableUserSrpRequests = $('#table_tab-user-srp-requests');

    /**
     * Table: User's own SRP requests
     */
    let userSrpAmount = 0;

    const tableUserSrpRequests = elementTableUserSrpRequests.DataTable({
        language: aaSrpSettings.dataTable.language,
        ajax: {
            url: aaSrpSettings.url.userSrpRequests,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'request_time',
                /**
                 * Render callback
                 *
                 * @param data
                 * @returns {*}
                 */
                render: {
                    display: (data) => {
                        return data === null ? '' : moment(data).utc().format(
                            aaSrpSettings.datetimeFormat
                        );
                    },
                    sort: (data) => {
                        return data === null ? '' : data;
                    }
                },
                className: 'srp-request-time'
            },
            {
                data: 'character_html',
                render: {
                    display: 'display',
                    sort: 'sort'
                },
                className: 'srp-request-character'
            },
            {
                data: 'fleet_name',
                /**
                 * Render callback
                 */
                render: {
                    /**
                     * Display callback
                     *
                     * @param {string} data
                     * @param {string} type
                     * @param {object} row
                     * @returns {string}
                     */
                    display: (data, type, row) => {
                        console.log('Fleet name:', data);
                        console.log('Fleet name type:', type);
                        console.log('Fleet name row:', row);
                        const l10nSrpCode = aaSrpSettings.translation.dataTable.content.srpCode;
                        const l10nRequestCode = aaSrpSettings.translation.dataTable.content.requestCode;

                        return data === null ? '' :  `<p>${data}</p><p class="small text-muted">${l10nSrpCode}: ${row.srp_code}<br>${l10nRequestCode}: ${row.request_code}</p>`;
                    },
                    /**
                     * Filter callback
                     *
                     * @param {string} data
                     * @param {string} type
                     * @param {object} row
                     * @returns {string}
                     */
                    filter: (data, type, row) => {
                        return data === null ? '' :  `${data} ${row.srp_code} ${row.request_code}`;
                    },
                    /**
                     * Sort callback
                     *
                     * @param {string} data
                     * @returns {string}
                     */
                    sort: (data) => {
                        return data === null ? '' : data;
                    }
                },
                className: 'srp-request-fleet-details'
            },
            // {
            //     data: 'srp_code',
            //     className: 'srp-request-srp-code'
            // },
            // {
            //     data: 'request_code',
            //     className: 'srp-request-code'
            // },
            {
                data: 'ship_html',
                render: {
                    display: 'display',
                    sort: 'sort'
                },
                className: 'srp-request-ship'
            },
            // {data: 'zkb_link'},
            {
                data: 'zbk_loss_amount',
                /**
                 * Render callback
                 */
                render: {
                    /**
                     * Display callback
                     *
                     * @param {int|string} data
                     * @returns {string}
                     */
                    display: (data) => {
                        return data === null ? '' :  `${new Intl.NumberFormat(aaSrpSettings.locale).format(data)} ISK`;
                    },
                    /**
                     * Filter callback
                     *
                     * @param data
                     * @returns {int|string|*}
                     */
                    filter: (data) => {
                        return data === null ? '' : data;
                    },
                    /**
                     * Sort callback
                     *
                     * @param {int|string} data
                     * @returns {int|string|*}
                     */
                    sort: (data) => {
                        return data === null ? '' : data;
                    }
                },
                className: 'srp-request-zkb-loss-amount text-end'
            },
            {
                data: 'payout_amount',
                /**
                 * Render callback
                 */
                render: {
                    /**
                     * Display callback
                     *
                     * @param {int|string} data
                     * @returns {string}
                     */
                    display: (data) => {
                        return data === null ? '' :  `${new Intl.NumberFormat(aaSrpSettings.locale).format(data)} ISK`;
                    },
                    /**
                     * Filter callback
                     *
                     * @param data
                     * @returns {int|string|*}
                     */
                    filter: (data) => {
                        return data === null ? '' : data;
                    },
                    /**
                     * Sort callback
                     *
                     * @param {int|string} data
                     * @returns {int|string|*}
                     */
                    sort: (data) => {
                        return data === null ? '' : data;
                    }
                },
                className: 'srp-request-payout text-end'
            },
            {
                data: 'request_status_icon',
                className: 'srp-request-status text-end'
            },
            // Hidden columns
            {data: 'request_status'},
            {data: 'ship'},
            {data: 'character'}
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [6]
            },
            {
                visible: false,
                targets: [7, 8, 9]
            }
        ],
        order: [
            [0, 'desc']
        ],
        filterDropDown: {
            columns: [
                {
                    idx: 9,
                    title: aaSrpSettings.translation.filter.character
                },
                {
                    idx: 8,
                    title: aaSrpSettings.translation.filter.ship
                },
                {
                    idx: 7,
                    title: aaSrpSettings.translation.filter.requestStatus
                }
            ],
            autoSize: false,
            bootstrap: true,
            bootstrap_version: 5
        },
        /**
         * When ever a row is created …
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: (row, data, rowIndex) => {
            // Row id attr
            $(row).attr('data-row-id', rowIndex);
            $(row).attr('data-srp-request-code', data.request_code);

            userSrpAmount += parseInt(data.payout_amount);

            $('.srp-dashboard-user-isk-cost-amount').html(
                `${new Intl.NumberFormat(aaSrpSettings.locale).format(userSrpAmount)} ISK`
            );
        }
    });

    /**
     * When the DataTable has finished rendering and is fully initialized
     */
    tableUserSrpRequests.on('draw', () => {
        // Show bootstrap tooltips
        [].slice.call(
            document.querySelectorAll(
                '[data-bs-tooltip="aa-srp"]'
            )
        ).map((tooltipTriggerEl) => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });

    /**
     * Modals
     */
    const modalSrpRequestDetails = $('#srp-request-details');

    // Show details
    modalSrpRequestDetails.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $.get({
            url: url,
            success: (data) => {
                modalSrpRequestDetails.find('.modal-body').html(data);
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestDetails.find('.modal-body').text('');
    });
});
