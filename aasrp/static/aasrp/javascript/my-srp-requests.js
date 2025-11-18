/* global _bootstrapTooltip, aaSrpSettings, fetchGet, moment, numberFormatter, _removeSearchFromColumnControl, DataTable */

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
                const dt = new DataTable(elementTableUserSrpRequests, { // eslint-disable-line no-unused-vars
                    language: aaSrpSettings.dataTables.language,
                    data: data,
                    layout: aaSrpSettings.dataTables.layout,
                    ordering: aaSrpSettings.dataTables.ordering,
                    columnControl: aaSrpSettings.dataTables.columnControl,
                    columns: [
                        {
                            data: {
                                display: (data) => data.request_time === null ? '' : moment(data.request_time).utc().format(
                                    aaSrpSettings.datetimeFormat
                                ),
                                filter: (data) => data.request_time,
                                sort: (data) => data.request_time
                            },
                            className: 'srp-request-time'
                        },
                        {
                            data: {
                                display: (data) => data.character_html.display,
                                filter: (data) => data.character_html.sort,
                                sort: (data) => data.character_html.sort
                            },
                            className: 'srp-request-character'
                        },
                        {
                            data: {
                                display: (data) => data.fleet_name_html.display,
                                filter: (data) => data.fleet_name_html.sort,
                                sort: (data) => data.fleet_name_html.sort
                            },
                            className: 'srp-request-fleet-details'
                        },
                        {
                            data: {
                                display: (data) => data.ship_html.display,
                                filter: (data) => data.ship_html.sort,
                                sort: (data) => data.ship_html.sort
                            },
                            className: 'srp-request-ship'
                        },
                        {
                            data: {
                                display: (data) => numberFormatter({
                                    value: data.zkb_loss_amount,
                                    locales: aaSrpSettings.locale,
                                    options: {
                                        style: 'currency',
                                        currency: 'ISK'
                                    }
                                }),
                                filter: (data) => data.zkb_loss_amount,
                                sort: (data) => data.zkb_loss_amount
                            },
                            className: 'srp-request-zkb-loss-amount text-end'
                        },
                        {
                            data: {
                                display: (data) => numberFormatter({
                                    value: data.payout_amount,
                                    locales: aaSrpSettings.locale,
                                    options: {
                                        style: 'currency',
                                        currency: 'ISK'
                                    }
                                }),
                                filter: (data) => data.payout_amount,
                                sort: (data) => data.payout_amount
                            },
                            className: 'srp-request-payout text-end'
                        },
                        {
                            data: 'request_status_icon',
                            className: 'srp-request-status text-end'
                        },
                    ],
                    columnDefs: [
                        {
                            target: 0,
                            columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1)
                        },
                        {
                            targets: [4, 5, 6],
                            orderable: false,
                            columnControl: [
                                {target: 0, content: []},
                                {target: 1, content: []}
                            ]
                        },
                        {
                            target: 6,
                            width: 90
                        }
                    ],
                    order: [
                        [0, 'desc']
                    ],
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
                        const dt = elementTableUserSrpRequests.DataTable();

                        // Show bootstrap tooltips
                        _bootstrapTooltip({selector: '#table_tab-user-srp-requests'});

                        dt.on('draw', () => {
                            _bootstrapTooltip({selector: '#table_tab-user-srp-requests'});
                        });
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
