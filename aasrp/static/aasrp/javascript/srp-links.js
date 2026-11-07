/* global _bootstrapTooltip, _removeSearchFromColumnControl, aaSrpSettings, DataTable, moment, numberFormatter */

$(document).ready(() => {
    'use strict';

    const elementTableSrpLinks = $('#table_tab-srp-links');

    // DataTable column indices for easier reference
    const dtColumn = {
        linkName: 0,
        creator: 1,
        fleetTime: 2,
        fleetType: 3,
        doctrine: 4,
        aarLink: 5,
        srpCode: 6,
        srpCost: 7,
        status: 8,
        pendingRequests: 9,
        actions: 10
    };

    // Initialize DataTable options
    let dataTableOptions = {
        ...aaSrpSettings.dataTables,
        order: [[dtColumn.fleetTime, 'asc']],
        columnDefs: [
            // Remove column control search from these columns
            {
                targets: [
                    dtColumn.fleetTime,
                    dtColumn.srpCost
                ],
                columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1)
            },
            // Remove column control from these columns completely and make them non-orderable
            {
                targets: [
                    dtColumn.aarLink,
                    dtColumn.pendingRequests,
                    dtColumn.actions
                ],
                columnControl: [
                    {target: 0, content: []},
                    {target: 1, content: []}
                ]
            },
            // Make these columns non-orderable
            {
                targets: [
                    dtColumn.aarLink,
                    dtColumn.pendingRequests,
                    dtColumn.actions
                ],
                orderable: false
            },
            // Column definitions for specific columns
            {
                target: dtColumn.fleetTime,
                className: 'srp-link-fleet-time',
                render: (data) => moment(data).utc().format(aaSrpSettings.datetimeFormat)
            },
            {
                target: dtColumn.srpCost,
                className: 'srp-link-total-cost',
                render: (data) => numberFormatter({
                    value: data,
                    locales: aaSrpSettings.locale,
                    options: {
                        style: 'currency',
                        currency: 'ISK'
                    }
                }),
                type: 'num'
            },
            {
                target: dtColumn.pendingRequests,
                className: 'srp-link-pending-requests'
            },
            {
                target: dtColumn.actions,
                className: 'srp-link-actions text-end'
            }
        ],
        initComplete: () => {
            const dt = elementTableSrpLinks.DataTable();

            _bootstrapTooltip({selector: '#table_tab-srp-links'});

            dt.on('draw', () => {
                _bootstrapTooltip({selector: '#table_tab-srp-links'});
            });

            $('input[name="srp-requests-filter"]').on('change', () => dt.draw());
        }
    };

    if (aaSrpSettings.paging === false) {
        dataTableOptions = {
            ...dataTableOptions,
            pageLength: 99999,
            layout: { // See: https://datatables.net/reference/option/layout
                topStart: null,
                bottomEnd: null
            }
        };
    }

    // Initialize DataTable
    const dt = new DataTable(elementTableSrpLinks, dataTableOptions);
    dt.on('preXhr.dt', (e, settings, data) => {
        data['filter[has_requests]'] = $('#aasrp-srp-request-filter-pending').is(':checked');
    });

    /**
     * Modals
     */
    const modalEnableSrpLink = $('#enable-srp-link');
    const modalDisableSrpLink = $('#disable-srp-link');
    const modalDeleteSrpLink = $('#delete-srp-link');

    // Enable link modal
    modalEnableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalEnableSrpLink.find('#modal-button-confirm-enable-srp-link').attr('href', url);
        modalEnableSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.enableSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalEnableSrpLink.find('.modal-body').html('');
    });

    // Disable link modal
    modalDisableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDisableSrpLink.find('#modal-button-confirm-disable-srp-link').attr('href', url);
        modalDisableSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.disableSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalDisableSrpLink.find('.modal-body').html('');
    });

    // Delete link modal
    modalDeleteSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDeleteSrpLink.find('#modal-button-confirm-delete-srp-link').attr('href', url);
        modalDeleteSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.deleteSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalDeleteSrpLink.find('.modal-body').html('');
    });
});
