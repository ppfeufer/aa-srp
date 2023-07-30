/* global aaSrpSettings, moment */

$(document).ready(() => {
    'use strict';

    /**
     * Table :: SRP Links
     */
    let totalSrpAmount = 0;

    $('#tab_aasrp_srp_links').DataTable({
        ajax: {
            url: aaSrpSettings.url.availableSrpLinks,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'srp_name',
                className: 'srp-link-fleet-name'
            },
            {
                data: 'creator',
                className: 'srp-link-creator'
            },
            {
                data: 'fleet_time',
                /**
                 * Render callback
                 *
                 * @param data
                 * @returns {*}
                 */
                render: (data) => {
                    return moment(data).utc().format(aaSrpSettings.datetimeFormat);
                },
                className: 'srp-link-fleet-time'
            },
            {
                data: 'fleet_type',
                className: 'srp-link-fleet-type'
            },
            // {
            //     data: 'fleet_commander',
            //     className: 'srp-link-fleet-commander'
            // },
            {
                data: 'fleet_doctrine',
                className: 'srp-link-fleet-doctrine'
            },
            {
                data: 'aar_link',
                className: 'srp-link-aar-link'
            },
            {
                data: 'srp_code',
                render: {
                    display: 'display',
                    _: 'sort'
                },
                className: 'srp-link-code'
            },
            {
                data: 'srp_costs',
                /**
                 * Render callback
                 *
                 * @param data
                 * @param type
                 * @returns {string|*}
                 */
                render: (data, type) => {
                    if (type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    } else {
                        return data;
                    }
                },
                className: 'srp-link-total-cost text-right'
            },
            {
                data: 'srp_status',
                className: 'srp-link-status'
            },
            {
                data: 'pending_requests',
                className: 'srp-link-pending-requests'
            },
            {
                data: 'actions',
                className: 'srp-link-actions'
            }
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [10]
            },
            {
                width: 115,
                targets: [10]
            }
        ],
        order: [[2, 'asc']],
        paging: aaSrpSettings.dataTable.paging,
        /**
         * When ever a row is created ...
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: (row, data, rowIndex) => {
            // Row id attr
            $(row)
                .attr('data-row-id', rowIndex)
                .attr('data-srp-code', data.srp_code.sort);

            totalSrpAmount += parseInt(data.srp_costs);

            $('.srp-dashboard-total-isk-cost-amount').html(
                totalSrpAmount.toLocaleString() + ' ISK'
            );
        }
    });

    /**
     * Table :: User's own SRP requests
     */
    let userSrpAmount = 0;

    $('#tab_aasrp_user_srp_requests').DataTable({
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
                render: (data) => {
                    return moment(data).utc().format(aaSrpSettings.datetimeFormat);
                },
                className: 'srp-request-time'
            },
            {
                data: 'character_html',
                render: {
                    display: 'display',
                    _: 'sort'
                },
                className: 'srp-request-character'
            },
            {
                data: 'fleet_name',
                className: 'srp-request-fleet-name'
            },
            {
                data: 'srp_code',
                className: 'srp-request-srp-code'
            },
            {
                data: 'request_code',
                className: 'srp-request-code'
            },
            {
                data: 'ship_html',
                render: {
                    display: 'display',
                    _: 'sort'
                },
                className: 'srp-request-ship'
            },
            // {data: 'zkb_link'},
            {
                data: 'zbk_loss_amount',
                /**
                 * Render callback
                 *
                 * @param data
                 * @param type
                 * @returns {string|*}
                 */
                render: (data, type) => {
                    if (type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    } else {
                        return data;
                    }
                },
                className: 'srp-request-zkb-loss-amount text-right'
            },
            {
                data: 'payout_amount',
                /**
                 * Render callback
                 *
                 * @param data
                 * @param type
                 * @returns {string|*}
                 */
                render: (data, type) => {
                    if (type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    } else {
                        return data;
                    }
                },
                className: 'srp-request-payout text-right'
            },
            {
                data: 'request_status_icon',
                className: 'srp-request-status text-center'
            },
            // Hidden columns
            {data: 'request_status'},
            {data: 'ship'},
            {data: 'character'}
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [8]
            },
            {
                visible: false,
                targets: [9, 10, 11]
            }
        ],
        order: [
            [0, 'desc']
        ],
        filterDropDown: {
            columns: [
                {
                    idx: 11,
                    title: aaSrpSettings.translation.filter.character
                },
                {
                    idx: 10,
                    title: aaSrpSettings.translation.filter.ship
                },
                {
                    idx: 9,
                    title: aaSrpSettings.translation.filter.requestStatus
                }
            ],
            autoSize: false,
            bootstrap: true
        },
        /**
         * When ever a row is created ...
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
                userSrpAmount.toLocaleString() + ' ISK'
            );
        }
    });

    /*
     * Modals
     */
    const modalEnableSrpLink = $('#enable-srp-link');
    const modalDisableSrpLink = $('#disable-srp-link');
    const modalDeleteSrpLink = $('#delete-srp-link');
    const modalSrpRequestDetails = $('#srp-request-details');

    // Enable link modal
    modalEnableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalEnableSrpLink.find('#modal-button-confirm-enable-srp-link')
            .attr('href', url);
        modalEnableSrpLink.find('.modal-body').html(
            aaSrpSettings.translation.modal.enableSrpLink.body + '<br>"' + name + '"'
        );
    }).on('hide.bs.modal', () => {
        modalEnableSrpLink.find('.modal-body').html('');
    });

    // Disable link modal
    modalDisableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDisableSrpLink.find('#modal-button-confirm-disable-srp-link')
            .attr('href', url);
        modalDisableSrpLink.find('.modal-body').html(
            aaSrpSettings.translation.modal.disableSrpLink.body + '<br>"' + name + '"'
        );
    }).on('hide.bs.modal', () => {
        modalDisableSrpLink.find('.modal-body').html('');
    });

    // Delete link modal
    modalDeleteSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDeleteSrpLink.find('#modal-button-confirm-delete-srp-link')
            .attr('href', url);
        modalDeleteSrpLink.find('.modal-body').html(
            aaSrpSettings.translation.modal.deleteSrpLink.body + '<br>"' + name + '"'
        );
    }).on('hide.bs.modal', () => {
        modalDeleteSrpLink.find('.modal-body').html('');
    });

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
