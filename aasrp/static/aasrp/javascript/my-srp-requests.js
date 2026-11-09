/* global _bootstrapTooltip, _formatCurrency, _removeSearchFromColumnControl, aaSrpSettings, DataTable, fetchGet, moment */

$(document).ready(() => {
    'use strict';

    const element = {
        tableUserSrpRequests: $('#table_tab-user-srp-requests'),
        totalSrpCost: $('#srp-dashboard-user-isk-cost-amount')
    };
    const custom_dt_filter = {
        request_status: $('#filter-request-status'),
        ship: $('#filter-ship'),
        character: $('#filter-character')
    };

    // Display total SRP cost to user
    const userSrpAmount = element.totalSrpCost.data('total-srp-cost') || 0;
    element.totalSrpCost.html(_formatCurrency(userSrpAmount));

    // DataTable column indices for easier reference
    const dtColumn = {
        requestTime: 0,
        character: 1,
        requestDetails: 2,
        ship: 3,
        iskLoss: 4,
        srpPayout: 5,
        status: 6,
        srpCode: 7, // Invisible: SRP Code (for internal use, not displayed to users)
        requestCode: 8, // Invisible: Request Code (for internal use, not displayed to users)
        requestStatus: 9, // Invisible: Request Status (for internal use, not displayed to users)
        killboardLink: 10 // Invisible: Killboard Link (for internal use, not displayed to users)
    };

    // Initialize DataTable with server-side processing
    const dt = new DataTable(element.tableUserSrpRequests, {
        ...aaSrpSettings.dataTables,
        order: [[0, 'desc']], // Default sorting by request time (newest first)
        serverSide: true, // Enable server-side processing
        ajax: {
            url: aaSrpSettings.url.userSrpRequests,
            data: (data) => {
                const mappedFilters = Object.fromEntries(
                    Object.entries(custom_dt_filter).map(([key, $el]) => [`dropdown_filter[${key}]`, $el.val()])
                );

                return {...data, ...mappedFilters};
            },
            error: (xhr, error) => console.error('Error fetching data:', xhr, error)
        },
        columnDefs: [
            // Request time
            {
                target: dtColumn.requestTime,
                render: (data) => moment(data).utc().format(aaSrpSettings.datetimeFormat),
                className: 'srp-request-time',
                columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1)
            },
            // Character
            {
                target: dtColumn.character,
                className: 'srp-request-character'
            },
            // Request details
            {
                target: dtColumn.requestDetails,
                className: 'srp-request-fleet-details'
            },
            // Ship
            {
                target: dtColumn.ship,
                className: 'srp-request-ship'
            },
            // ISK lost
            {
                target: dtColumn.iskLoss,
                render: (data) => _formatCurrency(data),
                className: 'srp-request-zkb-loss-amount',
                columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1),
                type: 'num'
            },
            // SRP payout
            {
                target: dtColumn.srpPayout,
                render: (data) => _formatCurrency(data),
                className: 'srp-request-payout',
                columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1),
                type: 'num'
            },
            // Status
            {
                target: dtColumn.status,
                render: (data) => data,
                className: 'srp-request-status text-end',
                orderable: false,
                columnControl: [
                    {target: 0, content: []},
                    {target: 1, content: []}
                ],
                width: '90'
            },
            // Invisible: SRP Code (for internal use, not displayed to users)
            {
                target: dtColumn.srpCode,
                visible: false
            },
            // Invisible: Request Code (for internal use, not displayed to users)
            {
                target: dtColumn.requestCode,
                visible: false
            },
            // Invisible: Request Status (for internal use, not displayed to users)
            {
                target: dtColumn.requestStatus,
                visible: false
            },
            // Invisible: Killboard Link (for internal use, not displayed to users)
            {
                target: dtColumn.killboardLink,
                visible: false
            }
        ],
        initComplete: () => {
            // Redraw table when filter values change
            Object.values(custom_dt_filter).forEach(($el) => {
                $el.on('change', () => dt.draw());
            });

            // Show bootstrap tooltips
            _bootstrapTooltip({selector: '#table_tab-user-srp-requests'});

            dt.on('draw', () => {
                _bootstrapTooltip({selector: '#table_tab-user-srp-requests'});
            });
        }
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
