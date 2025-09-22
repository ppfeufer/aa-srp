/* global aasrpBootstrapTooltip, aaSrpSettings, fetchGet, moment, numberFormatter */

$(document).ready(() => {
    'use strict';

    const elementTableUserSrpRequests = $('#table_tab-user-srp-requests');

    /**
     * Table: User's own SRP requests
     */
    let userSrpAmount = 0;

    fetchGet({url: aaSrpSettings.url.userSrpRequests})
        .then((data) => {
            if (data) {
                elementTableUserSrpRequests.DataTable({
                    language: aaSrpSettings.dataTable.language,
                    data: data,
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
                                filter: 'sort',
                                sort: 'sort'
                            },
                            className: 'srp-request-character'
                        },
                        {
                            data: 'fleet_name_html',
                            /**
                             * Render callback
                             */
                            render: {
                                display: 'display',
                                filter: 'sort',
                                sort: 'sort'
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
                                filter: 'sort',
                                sort: 'sort'
                            },
                            className: 'srp-request-ship'
                        },
                        // {data: 'zkb_link'},
                        {
                            data: 'zkb_loss_amount',
                            /**
                             * Render callback
                             */
                            render: {
                                display: (data) => {
                                    return numberFormatter({
                                        value: data,
                                        locales: aaSrpSettings.locale,
                                        options: {
                                            style: 'currency',
                                            currency: 'ISK'
                                        }
                                    });
                                },
                                filter: (data) => {
                                    return data;
                                },
                                sort: (data) => {
                                    return data;
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
                                display: (data) => {
                                    return numberFormatter({
                                        value: data,
                                        locales: aaSrpSettings.locale,
                                        options: {
                                            style: 'currency',
                                            currency: 'ISK'
                                        }
                                    });
                                },
                                filter: (data) => {
                                    return data;
                                },
                                sort: (data) => {
                                    return data;
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
                            numberFormatter({
                                value: userSrpAmount,
                                locales: aaSrpSettings.locale,
                                options: {
                                    style: 'currency',
                                    currency: 'ISK'
                                }
                            })
                        );
                    },
                    initComplete: () => {
                        // Show bootstrap tooltips
                        aasrpBootstrapTooltip({selector: '#table_tab-user-srp-requests'});
                    }
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching SRP request data:', error);
        });

    /**
     * Modals
     */
    const modalSrpRequestDetails = $('#srp-request-details');

    // Show details
    modalSrpRequestDetails.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        fetchGet({url: url, responseIsJson: false})
            .then((data) => {
                modalSrpRequestDetails.find('.modal-body').html(data);
            })
            .catch((error) => {
                console.log(`Error: ${error.message}`);
            });
    }).on('hide.bs.modal', () => {
        modalSrpRequestDetails.find('.modal-body').text('');
    });
});
